import multiprocessing
import aiofiles
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from core.prompt import generation_prompt_api, system_prompt
from core.pix2txt import pix2txt
from core.utils import chat_completions
from uuid import uuid4
import os
import logging
import uvicorn

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


def solution_generator(query: str):
    try:

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": generation_prompt_api.format(
                query=query)}
        ]
        for event in chat_completions(messages):

            if event.choices[0].delta.content:
                yield event.choices[0].delta.content

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An internal error occurred")





@app.post(
    "/api/v1/image_to_question",
    tags=["Extract question from the image"]
)
async def image2txt(file: UploadFile = File(...)):
    """
    Get a question extracted for the given image.

    - **file**: The image file to be processed.
    """
    try:
        if file.content_type.split("/")[0] != "image":
            raise HTTPException(
                status_code=400, detail="Uploaded file is not an image")

        file_extension = file.filename.split(".")[-1]
        file_location = f"images/questions/{uuid4()}.{file_extension}"
        async with aiofiles.open(file_location, "wb") as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"File saved to {file_location}")

        extracted_query = pix2txt(file_location)

        if not extracted_query:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")
        if file_location != None:
            os.remove(file_location)
            logger.info(f"File {file_location} deleted")
        return {"question": extracted_query.split("Question:")[1]}

    except Exception as e:
        logger.error(f"Error processing solution: {str(e)}")
        raise e


@app.post(
    "/api/v1/solution", tags=["Generate Solution"]
)
async def solution_for_question(query_text: str = Form(...)):
    """
    Get a streamed solution for the given question in text.
    - **query_text**: Question in text

    """
    try:
        if not query_text:
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")
        return StreamingResponse(
            solution_generator(query_text),
            media_type="text/event-stream",
        )

    except Exception as e:
        logger.error(f"Error processing solution: {str(e)}")
        return HTTPException(status_code=500, detail="An internal error occurred")


def run_server():
    cpu_count = multiprocessing.cpu_count()
    workers = max(1, int(cpu_count * 0.9))
    uvicorn.run("api:app", host="0.0.0.0", port=8000,reload=True)


if __name__ == "__main__":
    run_server()
