

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
load_dotenv() 
import streamlit as st
import json
import os
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from transformers import pipeline


load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

print(genai.configure(api_key=os.getenv("GOOGLE_API_KEY")))

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])



def get_gemini_response(question):
    prompt = """You are an AI Assistant specializing in Carbon Management for the Built Environment (construction, buildings, and infrastructure). 
    You are used by professionals in the field and construction organizations. Be explicit, informative, and explain technical concepts in a clear manner.
    If Any question apart of Carbon Management for the Built Environment or construction ot infrasrructure is asked kindly say "I'm Sorry i  Answer Carbon related Questions Only.
    You alway put at least three references and footnotes in accordance to the references a
    Make the result well documented an avoid unneccessary breaking of lines

 
    """

    response = chat.send_message(prompt+str(question), stream=True)
    return response

def main():
    c1, c2,c3 = st.columns(3)
    pth="Images\Logo2.jpg"
    c1.image(pth, width=200)
    c2.title("Carbon Management Chatbot")
    # with st.sidebar:
        # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        # "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask Me Anything Carbon"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    
    if prompt := st.chat_input():
        st.info(prompt)
        # st.session_state['chat_history'].append(prompt)
        for entry in st.session_state['chat_history']:
            if entry[0] == "You":
                st.sidebar.write(f"{entry[1]}")
                
        response = get_gemini_response(prompt)
        for chunk in response:
            st.write(chunk.text)
            st.session_state['chat_history'].append(("Bot", chunk.text))

    for text in st.session_state['chat_history']:
        st.write(f"{text}")