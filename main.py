import os
import time
from openai import OpenAI
from elevenlabs import generate, stream

oai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

e_api_key = os.environ.get("ELEVENLABS_API_KEY")

voice_id = os.environ.get("ELEVENLABS_VOICE_ID")


def generate_and_play_response(user_input):
    
    start_time = time.time()
    completion = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",  # gpt-3.5-turbo gpt-4-turbo-preview
        messages=[
            {"role": "system", "content": "You are an AI Assistant"},
            {"role": "user", "content": user_input}
        ],
        temperature=1,
        max_tokens=128,
        stream=True,
    )

    response_text = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nResponse from OpenAI received in: {elapsed_time} seconds\n")


    def text_stream():
        yield response_text

    audio_stream = generate(
        text=text_stream(),
        voice=voice_id,
        model="eleven_turbo_v2",
        stream=True,
        api_key=e_api_key
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"ElevenLabs STT started in: {elapsed_time} seconds\n")
    stream(audio_stream)


def main():

    while True:
        user_input = input("How can I help you? ")
        start_time = time.time()
        generate_and_play_response(user_input)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total response time: {elapsed_time} seconds\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye for now ...\n")
