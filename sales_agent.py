import streamlit as st
import pandas as pd
from autogen import UserProxyAgent, AssistantAgent
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('environment.env')

llm_config = {
    "config_list": [
        {
            "model": "mistralai/mistral-7b-instruct",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1"
        }
    ],
    "temperature": 0.3,
}

def summarize_bank_statement(text):
    user_proxy = UserProxyAgent(
        name="User",
        llm_config=llm_config,
        code_execution_config=False,
        human_input_mode="NEVER"
    )
    
    summarizer_agent = AssistantAgent(
        name="SummarizerAgent",
        llm_config=llm_config,
        system_message="Summarize financial bank statement data. Identify necessary versus discretionary expenses. You just have give total income and expense" \
        "and tell how much money is available to invest (income - expenses). Comment on total discretionary expenses as they can be additional savings."
    )
    
    # Initiate chat and capture messages
    # user_proxy.initiate_chat(
    #     summarizer_agent,
    #     message=f"Analyze this bank statement:\n\n{text}"
    # )

    response = user_proxy.initiate_chat(
        summarizer_agent,
        message=f"Analyze this bank statement:\n\n{text}",
        auto_reply=True,
        max_turns=1
    )

    #print(type(response))
    #print((response))
    return getattr(response, 'summary', None)
    
    # Extract the last message from the assistant
    # if summarizer_agent.chat_messages:
    #     messages = summarizer_agent.chat_messages[user_proxy]
    #     if messages:
    #         return messages[-1]["content"]
    # return "Could not generate summary"

def collect_user_profile():
    #st.subheader("📄 Step 1: Profile Details")

    short_term_goal = st.text_input("🏦 What is your short-term financial goal?")
    long_term_goal = st.text_input("💰 What is your long-term financial goal?")
    uploaded_file = st.file_uploader("📄 Upload your bank statement (.csv)", type=["csv"])

    # Initialize session state
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "profile_submitted" not in st.session_state:
        st.session_state.profile_submitted = False

    user_profile = st.session_state.user_profile

    # Submit Profile Button
    if st.button("🚀 Submit Profile"):
        if all([short_term_goal, long_term_goal, uploaded_file]):
            bank_data = pd.read_csv(uploaded_file)
            user_profile = {
                "short_term_goal": short_term_goal,
                "long_term_goal": long_term_goal,
                "bank_data_text": bank_data.to_string(),
                "bank_summary": None,
            }
            st.session_state.user_profile = user_profile
            st.session_state.profile_submitted = True
            st.success("✅ Profile saved! Click Process Bank Statement below.")
        else:
            st.warning("Please fill out all fields and upload a file.")

    # Process Bank Statement Button (run only if summary not already present)
    if st.session_state.get("profile_submitted") and st.session_state.user_profile:
        if st.button("🛠 Process Bank Statement Summary"):
            if not st.session_state.user_profile.get("bank_summary"):
                bank_text = st.session_state.user_profile["bank_data_text"]
                with st.spinner("Analyzing transactions..."):
                    summary = summarize_bank_statement(bank_text)
                    st.session_state.user_profile["bank_summary"] = summary
                st.success("✅ Analysis complete!")
            else:
                st.info("Bank statement already summarized.")

    # Always display the summary if it exists
    if st.session_state.user_profile and st.session_state.user_profile.get("bank_summary"):
        st.markdown("### Bank Statement Summary")
        st.write(st.session_state.user_profile["bank_summary"])

    return st.session_state.user_profile
