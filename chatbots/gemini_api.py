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


def search_web(query: str, num_results: int = 3) -> str:
    GOOGLE_API_KEY, CX = set_of_google_api.pop()
    print(f"Using GOOGLE_API_KEY: {GOOGLE_API_KEY}, CX: {CX}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": CX,
        "q": query,
        "num": num_results
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        snippets = []
        for i, item in enumerate(data.get("items", [])):
            snippet = item.get("snippet") or item.get("title")
            snippets.append(f"{i+1}. {snippet}")
        print(snippets)
        return "\n".join(snippets) if snippets else "[No results found]"
    except Exception as e:
        return f"[Search failed: {str(e)}]"
    finally:
        set_of_google_api.append([GOOGLE_API_KEY, CX])



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
tools = [
    Tool(name="WebSearch", func=search_web, description="Search the web for information."),
    #Tool(name="PDFParser", func=extract_text_from_pdf, description="Extract text from a PDF file."),
    Tool(name="FileSaver", func=save_json, description="Save JSON string to a file.")
]


#llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)


def get_required_tools(agent_type = 1):
    if agent_type == 1:
        return [
            Tool(name="WebSearch", func=search_web, description="Search the web for information."),
           
        ]
    elif agent_type == 2:
        pass
        return [
            Tool(name="WebSearch", func=search_web, description="Search the web for information."),
        ]

#6 agents will be there

def get_agent(agent_type = 1, verbose = True,temperature = 0):
    os.environ["GOOGLE_API_KEY"] = set_of_gemini_api.pop()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    return initialize_agent(
        get_required_tools(agent_type),
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
   

def without_agent(prompt : str) :
    os.environ["GOOGLE_API_KEY"] = set_of_gemini_api.pop()
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    set_of_gemini_api.append(os.environ["GOOGLE_API_KEY"])
    return llm.invoke(prompt)



def get_prompts( user_input,agent_type = 1,has_pdf = False):
    if agent_type == 1 : 
        if not has_pdf:
            return f"""
            You are a startup idea generator.

            User Input:
            Title: {user_input['title']}
            Short Description: {user_input['short_description']}
            Budget: {user_input['budget_range']}
            Category: {user_input['product_category']}
            Target Market: {user_input['target_market']}

            Task:
            Generate 3 startup ideas **and return strictly valid JSON only**.
            Do **NOT** include explanations, thoughts, reasoning, or extra text.
            Do **NOT** format with backticks or markdown.
            Return JSON in the following structure:

            {{
            "ideas": [
                {{
                "startup_idea": "...",
                "summary": "...",
                "quick_stats": {{
                    "market_size": "...",
                    "growth_potential": "...",
                    "target_audience": "..."
                }},
                "model_archetype": "..."
                }},
                ...  # 3 ideas
            ],
            "total_used_tokens_for_gemini_api": "(number)"
            }}            
            """
        else:
            return f"""
            You are a startup idea generator.

            User Input:
            Title: {user_input['title']}
            Short Description: {user_input['short_description']}
            Budget: {user_input['budget_range']}
            Category: {user_input['product_category']}
            Target Market: {user_input['target_market']}
            PDF summary : {user_input['business_plan']}

            Task:
            Generate 3 startup ideas **and return strictly valid JSON only**.
            Do **NOT** include explanations, thoughts, reasoning, or extra text.
            Do **NOT** format with backticks or markdown.
            Return JSON in the following structure:

            {{
            "ideas": [
                {{
                "startup_idea": "...",
                "summary": "...",
                "quick_stats": {{
                    "market_size": "...",
                    "growth_potential": "...",
                    "target_audience": "..."
                }},
                "model_archetype": "..."
                }},
                ...  # 3 ideas
            ],
            "total_used_tokens_for_gemini_api": "(number)"
            }}            
            """


        
    elif agent_type == 2:
        return f"""
            You are a startup business strategist AI.

            User Input:
                Title: {user_input['startup_idea']}
                Short Description: {user_input['summary']}
                Budget: {user_input['budget_range']}
                Target Audience: {user_input['target_audience']}
                Target Market: {user_input['target_market']}
                Model Archetype: {user_input['model_archetype']}

            Task:
            Based on the provided startup idea and details, generate a comprehensive business model, roadmap, market & competitor analysis, and chart in **Chart.js-ready format**.

            Output **strictly valid JSON only** (no markdown, no commentary, no explanations).

            JSON Structure:

            {{
                "business_model": {{
                    "revenue_streams": ["realistic revenue sources"],
                    "cost_structure": ["main costs with realistic estimates"],
                    "key_partnerships": ["strategic partnerships"],
                    "customer_segments": ["types of customers"]
                }},
                "roadmap": [
                    {{"phase": "Q1 2025", "milestone": "milestone text"}},
                    {{"phase": "Q2 2025", "milestone": "milestone text"}},
                    {{"phase": "Q3 2025", "milestone": "milestone text"}},
                    {{"phase": "Q4 2025", "milestone": "milestone text"}}
                ],
                "chart": {{
                    "user_growth": {{  
                        "type": "line",
                        "data": {{
                            "labels": ["Q1", "Q2", "Q3", "Q4"],
                            "datasets": [{{"label": "Active Users", "data": [1000, 5000, 15000, 30000]}}]
                        }}
                    }},
                    "revenue_vs_expenses": {{
                        "type": "bar",
                        "data": {{
                            "labels": ["Q1", "Q2", "Q3", "Q4"],
                            "datasets": [
                                {{"label": "Revenue", "data": [5000, 15000, 30000, 60000]}},
                                {{"label": "Expenses", "data": [4000, 8000, 20000, 35000]}}
                            ]
                        }}
                    }},
                    "market_segments": {{
                        "type": "pie",
                        "data": {{
                            "labels": ["Young Professionals", "Freelancers", "Small Businesses"],
                            "datasets": [{{"label": "Market Share (%)", "data": [50, 30, 20]}}]
                        }}
                    }},
                    "retention_rate": {{
                        "type": "doughnut",
                        "data": {{
                            "labels": ["Retained", "Churned"],
                            "datasets": [{{"label": "User Retention", "data": [80, 20]}}]
                        }}
                    }},
                    "funding_allocation": {{
                        "type": "radar",
                        "data": {{
                            "labels": ["Marketing", "R&D", "Operations", "Hiring", "Infrastructure"],
                            "datasets": [{{"label": "Allocation (%)", "data": [30, 25, 20, 15, 10]}}]
                        }}
                    }}
                }},
                "market_analysis": {{
                    "total_addressable_market": "estimated TAM in $",
                    "serviceable_available_market": "estimated SAM in $",
                    "growth_rate": "CAGR %",
                    "trends": ["list key market trends"],
                    "target_audience": ["list primary customer segments"]
                }},
                "competitor_analysis": [
                    {{
                        "name": "Competitor 1",
                        "products_services": ["main offerings"],
                        "market_share": "percentage",
                        "strengths": ["key strengths"],
                        "weaknesses": ["key weaknesses"]
                    }},
                    {{
                        "name": "Competitor 2",
                        "products_services": ["main offerings"],
                        "market_share": "percentage",
                        "strengths": ["key strengths"],
                        "weaknesses": ["key weaknesses"]
                    }},
                    {{
                        "name": "Competitor 3",
                        "products_services": ["main offerings"],
                        "market_share": "percentage",
                        "strengths": ["key strengths"],
                        "weaknesses": ["key weaknesses"]
                    }}
                ],
                "product_service": {{
                    "products": ["list products/services"],
                    "features": ["list key features"],
                    "unique_value_proposition": "concise UVP statement"
                }},
                "go_to_market": {{
                    "channels": ["list distribution channels"],
                    "strategies": ["list marketing/sales strategies"],
                    "launch_plan": "brief launch plan description"
                }},
                "traction": {{
                    "key_metrics": ["list measurable metrics"],
                    "milestones": ["list achieved milestones"]
                }},
                "financial_projection": {{
                    "revenue_forecast": [0, 0, 0, 0],
                    "expenses_forecast": [0, 0, 0, 0],
                    "profit_forecast": [0, 0, 0, 0]
                }},
                "risks_opportunities": {{
                    "risks": ["list potential risks"],
                    "opportunities": ["list potential opportunities"]
                }},
                "ask_funding": {{
                    "amount": 0,
                    "use_of_funds": ["list of fund allocations"]
                }},


                "data_for_montecarlo_simulation": {{
                    "production_cost": {{
                    "min": "(number)", It will be per unit cost
                    "max": "(number)"  It will be per unit cost
                    }},
                    "selling_price": {{
                    "min": "(number)", It will be per unit price
                    "max": "(number)"  It will be per unit price
                    }},
                    "demand": {{
                    "min": "(number)", It will be demand of total units in six months
                    "max": "(number)"  It will be demand of total units in six months
                    }}
                }},
                "total_used_tokens_for_gemini_api": "(number)"
            }}

            Rules:
            - Fill all fields with realistic values based on the startup idea.
            - Keep the chart structure exactly as given.
            - All numeric fields in chart must be numbers (no quotes).
            - Do not include any extra text, commentary, or markdown.
            """
    elif agent_type == 3:
        return f"""
            You are a startup idea generator.

            Title: {user_input['title']}
            Short Description: {user_input['short_description']}

            Previous User Inputs:
                Budget: {user_input['budget_range']}
                Category: {user_input['product_category']}
                Target Market: {user_input['target_market']}

            Updated Inputs:
                Budget: {user_input['new_budget_range']}
                Category: {user_input['new_product_category']}
                Target Market: {user_input['new_target_market']}

            Previously Generated Ideas:
            {user_input['previous_ideas']}

            Task:
            - Compare the new inputs with the previous ones.
            - If the changes are significant, generate a new set of 3 startup ideas aligned with the new criteria.
            - If the changes are minor, refine the previous ideas to better fit the updated inputs.
            - For each idea, provide:
                - startup_idea
                - summary
                - quick_stats: {{market_size, growth_potential, target_audience}}
                - model_archetype
            - Return strictly valid JSON only.
            - Do NOT include explanations, commentary, markdown, or extra text.

            JSON Structure:
            {{
                "ideas": [
                    {{
                        "startup_idea": "...",
                        "summary": "...",
                        "quick_stats": {{
                            "market_size": "...",
                            "growth_potential": "...",
                            "target_audience": "..."
                        }},
                        "model_archetype": "..."
                    }},
                    ...  # 3 ideas
                ],
                "total_used_tokens_for_gemini_api": "(number)"
            }}
            """

        

# Prepare a thread-safe queue of API keys
# api_key_queue = Queue()
# for key in set_of_gemini_api:
#     api_key_queue.put(key)

# def process_user_request(user_input,agent_type = 1):
#     api_key = api_key_queue.get()  # Get an available key
#     os.environ["GOOGLE_API_KEY"] = api_key
#     #print(f"START: {user_input['title']} with API_KEY {api_key} at {datetime.now().strftime('%H:%M:%S.%f')}")
#     #time.sleep(0.)
#     task = get_prompts(user_input, agent_type=3, has_pdf=False)
#     res = without_agent(task)
#    # print(f"END: {user_input['title']} at {datetime.now().strftime('%H:%M:%S.%f')}")
#     api_key_queue.put(api_key) 
#     print(json_parser(res.content)) # Return the key to the queue
#     return json_parser(res.content)


class GeminiAPIManager:
    api_key_queue = None

    @staticmethod
    def _init_queue():
        if GeminiAPIManager.api_key_queue is None:
            GeminiAPIManager.api_key_queue = Queue()
            for key in set_of_gemini_api:
                GeminiAPIManager.api_key_queue.put(key)

    @staticmethod
    def process_user_request(user_input, agent_type=1, has_pdf=False):
        GeminiAPIManager._init_queue()
        api_key = GeminiAPIManager.api_key_queue.get()  # Get an available key
        os.environ["GOOGLE_API_KEY"] = api_key
        #print(f"START: {user_input['title']} with API_KEY {api_key} at {datetime.now().strftime('%H:%M:%S.%f')}")
        #time.sleep(0.)
        task = get_prompts(user_input, agent_type=agent_type, has_pdf=has_pdf)
        res = without_agent(task)
    # print(f"END: {user_input['title']} at {datetime.now().strftime('%H:%M:%S.%f')}")
        GeminiAPIManager.api_key_queue.put(api_key)
        print(json_parser(res.content)) # Return the key to the queue


        return json.loads(json_parser(res.content))

# Example: list of user inputs
#user_inputs = [
    
#    {
#        "startup_idea": "Smart Farming",
#        "summary": "Precision agriculture with IoT and AI.",
#        "budget_range": "$40,000",
#        "target_audience": "Farmers",
#        "model_archetype": "AgriTech Platform"
#    }
#]
#  
user_inputs =[ {
    "title": "AI Fitness Coach",
    "short_description": "A virtual coach that uses AI to create personalized workout and nutrition plans.",
    "budget_range": "$25,000",
    "product_category": "Health & Fitness",
    "target_market": "Young Professionals",
    "new_budget_range": "$35,000",
    "new_product_category": "Wellness & Lifestyle",
    "new_target_market": "Remote Workers",
    "previous_ideas": [
        {
            "startup_idea": "AI Workout Planner",
            "summary": "An app that generates custom workout routines using AI.",
            "quick_stats": {
                "market_size": "$2B",
                "growth_potential": "High",
                "target_audience": "Fitness Enthusiasts"
            },
            "model_archetype": "Personal Trainer Bot"
        },
        {
            "startup_idea": "Nutrition AI",
            "summary": "AI-driven meal planning and grocery list generator.",
            "quick_stats": {
                "market_size": "$1.5B",
                "growth_potential": "Medium",
                "target_audience": "Health-Conscious Individuals"
            },
            "model_archetype": "Diet Planner Bot"
        },
        {
            "startup_idea": "Virtual Wellness Retreat",
            "summary": "Online platform for guided meditation and wellness workshops.",
            "quick_stats": {
                "market_size": "$800M",
                "growth_potential": "Growing",
                "target_audience": "Remote Workers"
            },
            "model_archetype": "Wellness Platform"
        }
    ]
}]
if __name__ == "__main__":
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(GeminiAPIManager.process_user_request, ui, 3) for ui in user_inputs]
        for future in as_completed(futures):
            results.append(future.result())
    for r in results:
        print("\nFINAL OUTPUT:\n", r)

