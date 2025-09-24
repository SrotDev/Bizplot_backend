import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType
import pdfplumber
import pytesseract
import requests
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
from queue import Queue

set_of_gemini_api = [
    "AIzaSyAcsgnomAm9XnKo3uLaKSbY0qF8Lo_i9ks",
    "AIzaSyA7Lj9jKzVX9J6foNagX5GrMtqAd5WRXzU"
]

set_of_google_api = [
    ["AIzaSyAMsVYBUyIFaFQ2XjYvRocppZTZUoe5iEM", "01945ddf4aba34ab5"],
]

def extract_text_from_pdf(pdf_path = "pitchdeck.pdf") -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                image = page.to_image(resolution=300)
                text = pytesseract.image_to_string(image.original)
            if text:
                full_text += text + "\n"
    return full_text




def save_json(data: str, filename: str = "output.json") -> str:
    with open(filename, "w") as f:
        f.write(data)
    return f"JSON saved to {filename}"


def json_parser(response_text: str):
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            parsed_json = json.loads(json_str)
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", e)
    else:
        print("No JSON found in response")



#llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)




 

def without_agent(prompt : str) :
    os.environ["GOOGLE_API_KEY"] = set_of_gemini_api.pop()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    set_of_gemini_api.append(os.environ["GOOGLE_API_KEY"])
    return llm.invoke(prompt)

 

previous_ideas = [
    {
        "startup_idea": "AI-Powered Debt Management Platform",
        "summary": "An AI-driven platform that analyzes user debt profiles, negotiates with creditors for lower interest rates or payment plans, and provides personalized strategies for debt repayment.",
        "quick_stats": {
            "market_size": "$3.5B",
            "growth_potential": "High",
            "target_audience": "Young professionals and individuals struggling with debt management."
        },
        "model_archetype": "AI-powered financial advisor and debt negotiator"
    }
]

def chat_bot(data):
    # Build conversation history for the prompt
    history = ""
    for convo in data["prev_response"]:
        if convo["Receiver"] == "ai":
            history += f"User: {convo['Message']}\n"
        else:
            history += f"AI: {convo['Message']}\n"

    # Compose the prompt
    prompt = f"""
You are a chatbot assistant for a startup.
Base all answers strictly on the following startup idea:
{data["idea"]}

Conversation history:
{history}

Current question: {data['current_q']}

Instructions:
- Only answer questions directly related to the provided startup idea.
- Do not make up answers or add extra information.
- Keep your response brief and relevant.
- Do not include explanations, thoughts, or formatting.
- Return only the answer.
"""

    # Get the answer from the LLM
    cur_response = without_agent(prompt)
    answer = cur_response.content.strip()

    # Update the conversation history
    updated_response = data["prev_response"] + [
        {"Receiver": "ai", "Message": data["current_q"]},
        {"Receiver": "user", "Message": answer}
    ]

    # Return as JSON
    print(json.dumps(updated_response, indent=2))
    return json.dumps(updated_response, indent=2)

# Example usage:
#chat_bot(dummy_chatbot_data)

# Define dummy_chatbot_data first
dummy_chatbot_data = {
    "idea": json.dumps([
        {
            "startup_idea": "AI-Powered Debt Management Platform",
            "summary": "An AI-driven platform that analyzes user debt profiles, negotiates with creditors for lower interest rates or payment plans, and provides personalized strategies for debt repayment.",
            "quick_stats": {
                "market_size": "$3.5B",
                "growth_potential": "High",
                "target_audience": "Young professionals and individuals struggling with debt management."
            },
            "model_archetype": "AI-powered financial advisor and debt negotiator"
        }
    ], indent=2),
    "prev_response": [
        {"Receiver": "ai", "Message": "What is the main benefit of the debt management platform?"},
        {"Receiver": "user", "Message": "It helps users negotiate with creditors and provides personalized repayment strategies."},
        {"Receiver": "ai", "Message": "Can it help with budgeting?"},
        {"Receiver": "user", "Message": "Yes, it analyzes your spending and suggests budgeting strategies."}
    ],
    "current_q": "Does the platform support automated payments to creditors?"
}


api_key_queue = Queue()
for key in set_of_gemini_api:
    api_key_queue.put(key)




# if __name__ == "__main__":
#     results = []
#    with ThreadPoolExecutor(max_workers=2) as executor:
#         futures = [executor.submit(process_user_request, ui, 2) for ui in user_inputs]
#         for future in as_completed(futures):
#             results.append(future.result())
#     for r in results:
#         print("\nFINAL OUTPUT:\n", r)


