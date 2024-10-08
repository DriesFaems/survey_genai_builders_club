from groq import Groq
import streamlit as st
import os
from crewai import Crew, Agent, Task, Process
from langchain_groq import ChatGroq
from PyPDF2 import PdfReader
from pyairtable import Table
import datetime

AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]  # Replace with your table name


# set environment variable for GROQ API key

airtable = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

# Create title for WHU MBA Streamlit App
st.title("Survey WHU GenAI Builders Club")

st.write("Welcome to the survey on the WHU GenAI Builders Club. The purpose of this survey is to get a better perspective on the community and to collect the necessary information to stimulate networking among the members.") 

text = ""

# Display initial input form for user details and PDF upload
with st.form("registration_form"):
    name = st.text_input("Please enter your first name and last name")
    email = st.text_input("Please enter your email address")
    # create multiple choice question
    genai_experience = st.radio("Please indicate which statement best reflects your current experience with generative AI tools:", ("Beginner: Just starting out with generative AI tools, limited or no prior experience", "Novice: Has some basic knowledge of generative AI tools but lacks practical experience.", "Intermediate: Has a fair amount of experience and a good understanding of generative AI tools", "Advanced: Highly skilled and experienced with generative AI tools", "Expert: Deep, specialized knowledge on using generative AI tools"))
    coding_experience = st.radio("Please indicate which statement best reflects your current experience with coding:", ("Beginner: Just starting out with coding, limited or no prior experience", "Novice: Has some basic knowledge of coding but lacks practical experience.", "Intermediate: Has a fair amount of experience and a good understanding of coding", "Advanced: Highly skilled and experienced with coding", "Expert: Deep, specialized knowledge on coding"))
    application_expriene =st.text_area("Please describe your experience with building applications using generative AI tools")
    # user needs to indicate with yes or no if they are a student
    uploaded_file = st.file_uploader("Please upload a PDF of your LinkedIn profile. You can find this PDF by going to your LinkedIn profile page, click on More, and click on Save PDF. By uploading the file, you agree that we use and store your LinkedIn profile for the purpose of networking in the GenAI Builders Club!", type="pdf")
    submit_form = st.form_submit_button("Submit")

# If the form is submitted
if submit_form and not st.session_state.goals_processed:
    if uploaded_file is not None:
        # Read the pdf file
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.session_state.profile = text

        
        record = {"Name": name, "Email": email, "LinkedIn Profile": st.session_state.profile, "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Generative AI Experience": genai_experience, "Coding Experience": coding_experience, "Application Experience": application_expriene}
        airtable.create(record)
        st.markdown("**Registration successful. You can now leave the registration.**")
        
    else:
        st.error("Please upload a PDF file.")



