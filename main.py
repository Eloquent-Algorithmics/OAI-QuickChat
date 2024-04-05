
import time
import sys
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import stream
from elevenlabs.client import ElevenLabs, Voice, VoiceSettings
from rich.console import Console
from rich.text import Text
from config import (
    OPENAI_API_KEY,
    OPENAI_SYSTEM_PROMPT,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)

console = Console()

oai_client = OpenAI(api_key=OPENAI_API_KEY)
e_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
voice_ident = ELEVENLABS_VOICE_ID


def generate_and_play_response(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})

    completion = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # gpt-3.5-turbo gpt-4-turbo-preview
        messages=conversation_history,
        temperature=0,
        max_tokens=64,
        stream=True,
    )

    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    conversation_history.append({"role": "assistant", "content": response_text.strip()})

    assistant_text = Text("Assistant: ", style="green")
    assistant_text.append(response_text.strip())
    console.print(assistant_text)

    def text_stream():
        yield response_text

    audio_stream = e_client.generate(
        text=text_stream(),
        voice=Voice(
            voice_id=ELEVENLABS_VOICE_ID,
            settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.0,
                style=0.0,
                use_speaker_boost=True,
                optimize_streaming_latency=4,
            ),
        ),
        model="eleven_turbo_v2",
        stream=True,
    )

    stream(audio_stream)


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


def main(use_voice_input=False):
    conversation_history = [
        {"role": "system", "content": OPENAI_SYSTEM_PROMPT}
    ]

    while True:
        if use_voice_input:
            user_input = recognize_speech()
            if user_input is None:
                continue
        else:
            user_input = input("How can I help you? ")

        start_time = time.time()

        generate_and_play_response(user_input, conversation_history)

        end_time = time.time()
        execution_time = end_time - start_time
        console.print(f"Execution time: {execution_time} seconds")


if __name__ == "__main__":
    try:
        use_voice_input = "--voice" in sys.argv
        main(use_voice_input)
    except KeyboardInterrupt:
        console.print("\nGoodbye for now ...\n")
