import os
import sys
import asyncio
import speech_recognition as sr
from openai import AsyncOpenAI
from rich.console import Console
from rich.text import Text
import websockets
import json
import base64
import shutil
import subprocess
import time
import signal

console = Console()

aclient = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
voice_id = os.environ.get("ELEVENLABS_VOICE_ID")


def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "


async def stream(audio_stream):
    """Stream audio data using mpv player."""
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()


async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"

    async with websockets.connect(uri) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                    "xi_api_key": ELEVENLABS_API_KEY,
                }
            )
        )

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get("isFinal"):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))

        async for text in text_chunker(text_iterator):
            await websocket.send(
                json.dumps({"text": text, "try_trigger_generation": True})
            )

        await websocket.send(json.dumps({"text": ""}))

        await listen_task


async def generate_and_play_response(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})

    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        temperature=0,
        max_tokens=64,
        stream=True,
    )

    content_list = []

    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                content_list.append(delta.content)
                yield delta.content

    await text_to_speech_input_streaming(voice_id, text_iterator())

    response_text = "".join(content_list)
    conversation_history.append({"role": "assistant", "content": response_text.strip()})

    assistant_text = Text(f"Assistant: ", style="green")
    assistant_text.append(response_text.strip())
    console.print(assistant_text)


def recognize_speech(timeout=20):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        console.print("Listening...\n")
        try:
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            console.print("Timeout reached, please try again.")
            return None

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        console.print("Could not understand audio")
        return None
    except sr.RequestError as e:
        console.print(f"Could not request results; {e}")
        return None


def signal_handler(sig, frame):
    console.print("\nGoodbye for now ...\n")
    sys.exit(0)


async def main(use_voice_input=False):
    conversation_history = [{"role": "system", "content": "You are an AI Assistant"}]

    while True:
        try:
            if use_voice_input:
                user_input = recognize_speech()
                if user_input is None:
                    continue
            else:
                user_input = input("How can I help you? ")

            start_time = time.time()

            await generate_and_play_response(user_input, conversation_history)

            end_time = time.time()
            execution_time = end_time - start_time
            console.print(f"Execution time: {execution_time} seconds")
        except KeyboardInterrupt:
            console.print("\nGoodbye for now ...\n")
            break


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    use_voice_input = "--voice" in sys.argv
    asyncio.run(main(use_voice_input))
