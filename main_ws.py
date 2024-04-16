"""
This script uses the AzureOpenAI Service and ElevenLabs websockets
"""
import sys
import json
import base64
import shutil
import subprocess
import signal
import time
import asyncio
import azure.cognitiveservices.speech as speechsdk
from openai import AsyncAzureOpenAI
from rich.console import Console
from rich.text import Text
import websockets
from config_ws import (
    AZURE_SYSTEM_PROMPT,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_API_VERSION,
    AZURE_OPENAI_MODEL,
    AZURE_AI_SERVICES_KEY,
    AZURE_AI_SERVICES_REGION,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)

console = Console()

az_oai_client = AsyncAzureOpenAI(
    azure_endpoint=str(AZURE_OPENAI_ENDPOINT),
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_API_VERSION,
)

voice_id = ELEVENLABS_VOICE_ID


def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (
        ".", ",", "?", "!", ";", ":", "—", "-",
        "(", ")", "[", "]", "}", " "
    )
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


async def text_to_speech_input_streaming(text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_turbo_v2"

    async with websockets.connect(uri) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.8
                    },
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
    """
    Generates response using Azure OpenAI model and plays using TTS streaming.

    Args:
        user_input (str): The user's input.
        conversation_history (list):
            A list of dictionaries representing the conversation history.

    Returns:
        None
    """
    conversation_history.append({"role": "user", "content": user_input})

    response = await az_oai_client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=conversation_history,
        temperature=1,
        top_p=1,
        max_tokens=128,
        frequency_penalty=1,
        presence_penalty=0.5,
        stream=True,
    )

    content_list = []

    async def text_iterator():
        async for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                content = delta.content
                if content:
                    content_list.append(content)
                    yield content

    await text_to_speech_input_streaming(text_iterator())

    response_text = "".join(content_list)
    conversation_history.append(
        {"role": "assistant", "content": response_text.strip()}
    )

    assistant_text = Text("🤖  ", style="green")
    assistant_text.append(response_text.strip())
    console.print(assistant_text)


def recognize_speech():
    speech_key, service_region = AZURE_AI_SERVICES_KEY, AZURE_AI_SERVICES_REGION
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=service_region
    )

    # Creates a recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    recognized_text = None

    def handle_final_result(evt):
        nonlocal recognized_text
        recognized_text = evt.result.text

    speech_recognizer.recognized.connect(handle_final_result)

    console.print("I'm listening ... \n")
    try:
        speech_recognizer.start_continuous_recognition()
        while recognized_text is None:
            time.sleep(0.5)
        speech_recognizer.stop_continuous_recognition()
    except Exception as e:
        console.print(f"Error: {e}")
        return

    return recognized_text


async def main(use_voice=False):
    """
    Main entry point for the application.

    Args:
        use_voice (bool, optional): Whether to use voice input.
    """
    conversation_history = [
        {"role": "system", "content": AZURE_SYSTEM_PROMPT}
    ]

    while True:
        try:
            if use_voice:
                user_input = recognize_speech()
                if user_input is None:
                    continue
            else:
                user_input = input("\nHow can I help you? ")

            await generate_and_play_response(user_input, conversation_history)

        except KeyboardInterrupt:
            console.print("\n\nGoodbye for now ...\n")
            break


def signal_handler(_sig, _frame):
    """
    Handles the signal received by the program.

    Args:
        sig (int): The signal number.
        frame (frame): The current stack frame.

    Returns:
        None
    """
    console.print("\n\nGoodbye for now ...\n")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    use_voice_input = "--voice" in sys.argv
    asyncio.run(main(use_voice_input))
