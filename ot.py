
import streamlit as st
import os
from dotenv import load_dotenv

from sales_agent import collect_user_profile
from investment_agent import suggest_investments
from budgetagent import analyze_budget

# Load API keys
load_dotenv('environment.env')

def main():
    st.set_page_config(page_title="💸 Personal Financial Portal", page_icon="💰")
    st.title("💸 Personal Financial Portal")

    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox("Choose a page:", ["🏠 Home", "📑 Share goals and flows", "📈 Investment Planning", "📝 Budget Planning", "🎯 Final Summary"])

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "investment_plan" not in st.session_state:
        st.session_state.investment_plan = None
    if "budget_plan" not in st.session_state:
        st.session_state.budget_plan = None

    if page == "🏠 Home":
        st.subheader("Welcome!")
        st.write("""
            This portal helps you create **short-term budgets** and **long-term investment plans** based on your financial goals.
            
            Steps:
                 
            First, tell us your financial goals/wishes in the "Share goals and flows" tab on the sidebar. 
                 
            Then, use the other sidebar options to view analysis on your monthly budget and to get investment strategy.
                 
            This is just to help you start thinking about your options. 
            When you are ready, contact us. Our expert human-financial advisors will see you through the plan.
        """)
        st.success("Use the sidebar to navigate.")

    elif page == "📑 Share goals and flows":
        st.subheader("📑 Step 1: Profile Details")
        collect_user_profile()

    elif page == "📈 Investment Planning":
        st.subheader("📈 Step 2: Investment Plan")

        st.write("🔍 Debug - User Profile in Session:", st.session_state.get("user_profile"))  # Temporary Debugging Line

        if st.session_state.user_profile:
            with st.spinner("Generating Investment Strategy..."):
                investment_plan = suggest_investments(st.session_state.user_profile)
                st.session_state.investment_plan = investment_plan
                st.success("✅ Investment plan generated!")
                #st.json(investment_plan)
                st.write(investment_plan)
        else:
            st.warning("⚠️ Please fill your profile first.")

    elif page == "📝 Budget Planning":
        st.subheader("📝 Step 3: Budget Plan")

        if st.session_state.user_profile:
            with st.spinner("Analyzing Budget Strategy..."):
                budget_plan = analyze_budget(st.session_state.user_profile)
                st.session_state.budget_plan = budget_plan
                st.success("✅ Budget plan generated!")
                st.write(budget_plan)
                # st.json(budget_plan)
        else:
            st.warning("⚠️ Please fill your profile first.")

    elif page == "🎯 Final Summary":
        st.subheader("🎯 Step 4: Final Combined Plan")

        if st.session_state.investment_plan and st.session_state.budget_plan:
            st.balloons()
            st.success("✅ Here’s your full financial plan:")
            st.markdown(f"**Short-Term Goal Plan:** {st.session_state.budget_plan.get('short_term_plan', 'No plan')}")
            st.markdown(f"**Long-Term Investment Plan:** {st.session_state.investment_plan.get('investment_recommendation', 'No plan')}")
        else:
            st.warning("⚠️ Please complete Investment and Budget Planning first.")

if __name__ == "__main__":
    main()

