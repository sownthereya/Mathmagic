from openai import OpenAI
from core.prompt import generation_prompt_api
from core.prompt import system_prompt, generation_prompt_api
from fastapi import HTTPException
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = None

if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logger.critical("LLM API key error: %s", e)
else:
    logger.warning(
        "OPENAI API key not provided. Bedrock functionality will be disabled."
    )


def chat_completions(
    messages,
    stream=True,
    max_tokens=4096,
):

    if not client:
        raise HTTPException(
            status_code=500,
            detail="Openai client is not initialized. API key is missing.",
        )
    try:
        return client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            top_p=0.009,
            seed=1234,
            messages=messages,
            max_tokens=max_tokens,
            stream=stream,
        )
    except Exception as e:
        logger.error("Error generating chat completions: %s", e)
        raise HTTPException(
            status_code=500, detail="Error generating chat completions")
