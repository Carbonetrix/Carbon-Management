import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
import os
from streamlit_chat import message
import google.generativeai as genai
from pymongo.mongo_client import MongoClient
import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
load_dotenv() 
from datetime import datetime, timedelta
import streamlit as st
import json
import os
from streamlit_chat import message
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from pymongo.mongo_client import MongoClient
from PIL import Image
import base64
from io import BytesIO

class BECMAIAssistant:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = ""
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.get_database("Carbonetrix")
        self.users_collection = self.db['Carbonetrix']
        self.feedback_collection = self.db['Feedback']

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        self.model = genai.GenerativeModel("gemini-pro")
        self.chat = self.model.start_chat(history=[])
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        self.chat = self.model.start_chat(history=[])

        self.initialize_session_state()

    def initialize_session_state(self):
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        if 'level' not in st.session_state:
            st.session_state['level'] = 'Beginner'

        if 'company_name' not in st.session_state:
            st.session_state['company_name'] = None

        if not st.session_state["messages"]:
            st.session_state["messages"].append({"role": "assistant", "content": "Ask Me Anything About Carbon Management"})

    def add_question_to_db(self, question, timestamp):
        company_collection = self.db["Questions"]
        company_collection.insert_one({"company": st.session_state['company_name'], "question": question, "timestamp": timestamp})

    def add_feedback_to_db(self, feedback, timestamp):
        self.feedback_collection.insert_one({"feedback": feedback, "timestamp": timestamp, "company": st.session_state['company_name']})

    def get_gemini_response(self, question, level):
        level_instructions = {
            "Beginner": "Explain in simple terms with basic details.",
            "Intermediate": "Provide more detailed explanations with some technical terms.",
            "Professional": "Include advanced technical details and professional formulas and point of view."
        }

        prompt = (
            f"You are an AI Assistant specializing in Carbon Management for the Built Environment (construction, buildings, and infrastructure). "
            f"You are used by professionals in the field and construction organizations. Be explicit, informative, and explain technical concepts in a clear manner. "
            f"If any question apart from Carbon Management for the Built Environment or construction or infrastructure is asked, kindly say 'I'm sorry, I answer carbon-related questions only.' "
            f"Always provide at least 5 references and footnotes from reputable and accessible sources such as academic journals, official government or organizational websites, and well-known industry publications. "
            f"Make sure the references are accessible and not broken links. "
            f"Ensure the response is well-documented and avoid unnecessary breaking of lines. "
            f"{level_instructions[level]} "
            f"Question: {question}"
        )
        response = self.chat.send_message(prompt, stream=True)
        return response

    @staticmethod
    def image_to_base64(image_path):
        img = Image.open(image_path)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_str

    def clear_chat_history(self):
        st.session_state.messages = [{"role": "assistant", "content": "Ask Me Anything About Carbon Management"}]
        st.session_state['chat_history'] = []

    def display_sidebar(self):
        with st.sidebar:
            st.header("Feedback")
            feedback = st.text_area("Please provide your feedback here")
            if st.button("Submit Feedback"):
                timestamp = datetime.now()
                self.add_feedback_to_db(feedback, timestamp)
                st.success("Thank you for your feedback!")

            st.sidebar.selectbox('Select Level:', ['Beginner', 'Intermediate', 'Professional'], key='level')
            st.sidebar.title("Chat History")
            for entry in st.session_state['chat_history']:
                role, content, timestamp = entry
                if role == "You":
                    st.sidebar.write(f"{content} ")

            st.sidebar.button('Clear Chat History', on_click=self.clear_chat_history)

    def display_header(self):
        c1, c2, _ = st.columns([1, 2, 1])
        pth = "Images/Logo2.jpg"
        c1.image(pth, width=200)
        c2.title(":green[BECM AI ASSISTANT]")

    def display_chat(self):
        user_avatar_style = "identicon"
        user_seed = "1234"

        bot_logo_base64 = self.image_to_base64("Images/Logo2.jpg")
        bot_logo_html = f"data:image/png;base64,{bot_logo_base64}"

        chat_container = st.container()

        with chat_container:
            if st.session_state.messages:
                for i, msg in enumerate(st.session_state.messages):
                    if isinstance(msg, dict) and msg.get("role") == "user" and "content" in msg:
                        message(msg["content"], is_user=True, key=f"user_{i}", avatar_style=user_avatar_style, seed=user_seed)
                    elif isinstance(msg, dict) and msg.get("role") == "assistant" and "content" in msg:
                        st.markdown(f"""
                        <div id='{i}' style='text-align: left; color: black; background-color: #f4f4f4; padding: 10px; border-radius: 10px; margin: 10px 0;'>
                            <img src='{bot_logo_html}' alt='Bot Avatar' style='width: 50px; height: 50px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 10px;' />
                            <span style='vertical-align: middle;'>\n{msg['content']}\n</span>
                        </div>
                        """, unsafe_allow_html=True)
                    elif not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                        st.error("Invalid message format")

    def handle_input(self):
        if prompt := st.chat_input():
            timestamp = datetime.now()
            self.add_question_to_db(prompt, timestamp)
            if prompt:
                response = self.get_gemini_response(prompt, st.session_state['level'])
                response_text = "".join(chunk.text for chunk in response)

                timestamp = datetime.now()
                st.session_state['chat_history'].append(("You", prompt, timestamp))
                st.session_state['chat_history'].append(("Bot", response_text, timestamp))

                st.session_state["messages"].append({"role": "user", "content": prompt})
                st.session_state["messages"].append({"role": "assistant", "content": response_text})

                st.experimental_rerun()

    def run(self):
        if not st.session_state['company_name']:
            company_name = st.sidebar.text_input("Please enter your company's name to continue:")
            if company_name:
                st.session_state['company_name'] = company_name
                st.experimental_rerun()
            else:
                st.stop()

        self.display_sidebar()
        self.display_header()
        self.display_chat()
        self.handle_input()


if __name__ == "__main__":
    assistant = BECMAIAssistant()
    assistant.run()
