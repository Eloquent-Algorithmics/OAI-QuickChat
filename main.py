import os
import time
import sys
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import generate, stream
from rich.console import Console
from rich.text import Text

console = Console()

oai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

e_api_key = os.environ.get("ELEVENLABS_API_KEY")

voice_id = os.environ.get("ELEVENLABS_VOICE_ID")


def generate_and_play_response(user_input, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})

    completion = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # gpt-3.5-turbo gpt-4-turbo-preview
        messages=conversation_history,
        temperature=1,
        max_tokens=128,
        stream=True,
    )

    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    conversation_history.append({"role": "assistant", "content": response_text.strip()})

    assistant_text = Text(f"Assistant: ", style="green")
    assistant_text.append(response_text.strip())
    console.print(assistant_text)

    def text_stream():
        yield response_text

    audio_stream = generate(
        text=text_stream(),
        voice=voice_id,
        model="eleven_turbo_v2",
        stream=True,
        api_key=e_api_key,
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
    conversation_history = [{"role": "system", "content": "You are an AI Assistant"}]

    while True:
        if use_voice_input:
            user_input = recognize_speech()
            if user_input is None:
                continue
        else:
            user_input = input("How can I help you? ")

        generate_and_play_response(user_input, conversation_history)


if __name__ == "__main__":
    try:
        use_voice_input = "--voice" in sys.argv
        main(use_voice_input)
    except KeyboardInterrupt:
        console.print("\nGoodbye for now ...\n")
