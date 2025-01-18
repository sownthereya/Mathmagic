import asyncio
import base64
from io import BytesIO
from openai import OpenAI
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


MODEL='gpt-4o-2024-08-06'
MAX_TOKENS=2048


system_prompt = """
You are a helpful assistant that provides detailed, step-by-step solutions to problems. 
For math-related questions, focus on breaking down the solution into small steps and using LaTeX for equations.
For physics questions, explain the process step by step, including key concepts.
Always provide detailed explanations for each step and ensure the user understands how the solution is reached.
Avoid unnecessary conversational phrases like 'Here is the solution'.
"""

user_prompt = """
This is my question: {query}. Help me to solve it.

Instructions:

1. Break down the solution into clear steps.
2. Explain each step in detail and how it leads to the next.
3. For math problems, prioritize derivation and use LaTeX for formulas (enclosed in $$).
4. For physics, provide a step-by-step explanation with key concepts.
5. Verify the solution at the end and highlight important steps and the final answer.

must enclose the equation and formulas with $$ and $ like $$a^2 + b^2 = c^2$$ to be displayed properly in the streamlit application.
"""

user_prompt_for_image = """
I have attached image with question/problem Help me to solve it.

Instructions:

1. Break down the solution into clear steps.
2. Explain each step in detail and how it leads to the next.
3. For math problems, prioritize derivation and use LaTeX for formulas (enclosed in $$).
4. For physics, provide a step-by-step explanation with key concepts.
5. Verify the solution at the end and highlight important steps and the final answer.

must enclose the equation and formulas with $$ and $ like $$a^2 + b^2 = c^2$$ to be displayed properly in the streamlit application.
"""

def encode_image(image):

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def process_image_question(image):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text":user_prompt_for_image },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(image)}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=MAX_TOKENS,
            seed=42,
            stream=True
        )
        # return response.choices[0].message.content
        for chunk in response:
            c=chunk.choices[0].delta.content
            if c:
                yield c

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

# Function to get response from OpenAI for text-only query
def process_text_question(question):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content":system_prompt},
                {"role": "user", "content": user_prompt.format(query=question)}
            ],
            stream=True,
            seed=42,
            max_tokens=MAX_TOKENS
        )
        for chunk in response:
            c=chunk.choices[0].delta.content
            if c:
                yield c

    except Exception as e:
        return f"An error occurred: {str(e)}"
    

def run_async(coro):
    return asyncio.run(coro)

# Streamlit app
def main():
    st.title("Math Magic 🪄")

    # Create tabs
    tab1, tab2 = st.tabs(["Image-based Question", "Text-based Question"])

    # Image-based Question tab
    with tab1:
        st.header("Image-based Question")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            
            if st.button("Extract Question", key="image_button"):
                with st.spinner('Processing...'):
                    extracted_question = process_image_question(image)
                    st.write("**Extracted Question:**")
                    st.write(extracted_question)

    # Text-based Question tab
    with tab2:
        st.header("Text-based Question")
        text_question = st.text_input("Ask a general question:")

        if text_question:
            if st.button("Get Answer for Text", key="text_button"):
                with st.spinner('Processing...'):
                    answer = process_text_question(text_question)
                    st.write("**Answer:**")
                    st.write(answer)

if __name__ == "__main__":
    main()