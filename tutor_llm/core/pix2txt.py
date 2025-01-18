import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def pix2txt(image_path: str):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Please extract the information from the image exactly as shown. Express formulas and equations using only latex.Enclose the latex parts with $$ like $$a^2 + b^2 = c^2$$.If options are present, list each option on a new line. Your response should accurately reflect the content of the image.In the target section, identify what is being asked to find in the given problem.

          Output Format:

          Question: [Extracted Question]

          Options:
          [Extracted Option 1]
          [Extracted Option 2]
          [Extracted Option 3]
          [Extracted Option 4]

          if options are not present, say No options.and if the image doesnt contain any question the say 'Given image dont have any question or text'""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.0,
        "seed": 42,
    }
    r = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    return dict(r.json())["choices"][0]["message"]["content"]
