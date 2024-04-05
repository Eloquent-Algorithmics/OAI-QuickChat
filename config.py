
# coding: utf-8
# Filename: config.py
# Path: /config.py

"""
This module loads environment variables from the .env file.

The .env file is not included in the repository for security reasons.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not set")

OPENAI_SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT")
if OPENAI_SYSTEM_PROMPT is None:
    raise ValueError("OPENAI_SYSTEM_PROMPT not set")

OPENAI_SYSTEM_PROMPT_WS = os.getenv("OPENAI_SYSTEM_PROMPT_WS")
if OPENAI_SYSTEM_PROMPT_WS is None:
    raise ValueError("OPENAI_SYSTEM_PROMPT_WS not set")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
if AZURE_OPENAI_ENDPOINT is None:
    raise ValueError("AZURE_OPENAI_ENDPOINT not set")

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
if AZURE_OPENAI_KEY is None:
    raise ValueError("AZURE_OPENAI_KEY not set")

AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
if AZURE_API_VERSION is None:
    raise ValueError("AZURE_API_VERSION not set")

AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
if AZURE_OPENAI_MODEL is None:
    raise ValueError("AZURE_OPENAI_MODEL not set")

TTS_PROVIDER = os.getenv("TTS_PROVIDER")
if TTS_PROVIDER is None:
    raise ValueError("TTS_PROVIDER not set")

PYTTSX4_VOICE_ID = os.getenv("PYTTSX4_VOICE_ID")
if PYTTSX4_VOICE_ID is None:
    raise ValueError("PYTTSX4_VOICE_ID not set")

PYTTSX4_RATE = int(os.getenv("PYTTSX4_RATE", str(150)))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if ELEVENLABS_API_KEY is None:
    raise ValueError("ELEVENLABS_API_KEY not set")

ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
if ELEVENLABS_VOICE_ID is None:
    raise ValueError("ELEVENLABS_VOICE_ID not set")
