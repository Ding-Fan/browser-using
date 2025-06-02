from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
from markdown_extractor import extract_and_save_markdown
import json

# Read GOOGLE_API_KEY into env
load_dotenv()

models =  {
    "gemini": {
        "2.5-flash": "gemini-2.5-flash",
        "2.0-flash-exp": "gemini-2.0-flash-exp",
        "2.0-flash": "gemini-2.0-flash",
        "2.0-flash-lite": "gemini-2.0-flash-lite",
        "1.5-pro": "gemini-1.5-pro",
        "1.5-flash": "gemini-1.5-flash",
        "1.5": "gemini-1.5",
    }
}

# Initialize the model
llm = ChatGoogleGenerativeAI(model=models["gemini"]["2.0-flash"])
# not working
# llm = ChatGoogleGenerativeAI(model=models["gemini"]["2.0-flash-lite"])

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
        browse_instruction = f"Browse this URL {urls_text}, get the information of that company, "
    else:
        urls_text = "\n".join([f"- {url}" for url in urls])
        browse_instruction = f"Browse these URLs for {company_name}:\n{urls_text}\n\n for each of the URL: pay attention to the company culture, values, and mission etc. also look for their products, services, and any unique aspects, and randomly browse some pages to get a good understanding and comprehensive information of the company."

    agent = Agent(
        task=(
            f"I'm a student. I'm writing my resume in Japanese. "
            f"Here is my personal information and background:\n\n{about_me}\n\n"
            f"Please follow these instructions for writing 志望動機:\n\n{motivation_instructions}\n\n"
            f"{browse_instruction}"
            f"Based on both my background and the company information, "
            f"help me write 志望動機 in Japanese for it. "
            f"You should create short, medium, and long versions.\n"
            f"Output the result in markdown format, with clear section headers for each version."
        ),
        llm=llm,
    )
    result = await agent.run()
    print(result)

    # Use the reusable extractor to save markdown
    extract_and_save_markdown(result)

asyncio.run(main())