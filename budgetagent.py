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
    "temperature": 0.3,
}

def analyze_budget(user_profile):
    user_proxy = UserProxyAgent(
        name="User",
        llm_config=llm_config,
        code_execution_config=False,
        human_input_mode="NEVER"
    )

    budget_agent = AssistantAgent(
        name="BudgetPlannerAgent",
        llm_config=llm_config,
        system_message=("You are a professional personal finance assistant. "
            "Your task is to take the user's summary of their bank statement. "
            "Analyze and create a detailed, practical budgeting plan that helps them achieve their short-term goal within the desired timeframe, "
            "while building good financial habits for the long term. "
            "Prioritize covering essential recurring expenses first, then allocate savings, and recommend specific areas for reducing discretionary spending. "
            "Provide actionable advice, be encouraging, and keep your recommendations succinct."
        )
    )

    message = f"""
    User Financial Information:
    - Short-Term Goal: {user_profile.get('short_term_goal', 'Not provided')}
    - Long-Term Goal: {user_profile.get('long_term_goal', 'Not provided')}
    - Bank Summary: {user_profile.get('bank_summary', 'No bank summary')}

    Create a practical budget plan.
    """

    response = user_proxy.initiate_chat(
        budget_agent,
        message=message,
        auto_reply=True,
        max_turns=1
    )

    return {"short_term_plan": str(response.summary)}

