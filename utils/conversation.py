"""
This module contains utility functions for managing conversation history and summarizing it.
"""

import os
import json
from rich.console import Console
from openai import AzureOpenAI, APIConnectionError, RateLimitError, APIStatusError
from config_ws import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_API_VERSION,
    AZURE_SYSTEM_PROMPT,
    AZURE_OPENAI_MODEL,
)

client = AzureOpenAI(
    azure_endpoint=str(AZURE_OPENAI_ENDPOINT),
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_API_VERSION,
)
console = Console()


def load_conversation_history(file_path="conversation_history.json"):
    """
    This function loads conversation history from a JSON file.

    :param file_path: Defaults to "conversation_history.json".
    :return: A list of conversation messages.
    """
    with console.status("[bold green]Loading...", spinner="dots"):
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read().strip()
                    if file_content:
                        conversation_history = json.loads(file_content)
                    else:
                        raise ValueError("File is empty or contains invalid JSON.")
            else:
                conversation_history = [
                    {
                        "role": "system",
                        "content": AZURE_SYSTEM_PROMPT,
                    }
                ]
        except (IOError, ValueError) as error:
            console.print(f"[bold red]Error loading history: {error}")
            conversation_history = [
                {
                    "role": "system",
                    "content": AZURE_SYSTEM_PROMPT,
                }
            ]
    return conversation_history


def save_conversation_history(
    conversation_history, file_path="conversation_history.json"
):
    """
    Save the conversation history to a JSON file.

    Args:
        conversation_history (list): representing the conversation history.
        file_path (str, optional): JSON file where the conversation history.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f)
    except IOError as io_error:
        print(f"An error occurred saving conversation history: {io_error}")


def format_conversation_history_for_summary(conversation_history):
    """
    Format the conversation history for summary display.

    Args:
        conversation_history (str): The conversation history as a string.

    Returns:
        str: The formatted conversation history.
    """
    with console.status("[bold green]Formatting...", spinner="dots"):
        formatted_history = ""
        for message in conversation_history:
            role = message["role"].capitalize()
            content = message["content"]
            formatted_history += f"{role}: {content}\n"
    return formatted_history


def summarize_conversation_history_direct(conversation_history):
    """
    This function summarizes the conversation history provided as input.

    :param conversation_history: A list of conversation messages.
    :return: None
    """
    with console.status("[bold green]Summarizing..", spinner="dots"):
        try:
            formatted_history = format_conversation_history_for_summary(
                conversation_history
            )
            summary_prompt = (
                "Please summarize the following conversation history and "
                "retain all important information:\n\n"
                f"{formatted_history}\nSummary:"
            )
            messages = conversation_history + [
                {"role": "user", "content": summary_prompt}
            ]

            response = client.chat.completions.create(
                model=AZURE_OPENAI_MODEL,
                messages=messages,
                max_tokens=300,
                stop=None,
                temperature=0,
                top_p=0.5,
                frequency_penalty=0,
                presence_penalty=0,
            )

            summary_text = response.choices[0].message.content.strip()
            summarized_history = [{"role": "system", "content": AZURE_SYSTEM_PROMPT}]
            summarized_history.append({"role": "assistant", "content": summary_text})
        except APIConnectionError as e:
            console.print("[bold red]The server could not be reached")
            console.print(e.__cause__)
            summarized_history = [
                {
                    "role": "assistant",
                    "content": "Error: The server could not be reached.",
                }
            ]
        except RateLimitError as e:
            console.print(f"[bold red]A 429 status code was received.{e}")
            summarized_history = [
                {
                    "role": "assistant",
                    "content": "Error: Rate limit exceeded. Try again later.",
                }
            ]
        except APIStatusError as e:
            console.print("[bold red]non-200-range status code received")
            console.print(e.status_code)
            console.print(e.response)
            summarized_history = [
                {
                    "role": "assistant",
                    "content": f"Error: API error {e.status_code}.",
                }
            ]
    return summarized_history
