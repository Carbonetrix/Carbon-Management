

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
import anthropic

# model = genai.GenerativeModel("gemini-1.5-flash-latest")
# chat = model.start_chat(history=[])


# MongoDB Management
# client = MongoClient(os.getenv("uri"))
client = MongoClient(st.secrets["uri"])
db = client.get_database("Carbonetrix")
users_collection = db['Carbonetrix']
feedback_collection = db['Feedback'] 



# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if 'level' not in st.session_state:
    st.session_state['level'] = 'Beginner'

# Add initial assistant message if chat history is empty
if not st.session_state["messages"]:
    st.session_state["messages"].append({"role": "assistant", "content": "Ask Me Anything About Carbon Management"})


if 'company_name' not in st.session_state:
    st.session_state['company_name'] = None

if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

def add_question_to_db(question, timestamp):
    company_collection = db["Questions"]
    company_collection.insert_one({
        "company": st.session_state['company_name'], 
        "email": st.session_state['user_email'], 
        "question": question, 
        "timestamp": timestamp
    })

def add_feedback_to_db(feedback, timestamp):
    feedback_collection.insert_one({
        "feedback": feedback, 
        "timestamp": timestamp,
        "company": st.session_state['company_name'], 
        "email": st.session_state['user_email'],
    
    })



# Prompting of the model through API
# def get_gemini_response(question, level):
#     level_instructions = {
#         "Beginner": "Explain in simple terms with basic details.",
#         "Intermediate": "Provide more detailed explanations with some technical terms.",
#         "Professional": "Include advanced technical details and professional formulas and point of view."
#     }

#     prompt = (
#         f"You are an AI Assistant specializing in Carbon Management for the Built Environment (construction, buildings, and infrastructure). "
#         f"You are used by professionals in the field and construction organizations. Be explicit, informative, and explain technical concepts in a clear manner. "
#         f"If any question apart from Carbon Management for the Built Environment or construction or infrastructure is asked, kindly say 'I'm sorry, I answer carbon-related questions only.' "
#         f"Always provide at least 5 references and footnotes from reputable and accessible sources such as academic journals, official government or organizational websites, and well-known industry publications. "
#         f"Make sure the references are accessible and not broken links. "
#         f"Ensure the response is well-documented and avoid unnecessary breaking of lines. "
#         f"{level_instructions[level]} "
#         f"Question: {question}"
#     )
#     response = chat.send_message(prompt, stream=True)
#     return response


def get_claude_response(user_content, level):
    api_key = st.secrets.CARBONETRIX_ANTHROPIC_API_KEY
    # api_key = os.getenv("CARBONETRIX_ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    
    level_instructions = {
        "Beginner": "Explain in simple terms with basic details.",
        "Intermediate": "Provide more detailed explanations with some technical terms.",
        "Professional": "Include advanced technical details and professional formulas and points of view."
    }

    prompt = (
        f"You are an AI Assistant specializing in Carbon Management for the Built Environment (construction, buildings, and infrastructure). "
        f"You are used by professionals in the field and construction organizations. Be explicit, informative, and explain technical concepts in a clear manner. "
        f"If any question apart from Carbon Management for the Built Environment or construction or infrastructure is asked, kindly say 'I'm sorry, I answer carbon-related questions only.' "
        f"Always provide at least 5 references and footnotes from reputable and accessible sources such as academic journals, official government or organizational websites, and well-known industry publications. "
        f"Make sure the references are accessible and make each refences on a new line "
        f"Ensure the response is well-documented and avoid unnecessary breaking of lines. "
        f"{level_instructions[level]} "
        f"Question: {user_content}"
    )
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="Generate detailed responses to user-provided questions",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text



def main():
   
    if not st.session_state['company_name'] or not st.session_state['user_email']:
        st.sidebar.header("User Information")
        company_name = st.sidebar.text_input("Please enter your Username/company's name to continue:")
        user_email = st.sidebar.text_input("Please enter your email to continue:")
      

        if st.sidebar.button("Submit"):
            if company_name and user_email:
                st.session_state['company_name'] = company_name
                st.session_state['user_email'] = user_email
                st.experimental_rerun()
            else:
                st.sidebar.warning("Please enter both your company name and email to continue.")
        else:
            st.stop()

    with st.sidebar:
        st.header("Feedback")
        feedback = st.text_area("Please provide your feedback here")
        if st.button("Submit Feedback"):
            timestamp = datetime.now()
            add_feedback_to_db(feedback, timestamp)
            st.success("Thank you for your feedback!")

    # st.set_page_config(layout="wide")
    c1, c2, c3 = st.columns([1, 2, 1])
    pth = "Images/logo.png"
    c1.image(pth, width=180)
    c2.title(":blue[BECM AI ASSISTANT]")


    st.sidebar.selectbox('Select Level:', ['Beginner', 'Intermediate', 'Professional'], key='level')


    st.sidebar.title("Chat History")
    for entry in st.session_state['chat_history']:
        role, content,timestamp= entry
        if role == "You":
            st.sidebar.write(f"{content} ")

    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    user_avatar_style="identicon"
    user_seed = "123456"

    def image_to_base64(image_path):
        img = Image.open(image_path)
        buffer = BytesIO()
        img.save(buffer, format="PNG",)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_str

    bot_logo_base64 = image_to_base64("Images/logo.png")
    bot_logo_html = f"data:image/png;base64,{bot_logo_base64}"



    # Initializing streamlit containers
    chat_container = st.container()
    input_container = st.container()

    with chat_container:
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages):
                if isinstance(msg, dict) and msg.get("role") == "user" and "content" in msg:
                    # st.chat_message(msg["content"], is_user=True, key=f"user_{i}")
                    message(msg["content"], is_user=True, key=f"user{i}",avatar_style=user_avatar_style, seed=user_seed,)
                elif isinstance(msg, dict) and msg.get("role") == "assistant" and "content" in msg:
                    # Custom HTML for displaying the company logo
                    st.markdown(f"""
                    <div id='{i}' style='text-align: left; color: black; background-color: #f4f4f4; padding: 10px; border-radius: 10px; margin: 10px 0;'>
                        <img src='{bot_logo_html}' alt='Bot Avatar' style='width: 30px; height: 30px; border-radius: 50%; display: inline-block; vertical-align: middle; margin-right: 10px;' />
                        <span style='vertical-align: middle;'>\n{msg['content']}\n</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    st.error("Invalid message format")




    # with input_container:
    if prompt := st.chat_input():
        message(prompt, is_user=True, key=f"user{i}",avatar_style=user_avatar_style, seed=user_seed,)
        timestamp = datetime.now()
        add_question_to_db(prompt, timestamp)
      
        
        with input_container:
            if prompt:
                
                response_text = get_claude_response(prompt, st.session_state['level'])
                # response = get_gemini_response(prompt, st.session_state['level'])
                # response_text = "".join(chunk.text for chunk in response)
        
        

                timestamp = datetime.now()
                st.session_state['chat_history'].append(("You", prompt, timestamp))
                st.session_state['chat_history'].append(("Bot", response_text, timestamp))

                st.session_state["messages"].append({"role": "user", "content": prompt})
                st.session_state["messages"].append({"role": "assistant", "content": response_text})

                st.experimental_rerun()

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Ask Me Anything About Carbon Management"}]
    st.session_state['chat_history'] = []
    # st.experimental_rerun()


if __name__ == "__main__":
    main()
