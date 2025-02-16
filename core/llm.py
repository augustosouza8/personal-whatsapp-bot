# core/llm.py
"""
LLM Integration Module using Groq API.

This module integrates with the Groq API to generate dynamic, human-like responses
based on the conversation context provided in the prompt.
"""

import re
import logging
from groq import Groq
from config import settings

# Initialize a logger for this module
logger = logging.getLogger(__name__)

def parse_prompt_to_messages(prompt: str) -> list:
    """
    Parse the prompt string into a list of message dictionaries that the Groq API can understand.

    Args:
        prompt (str): The full conversation prompt with context.

    Returns:
        list: A list of dictionaries, each containing "role" and "content" keys.
    """
    messages = []
    # Split the prompt into lines and process each line
    for line in prompt.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Identify the role based on a simple prefix convention.
        if line.startswith("User:"):
            messages.append({"role": "user", "content": line[len("User:"):].strip()})
        elif line.startswith("Bot:"):
            messages.append({"role": "assistant", "content": line[len("Bot:"):].strip()})
        else:
            # For lines without a clear role, treat them as system instructions.
            messages.append({"role": "system", "content": line})
    return messages

def get_llm_response(prompt: str) -> str:
    """
    Send a prompt to the Groq API and return the generated response.

    Args:
        prompt (str): The conversation prompt including context.

    Returns:
        str: The cleaned response text from the Groq API.

    Raises:
        Exception: If there is an error during the API call.
    """
    # Initialize the Groq client using the API key from our settings.
    client = Groq(api_key=settings.GROQ_API_KEY)
    # Convert the prompt into a structured list of messages.
    messages = parse_prompt_to_messages(prompt)
    # Determine the model to use; fall back to a default if not specified.
    model = getattr(settings, "DEFAULT_GROQ_MODEL", "deepseek-r1-distill-llama-70b")

    try:
        # Call the Groq API to generate a response.
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model
        )
        # Extract the content of the response.
        response = chat_completion.choices[0].message.content
        logger.info("Prompt sent to LLM:\n%s", prompt)
        logger.info("LLM raw response:\n%s", response)
        # Remove any extraneous metadata (like <think> tags) from the response.
        cleaned_response = re.sub(r'<think>.*?</think>\s*', '', response, flags=re.DOTALL).strip()
        logger.info("Cleaned LLM response:\n%s", cleaned_response)
        return cleaned_response
    except Exception as e:
        # Log the error and propagate the exception.
        logger.error("LLM API call failed", exc_info=True)
        raise e
