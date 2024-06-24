import streamlit as st
from pymongo import MongoClient

# Use Streamlit's secrets management to fetch the credentials
db_username = st.secrets["db_username"]
db_password = st.secrets["db_password"]
cluster_name = st.secrets["cluster_name"]

# Define a function that initializes the connection to MongoDB
# @st.experimental_singleton(suppress_st_warning=True)
def init_connection():
    uri = f"mongodb+srv://{db_username}:{db_password}@{cluster_name}.mongodb.net/?retryWrites=true&w=majority&appName=Carbonetrix"
    return MongoClient(uri)

# Initialize the connection
client = init_connection()

# Use the client to interact with the database
db = client["your_database_name"]  # Replace with your database name
collection = db["your_collection_name"]  # Replace with your collection name

# Example Streamlit app content
st.title("MongoDB Connection Test")
st.write("Connected to the database!")

# Example query
documents = collection.find().limit(5)
for doc in documents:
    st.write(doc)
