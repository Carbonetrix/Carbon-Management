import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import chatbot as app


# Security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False



uri = "mongodb+srv://Usman:DvlNBJrLRyU0gESv@carbonetrix.pllb2my.mongodb.net/?retryWrites=true&w=majority&appName=Carbonetrix"

# MongoDB Management
client = MongoClient(uri)
    
db = client.get_database("Carbonetrix")
users_collection = db['Carbonetrix']




# DvlNBJrLRyU0gESv


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# DB Functions
def create_usertable():
    pass  # Not needed for MongoDB

def add_userdata(username, password,email,company_name):
    users_collection.insert_one({"username": username, "email": email,"password": password,"comapnr_name":company_name})
    # users_collection.insert_one({"username": username, "password": password, "email": email, "company_name": company_name})
    db.create_collection(company_name)


def login_user(username, password):
    user=users_collection.find_one({"username": username, "password": password})
    return user


def view_all_users():
    users = users_collection.find()
    return list(users)

def get_user_by_username(username):
    return users_collection.find_one({"username": username})

def update_password(username, new_password):
    users_collection.update_one({"username": username}, {"$set": {"password": new_password}})

def send_reset_email(to_email, new_password):
    from_email = "olamidehassan007@gmail.com"
    from_password = "Osuolale99"
    subject = "Password Reset"
    message = f"Your new password is: {new_password}"
    

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

def main():
    """Simple Login App"""

    # st.title("Simple Login App")

    menu = ["Home","SignUp", "Login", "Forgot Password"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        # st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            # result = login_user(username, password)
            if result:
                st.success(f"Logged In as {username}")

                task = st.sidebar.selectbox("Task", ["BECM AI Assistant", "Chat Your Files", "Decarbonisation news"])
                if task == "BECM AI Assistant":
                    app.main()

                elif task == "Chat Your Files":
                    # st.subheader("Analytics")
                    app.main()
                elif task == "Decarbonisation news":
                    st.subheader("User Profiles")
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result, columns=["Username", "Password"])
                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        email = st.text_input("Email")
        company_name = st.text_input("Company Name")
        # email=st.text_input("Email")
    



        if st.button("Signup"):
            # create_usertable()
            # add_userdata(new_user, make_hashes(new_password))
            add_userdata(new_user, make_hashes(new_password), email, company_name)
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

    elif choice == "Forgot Password":
        st.subheader("Forgot Password")
        username = st.text_input("Username")
        if st.button("Reset Password"):
            user = get_user_by_username(username)
            if user:
                new_password = "newpassword123"  # Generate or use a more secure method
                hashed_new_password = make_hashes(new_password)
                update_password(username, hashed_new_password)
                send_reset_email(user['username'], new_password)
                st.success("A new password has been sent to your email address.")
            else:
                st.warning("Username not found")

if __name__ == '__main__':
    main()

