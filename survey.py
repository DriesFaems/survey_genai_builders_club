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
groq_api_key = st.secrets["GROQ_API_KEY"]

# set environment variable for GROQ API key

os.environ["GROQ_API_KEY"] = groq_api_key

airtable = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)


# Initialize session state to keep track of the process
if 'goals_processed' not in st.session_state:
    st.session_state.goals_processed = False
    st.session_state.goals = ""

# Create title for WHU MBA Streamlit App
st.title("Survey WHU GenAI Builders Club")

st.write("Welcome to the survey on the WHU GenAI Builders Club. The purpose of this survey is to get a better perspective on the community and to collect the necessary information to stimulate networking among the members.") 
         
st.markdown("**Please execute the following steps**")
st.write("Step 1: Fill in the form below and upload your LinkedIn profile.")
st.write("Step 2: Based on your LinkedIn profile, the application will give you a first suggestion of your potential contribution to the GenAI Builders Club. You can review and adjust these suggestions to your preference.")
st.write("Step 3: After you have adjusted the contributions, you need to click on Save Adjusted Contributions. This will end the registration process")

text = ""

# Display initial input form for user details and PDF upload
with st.form("registration_form"):
    name = st.text_input("Please enter your first name and last name")
    email = st.text_input("Please enter your email address")
    # create multiple choice question
    genai_experience = st.radio("Please indicate which statement best reflects your current experience with generative AI tools:", ("Beginner: Just starting out with generative AI tools, limited or no prior experience", "Novice: Has some basic knowledge of generative AI tools but lacks practical experience.", "Intermediate: Has a fair amount of experience and a good understanding of generative AI tools", "Advanced: Highly skilled and experienced with generative AI tools", "Expert: Deep, specialized knowledge on using generative AI tools"))
    coding_experience = st.radio("Please indicate which statement best reflects your current experience with coding:", ("Beginner: Just starting out with coding, limited or no prior experience", "Novice: Has some basic knowledge of coding but lacks practical experience.", "Intermediate: Has a fair amount of experience and a good understanding of coding", "Advanced: Highly skilled and experienced with coding", "Expert: Deep, specialized knowledge on coding"))
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

        client = Groq()
        GROQ_LLM = ChatGroq(model="llama3-70b-8192")

        # Create agent to analyze the text and identify core skills
        goal_identifier = Agent(
            role='Identify core contributions based on the LinkedIn profile',
            goal=f"""Identify core contributions based on the LinkedIn profile.""", 
            backstory=f"""You are a great expert in helping people to identify which contributions they can make to the Generative AI Builders Club, which is a community initiative where community members try to jointly leverage generative ai for application building. 
            You have been trained to rely on the LinkedIn profile of persons to formulate specific contributions""",  
            verbose=True,
            llm=GROQ_LLM,
            allow_delegation=False,
            max_iter=5,
        )

        # Create a task to identify the core skills
        identify_goals = Task(
            description=f""" Based on the LinkedIn profile provided below, identify and suggest three specific contributions that the person could make to the Generative AI Builders Club. 
                        Rules:The contributions should be: (i) Tailored to their professional background, skills, interests, and career objectives; (ii) Actionable and specific, enabling the person to make meaningful connections. (iii)Aligned with the objectives of the Generative AI Builders Club.
                        Instructions: Begin by briefly summarizing the person's current professional status and objectives based on their LinkedIn profile. For each contribution, provide a clear and concise description. Present the contributions in a numbered list for clarity.
                        Here is the LInkedIn profile: {st.session_state.profile} """,
            expected_output='As output, provide a clear description of the identified contributions.',
            agent=goal_identifier,
        )

        crew = Crew(
            agents=[goal_identifier],
            tasks=[identify_goals],
            process=Process.sequential,
            share_crew=False,
        )
        results = crew.kickoff()
        st.session_state.goals = identify_goals.output.exported_output
        st.session_state.goals_processed = True

        
    else:
        st.error("Please upload a PDF file.")

# If skills have already been processed, allow adjustment without re-running the agents
if st.session_state.goals_processed:
    with st.form("adjust_goals_form"):
        adjusted_goals = st.text_area("Please review and adjust the contributions below:", value=st.session_state.goals)
        save_adjusted_goals = st.form_submit_button("Save Adjusted Networking Goals")

    if save_adjusted_goals:
        st.session_state.goals = adjusted_goals
        st.write("Adjusted Goals Saved:")
        st.write(st.session_state.goals)
        st.markdown("**Registration successful. You can now leave the registration.**")
        record = {"Name": name, "Email": email, "LinkedIn Profile": st.session_state.profile, "Contributions": st.session_state.goals, "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Generative AI Experience": genai_experience, "Coding Experience": coding_experience}
        airtable.create(record)

