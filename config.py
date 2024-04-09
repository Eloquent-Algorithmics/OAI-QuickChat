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

OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
if OPENAI_ORG_ID is None:
    raise ValueError("OPENAI_ORG_ID not set")

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
if OPENAI_MODEL is None:
    raise ValueError("OPENAI_MODEL not set")

OPENAI_SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT")
if OPENAI_SYSTEM_PROMPT is None:
    raise ValueError("OPENAI_SYSTEM_PROMPT not set")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if ELEVENLABS_API_KEY is None:
    raise ValueError("ELEVENLABS_API_KEY not set")

ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
if ELEVENLABS_VOICE_ID is None:
    raise ValueError("ELEVENLABS_VOICE_ID not set")
