from autogen import UserProxyAgent, AssistantAgent
import os
from dotenv import load_dotenv

load_dotenv('environment.env')

llm_config = {
    "config_list": [
        {
            "model": "mistralai/mistral-7b-instruct",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "base_url": "https://openrouter.ai/api/v1"
        }
    ],
    "temperature": 0.4,
}

def suggest_investments(user_profile):
    user_proxy = UserProxyAgent(
        name="User",
        llm_config=llm_config,
        code_execution_config=False,
        human_input_mode="NEVER"
    )
    
    investor_agent = AssistantAgent(
        name="InvestmentPlannerAgent",
        llm_config=llm_config,
        system_message=("You are an expert financial planning assistant. "
            "Given the user's short-term and long-term goals, risk profile, investment time horizon, and bank statement summary, "
            "design two investment portfolio strategies: one aggressive and one conservative. "
            "Give advice to help them achieve their goals. The reccomendations should be succint and custom to user's finances."
        )

    )

    message = f"""
    Based on this user profile:
    - Short-Term Goal: {user_profile.get('short_term_goal', 'Not provided')}
    - Long-Term Goal: {user_profile.get('long_term_goal', 'Not provided')}
    - Bank Summary: {user_profile.get('bank_summary', 'No bank summary available')}
    

    Create two investment portfolios: one aggressive, one conservative. 
    Give specific advice in how much to invest and where to invest to help them achieve their goals.
    Calculate estimated return from each strategy.
    """

    response = user_proxy.initiate_chat(
        investor_agent,
        message=message,
        auto_reply=True,
        max_turns=1
    )
    
    draft_response = str(response.summary)
    
    # 🔥 ADD SELF-REFLECTION HERE 🔥
    reviewer_agent = AssistantAgent(
        name="SelfReviewAgent",
        llm_config=llm_config,
        system_message="You are a critical reviewer. Review the portfolio suggestion for logical consistency, practicality, and generate a complete and concrete response. Answer as if you are answering the user")

    review_response = user_proxy.initiate_chat(
        reviewer_agent,
        message=str(response.summary),
        auto_reply=True,
        max_turns=1)
    
    review_text = str(review_response.summary)

    # Now create a Refiner Agent
    refiner_agent = AssistantAgent(
        name="RefinerAgent",
        llm_config=llm_config,
        system_message=(
            "You are a financial assistant tasked with improving a draft plan based on reviewer feedback. "
            "Read the original plan and the reviewer suggestions carefully. "
            "Then create a polished final investment/budget plan incorporating the feedback."
        )
    )

    # Send the original draft + review comments
    refinement_message = f"""
    Original Plan:
    {draft_response}

    Reviewer Feedback:
    {review_text}

    Please generate the Investment Plan. Be professional and don't say I or we have done, directly say the recommendation. Be very concise.
    """

    # User proxy to start the new conversation
    final_response = user_proxy.initiate_chat(
        refiner_agent,
        message=refinement_message,
        auto_reply=True,
        max_turns=1)

    # Return the final polished plan
    return {"investment_recommendation": str(final_response.summary)}
