from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
from markdown_extractor import extract_and_save_markdown
import json
import os
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

# Read environment variables
load_dotenv()

# LLM Configuration - Change these two lines to switch models
PROVIDER = "deepseek"  # Options: "google", "deepseek"
MODEL = "reasoner"         # For google: "2.5-flash", "2.0-flash-exp", "2.0-flash", "1.5-pro", "1.5-flash", "1.5"
                       # For deepseek: "chat"

def get_llm(provider: str, model: str):
    """Initialize and return the specified LLM model"""
    
    if provider == "google":
        # Google Gemini models configuration
        google_models = {
            "2.5-flash": "gemini-2.5-flash",
            "2.0-flash-exp": "gemini-2.0-flash-exp", 
            "2.0-flash": "gemini-2.0-flash",
            "2.0-flash-lite": "gemini-2.0-flash-lite",
            "1.5-pro": "gemini-1.5-pro",
            "1.5-flash": "gemini-1.5-flash",
            "1.5": "gemini-1.5",
        }
        
        if model not in google_models:
            raise ValueError(f"Unsupported Google model: {model}. Available options: {list(google_models.keys())}")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        return ChatGoogleGenerativeAI(model=google_models[model])
    
    elif provider == "deepseek":
        # https://api-docs.deepseek.com/quick_start/pricing/
        # DeepSeek models configuration
        deepseek_models = {
            "chat": "deepseek-chat",
            "reasoner": "deepseek-reasoner",
        }
        
        if model not in deepseek_models:
            raise ValueError(f"Unsupported DeepSeek model: {model}. Available options: {list(deepseek_models.keys())}")
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        return ChatDeepSeek(
            base_url='https://api.deepseek.com/v1', 
            model=deepseek_models[model], 
            api_key=SecretStr(api_key)
        )
    
    else:
        raise ValueError(f"Unsupported provider: {provider}. Available options: ['google', 'deepseek']")

# Initialize the selected LLM
llm = get_llm(PROVIDER, MODEL)



import asyncio

async def main():

    # Read about-me information
    try:
        with open("input/about-me.md", "r", encoding="utf-8") as f:
            about_me = f.read()
    except FileNotFoundError:
        about_me = "No personal information provided."

    # Read 志望動機 instructions
    try:
        with open("input/志望動機_instructions.md", "r", encoding="utf-8") as f:
            motivation_instructions = f.read()
    except FileNotFoundError:
        motivation_instructions = "No specific instructions provided for 志望動機 writing."

    # Read company/URL data from JSON file
    try:
        with open("input/companies.json", "r", encoding="utf-8") as f:
            companies_data = json.load(f)
    except FileNotFoundError:
        print("Error: input/companies.json file not found. Please create the file with company data.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in input/companies.json.")
        return
    
    # Get the current working company
    if "working" not in companies_data:
        print("Error: No 'working' company specified in companies.json.")
        return
    
    current_company = companies_data["working"]
    
    # Check if the company exists in backlog
    if "backlog" not in companies_data or current_company not in companies_data["backlog"]:
        print(f"Error: Company '{current_company}' not found in backlog.")
        if "backlog" in companies_data:
            print(f"Available companies: {list(companies_data['backlog'].keys())}")
        return
    
    company_info = companies_data["backlog"][current_company]
    company_name = company_info.get("name", current_company)
    
    # Handle URLs - support both single URL and multiple URLs
    urls = company_info.get("url", company_info.get("urls", []))
    
    if isinstance(urls, str):
        urls = [urls]
    elif not isinstance(urls, list):
        print(f"Error: Invalid URL format for company '{company_name}'.")
        return
    
    if not urls:
        print(f"Error: No URLs provided for company '{company_name}'.")
        return
    
    # Format URLs for the task
    if len(urls) == 1:
        urls_text = urls[0]
        browse_instruction = f"Browse this URL: {urls_text}\n\nResearch the company thoroughly by exploring:"
    else:
        urls_text = "\n".join([f"- {url}" for url in urls])
        browse_instruction = f"Browse these URLs for {company_name}:\n{urls_text}\n\nResearch the company thoroughly by exploring:"
    
    browse_instruction += (
        "\n• Company culture, values, and mission"
        "\n• Products, services, and unique features"
        "\n• Recent news, achievements, or initiatives"
        "\n• Team, leadership, and company size"
        "\n\n**BROWSING LIMITS (to save tokens):**"
        "\n• Maximum 8 pages total (including provided URLs)"
        "\n• Ensure all provided URLs are visited"
        "\n• Browse two additional new pages to get a broader view"
        "\n• Spend no more than 60 seconds per page"
        "\n• Focus only on key information, skip detailed content"
        "\n• Only one long articles or blog post is allowed to read in detail"
    )

    agent = Agent(
        task=(
            f"I'm a student. I'm writing my resume in Japanese. "
            f"Here is my personal information and background:\n\n{about_me}\n\n"
            f"Please follow these instructions for writing 志望動機:\n\n{motivation_instructions}\n\n"
            f"{browse_instruction}"
            f"Based on both my background and the company information, "
            f"help me write 志望動機 in Japanese for it. "
            f"You should create short, medium, and long versions.\n"
            f"At the end, provide a Analyse section of the company.\n"
            f"Output the result in markdown format, with clear section headers for each version."
        ),
        llm=llm,
    )
    result = await agent.run()
    print(result)

    # Use the reusable extractor to save markdown
    extract_and_save_markdown(result)

asyncio.run(main())