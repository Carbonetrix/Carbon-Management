# BECM AI Assistant

BECM AI Assistant is a Streamlit-based application designed to provide detailed responses to questions related to Carbon Management for the Built Environment. The AI assistant is powered by Claude AI and offers responses based on the user's expertise level, including Beginner, Intermediate, and Professional.

## Features

- User authentication via company name and email.
- Multi-level explanations (Beginner, Intermediate, Professional).
- Chat history with persistent session state.
- Feedback submission to MongoDB.
- Instant display of user queries and AI responses.
- Customizable avatars and branding.

## Prerequisites

- Python 3.7+
- Streamlit
- MongoDB
- Claude AI API Key
- dotenv for environment variable management

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/becm-ai-assistant.git
   cd becm-ai-assistant

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install the required packages:
    ```bash
    pip install -r requirements.txt

4. Set up environment variables by creating a .env file in the root directory and adding your MongoDB URI and Claude AI API Key:
    ```bash
    uri=your_mongodb_uri
    CARBONETRIX_ANTHROPIC_API_KEY=your_claude_ai_api_key

5. Ensure you have an image named logo.png in the Images directory for branding.


# Usage

1. Run the Streamlit application:
    ```bash
    streamlit run chatbot.py

2. Open your browser and navigate to http://localhost:8501.

3. Enter your company name and email to continue.

4. Select your expertise level from the sidebar.

5. Interact with the AI assistant by typing questions in the input box.

6. View chat history and submit feedback via the sidebar.


# Code Overview

## app.py

- Imports and Environment Setup: Loads required libraries and environment variables.
- MongoDB Management: Connects to MongoDB and initializes collections.
- Session State Initialization: Initializes session state variables for chat history, messages, and user details.
- Functions: Includes functions for adding questions and feedback to the database and fetching responses from Claude AI.
- Main Function: Handles user authentication, feedback submission, chat interface, and interaction logic.

## Streamlit Components

- Sidebar: Used for user authentication, feedback submission, level selection, and displaying chat history.
- Chat Container: Displays chat messages.
- Input Container: Captures user input and displays instant responses.

## Helper Functions

- 'add_question_to_db(question, timestamp)': Adds user questions to the MongoDB database.
- 'add_feedback_to_db(feedback, timestamp)': Adds user feedback to the MongoDB database.
- 'get_claude_response(user_content, level)': Fetches responses from Claude AI based on user input and selected expertise level.
- 'clear_chat_history()': Clears chat history from session state


# License

This project is licensed under the MIT License. See the LICENSE file for details.