def chat_bot(data):
    # Build conversation history for the prompt
    history = ""
    for convo in data["prev_response"]:
        if convo["Receiver"] == "ai":
            history += f"User: {convo['Message']}\n"
        else:
            history += f"AI: {convo['Message']}\n"

    # Compose the prompt
    prompt = f"""
You are a chatbot assistant for a startup.
Base all answers strictly on the following startup idea:
{data["idea"]}

Conversation history:
{history}

Current question: {data['current_q']}

Instructions:
- Only answer questions directly related to the provided startup idea.
- Do not make up answers or add extra information.
- Keep your response brief and relevant.
- Do not include explanations, thoughts, or formatting.
- Return only the answer.
"""

    # Get the answer from the LLM
    cur_response = without_agent(prompt)
    answer = cur_response.content.strip()

    # Update the conversation history
    updated_response = data["prev_response"] + [
        {"Receiver": "ai", "Message": data["current_q"]},
        {"Receiver": "user", "Message": answer}
    ]


    # Return as JSON
    print(json.dumps(updated_response, indent=2))
    return updated_response
    # return json.dumps(updated_response, indent=2)

#chat_bot(dummy_chatbot_data)



def comparison(data):
    prompt = f"""
You are a startup idea evaluator.
Here are Two ideas to compare:
Idea 1:
{data["idea1"]}
Idea 2:
{data["idea2"]}

Compare the two ideas across the following categories:
- Market Depth
- Audience Breadth
- Business Model Richness
- Risk Awareness
- Traction Signals
- Roadmap Clarity

For each category, assign a score to Idea 1 and Idea 2 (0 if evenly matched), give a verdict ("Tie", "Idea 1", or "Idea 2"), and add a brief comment.

After all categories, provide the total score for each idea and a final verdict.

Return strictly valid JSON in this format:

{{
  "comparison": [
    {{
      "category": "Market Depth",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }},
    {{
      "category": "Audience Breadth",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }},
    {{
      "category": "Business Model Richness",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }},
    {{
      "category": "Risk Awareness",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }},
    {{
      "category": "Traction Signals",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }},
    {{
      "category": "Roadmap Clarity",
      "idea_1_score": 0,
      "idea_2_score": 0,
      "verdict": "Tie",
      "comment": "Both ideas are evenly matched here."
    }}
  ],
  "total_score": {{
    "idea_1": 0,
    "idea_2": 0
  }},
  "final_verdict": {{
    "winner": "No Clear Winner",
    "comment": "Both ideas are balanced overall. Consider qualitative differentiation (brand, UX, defensibility)."
  }}
}}

Do not include any explanations, markdown, or extra text. Only return the JSON.
"""
    response = without_agent(prompt)
    print(json_parser(response.content))
    return json_parser(response.content)

dummy_comparison_data = {
    "idea1": json.dumps({
        "startup_idea": "AI-Powered Debt Management Platform",
        "summary": "A platform that uses AI to analyze user debt profiles, negotiate with creditors, and provide personalized repayment strategies. Integrates with financial accounts for real-time tracking.",
        "quick_stats": {
            "market_size": "$3.5B",
            "growth_potential": "High",
            "target_audience": "Young professionals, individuals with multiple debts"
        },
        "model_archetype": "AI-powered financial advisor and negotiator",
        "features": [
            "Automated debt analysis",
            "Creditor negotiation engine",
            "Personalized repayment plans",
            "Progress tracking dashboard",
            "Financial wellness tips"
        ],
        "traction": {
            "active_users": 12000,
            "monthly_growth": "12%",
            "partnerships": ["CreditFix", "DebtRelief Inc."]
        },
        "risks": [
            "Regulatory compliance",
            "Data privacy concerns",
            "Dependence on third-party financial APIs"
        ],
        "roadmap": [
            {"phase": "Q1 2025", "milestone": "Launch beta version"},
            {"phase": "Q2 2025", "milestone": "Integrate with top 5 banks"},
            {"phase": "Q3 2025", "milestone": "Add AI negotiation module"},
            {"phase": "Q4 2025", "milestone": "Expand to EU market"}
        ]
    }, indent=2),
    "idea2": json.dumps({
        "startup_idea": "Smart Farming Platform",
        "summary": "A cloud-based platform using IoT sensors and AI analytics to help farmers optimize crop yields, reduce costs, and monitor field conditions in real time.",
        "quick_stats": {
            "market_size": "$2.1B",
            "growth_potential": "Medium",
            "target_audience": "Commercial farmers, agri-businesses"
        },
        "model_archetype": "AgriTech SaaS",
        "features": [
            "Soil and weather sensors",
            "AI-powered yield prediction",
            "Automated irrigation control",
            "Mobile app for farm management",
            "Marketplace for farm supplies"
        ],
        "traction": {
            "active_farms": 500,
            "monthly_growth": "8%",
            "partnerships": ["AgroTech", "GreenFields"]
        },
        "risks": [
            "Hardware reliability",
            "Farmer adoption rate",
            "Seasonal market fluctuations"
        ],
        "roadmap": [
            {"phase": "Q1 2025", "milestone": "Deploy pilot farms"},
            {"phase": "Q2 2025", "milestone": "Release mobile app"},
            {"phase": "Q3 2025", "milestone": "Integrate supply marketplace"},
            {"phase": "Q4 2025", "milestone": "Expand to new regions"}
        ]
    }, indent=2)
}

