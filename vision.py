# # Q&A Chatbot
# #from langchain.llms import OpenAI

# from dotenv import load_dotenv

# load_dotenv()  # take environment variables from .env.

# import streamlit as st
# import os
# import pathlib
# import textwrap
# from PIL import Image


# import google.generativeai as genai


# os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ## Function to load OpenAI model and get respones

# def get_gemini_response(input,image,prompt):
#     model = genai.GenerativeModel('gemini-pro-vision')
#     response = model.generate_content([input,image[0],prompt])
#     return response.text
    

# def input_image_setup(uploaded_file):
#     # Check if a file has been uploaded
#     if uploaded_file is not None:
#         # Read the file into bytes
#         bytes_data = uploaded_file.getvalue()

#         image_parts = [
#             {
#                 "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
#                 "data": bytes_data
#             }
#         ]
#         return image_parts
#     else:
#         raise FileNotFoundError("No file uploaded")


# ##initialize our streamlit app

# st.set_page_config(page_title="Gemini Image Demo")

# st.header("Gemini Application")
# input=st.text_input("Input Prompt: ",key="input")
# uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
# image=""   
# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="Uploaded Image.", use_column_width=True)


# submit=st.button("Tell me about the image")

# input_prompt = """
#                You are an expert in understanding invoices.
#                You will receive input images as invoices &
#                you will have to answer questions based on the input image
#                """

# ## If ask button is clicked

# if submit:
#     image_data = input_image_setup(uploaded_file)
#     response=get_gemini_response(input_prompt,image_data,input)
#     st.subheader("The Response is")
#     st.write(response)
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Check if Firebase Admin SDK has been initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("C:/Users/Pradnya/Desktop/credentials.json.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    # If Firebase app is already initialized, use the existing app
    db = firestore.client()

# Configure Generative AI with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load OpenAI model and get responses
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Authentication step
def login():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.button("Login")

    if submitted:
        try:
            user = auth.get_user_by_email(email)
            # Verify user's password
            # You may need to handle password verification on the client-side
            # as Firebase Admin SDK doesn't provide direct method for password verification
            # Typically, use Firebase Authentication client SDK on the frontend
            # If verification is successful, return True
            # and store the user's email in the session
            if user:
                # Set session token or flag
                st.session_state.is_logged_in = True
                return email
        except:
            st.error("Authentication failed. Please check your email and password.")
    return None

def signup():
    st.subheader("Signup")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.button("Signup")

    if submitted:
        if not email or not password:
            st.error("Please provide both email and password.")
            return None
        
        try:
            user = auth.create_user(email=email, password=password)

            # Save user data to Firestore
            save_user_data(user.uid, email)

            st.success("User registered successfully!")
            return email
        except Exception as e:
            st.error(f"Registration success")
    return None

def save_user_data(user_id, email):
    user_ref = db.collection("users").document(user_id)
    user_ref.set({
        "email": email
        # Add more user data fields as needed
    })

def main():
    # Check if user is logged in
    if st.session_state.get("is_logged_in", False):
        # User is logged in
        st.title("Gemini Application")
        st.write("Welcome to the Gemini Application!")
        input_text = st.text_input("Input Prompt: ", key="input")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        image = ""   
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
        submit = st.button("Tell me about the image")
        input_prompt = """
                       You are an expert in understanding invoices.
                       You will receive input images as invoices &
                       you will have to answer questions based on the input image
                       """
        # If ask button is clicked
        if submit:
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt, image_data, input_text)
            st.subheader("The Response is")
            st.write(response)
    else:
        # User is not logged in
        st.sidebar.title("Authentication")
        auth_option = st.sidebar.radio("Choose option", ["Login", "Signup"])
        if auth_option == "Login":
            user_email = login()
        elif auth_option == "Signup":
            user_email = signup()
        if user_email:
            st.title(f"Welcome, {user_email}")

if __name__ == "__main__":
    main()
