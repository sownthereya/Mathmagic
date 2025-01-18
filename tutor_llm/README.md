# Tutor llm

## Overview

This project requires an OpenAI API key and a JWT token to function properly. Please follow the steps below to set them up before running the application.

## Setup Instructions

1. **Install Dependencies**

   Install the required dependencies using your preferred package manager.

   pip install -r requirements.txt

2. **Generate a JWT Token**

   If you don't already have a JWT token, you can generate one using a simple command in the terminal. For example, using `openssl`:

   JWT_TOKEN=$(openssl rand -base64 32)
   echo "Your generated JWT token is: $JWT_TOKEN"

   This command generates a random string, which you can use as a JWT token.

3. **Set Up Environment Variables**

   Create a `.env` file in the root of your project and add the following environment variables:

   OPENAI_API_KEY=your-openai-api-key
   JWT_TOKEN=your-jwt-token

   Replace `your-openai-api-key` with your actual OpenAI API key and `your-jwt-token` with the token you generated in the previous step.

4. **Run the Application**

   After setting up your environment variables, you can run the application:

   python api.py

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
