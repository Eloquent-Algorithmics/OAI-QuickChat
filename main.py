"""
This script uses the OpenAI API and ElevenLab's REST API
"""
import sys
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import stream
from elevenlabs.client import ElevenLabs, Voice, VoiceSettings
from rich.console import Console
from rich.text import Text
from config import (
    OPENAI_API_KEY,
    OPENAI_ORG_ID,
    OPENAI_PROJECT_ID,
    OPENAI_MODEL,
    OPENAI_SYSTEM_PROMPT,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)

console = Console()

oai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORG_ID,
    project=OPENAI_PROJECT_ID,
)
e_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
voice_ident = ELEVENLABS_VOICE_ID


def generate_and_play_response(user_input, conversation_history):
    """
    Generates response using the OpenAI API and
    plays it using the ElevenLabs TTS API.

    Args:
        user_input (str): The user's input.
        conversation_history (list): The conversation history as a list of
        dictionaries, where each dictionary represents a message with 'role'
        (either 'user' or 'assistant') and 'content' (the message content).

    Returns:
        None
    """
    conversation_history.append({"role": "user", "content": user_input})

    completion = oai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=conversation_history,
        temperature=0.5,
        top_p=0.95,
        max_tokens=128,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stream=True,
    )

    response_text = ""
    for chunk in list(completion):
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    conversation_history.append(
        {"role": "assistant", "content": response_text.strip()}
    )

    assistant_text = Text("🤖  ", style="green")
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
    """
    Recognizes speech from the microphone input.

    Args:
        timeout (int): The maximum number of seconds to wait for speech input.

    Returns:
        str or None: The recognized speech as a string,
        or None if no speech was detected or an error occurred.
    """
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


def main(use_voice=False):
    """
    Main function for running the QuickChat application.

    Parameters:
    - use_voice (bool): Flag indicating whether to use voice input.

    Returns:
    - None
    """
    conversation_history = [
        {"role": "system", "content": OPENAI_SYSTEM_PROMPT}
    ]

    while True:
        if use_voice:
            user_input = recognize_speech()
            if user_input is None:
                continue
        else:
            user_input = input("\nHow can I help you? ")

        generate_and_play_response(user_input, conversation_history)


if __name__ == "__main__":
    try:
        use_voice_input = "--voice" in sys.argv
        main(use_voice_input)
    except KeyboardInterrupt:
        console.print("\n\nGoodbye for now ...\n")
