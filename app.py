import base64
import json
from io import BytesIO
import PyPDF2
import streamlit as st
from streamlit_javascript import st_javascript
from streamlit_pdf_viewer import pdf_viewer
from openai import OpenAI


# Setting Streamlit page configuration
st.set_page_config(page_title="pdf-GPT", page_icon="📖", layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        

local_css("style.css")

# Function to convert PDF to structured text
def convert_pdf_to_structured_text(pdf_file):
    """Extracts text from a PDF file and returns it with basic formatting."""
    if not pdf_file:
        return ""  # Handle empty file case

    with BytesIO(pdf_file.read()) as buffer:  # Use BytesIO to read file-like object
        pdf_reader = PyPDF2.PdfReader(buffer)
        num_pages = len(pdf_reader.pages)

        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"  # Add double line breaks for page breaks

        return text

# Setting up OpenAI API key

openai_api_key = st.secrets["API_KEY"]

# Initializing messages list
messages = []

# App layout
st.header("Your Bank Statement App")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

# Function to clear submit flag
def clear_submit():
    st.session_state["submit"] = False


# Sidebar upload and processing
with st.sidebar:
    st.markdown("<p style='font-family: san serif; color: black; font-size: 20px; padding: 0px; margin: 0px'>Upload PDF</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf"],
        on_change=clear_submit,
        label_visibility = "hidden"
    )

    # pdf_viewer(uploaded_file)
    structured_text = convert_pdf_to_structured_text(uploaded_file)
    if structured_text:
        prompt = f""" Below is a bank statement of a client in textual form. We want to find these information out of it: Bank name, Customer name, IBAN, Account number, Phone number, Salary, Statement balance, Highest spent amount, Highest received amount.
        The output should be an array with the values like this: [Bank name, Customer name, IBAN, Account number, Phone number, Salary, Statement balance, Highest spent amount, Highest received amount]. And if there is no bank statement output an array like this ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
        The bank statement text is: "{structured_text}"
        """
        client = OpenAI(api_key=openai_api_key)
        messages.append([{"role": "user", "content":prompt }])
        response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content":prompt }])
        data = response.choices[0].message.content
        print(data)
    if structured_text:
        
        print(data)
        data  = json.loads(data)


# Main content display
col1, col2 = st.columns(spec=[2, 1], gap="small")

if uploaded_file:
    with col1:
        with st.container(border = True)
            if uploaded_file:
                pdf_viewer(uploaded_file.getvalue())

    with col2:
        if data:
            with st.expander("Get Customer Information"):
                # st.subheader("Get information")

                # Display extracted information
                labels = ["Bank Name", "Customer Name", "IBAN", "Account Number", "Phone Number", "Salary", "Statement Balance", "Highest Spent Amount", "Highest Received Amount"]
                for label, value in zip(labels, data):
                    st.markdown(f"<p style='font-family: Arial; color: black; font-size: 25px;'>{label}:</p>", unsafe_allow_html=True)
                    st.write(value)
