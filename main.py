from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
from markdown_extractor import extract_and_save_markdown

# Read GOOGLE_API_KEY into env
load_dotenv()

models =  {
    "gemini": {
        "2.0-flash-exp": "gemini-2.0-flash-exp",
        "2.0-flash": "gemini-2.0-flash",
        "1.5-pro": "gemini-1.5-pro",
        "1.5-flash": "gemini-1.5-flash",
        "1.5": "gemini-1.5",
        "1.0-pro": "gemini-1.0-pro",
        "1.0-flash": "gemini-1.0-flash",
    }
}

# Initialize the model
llm = ChatGoogleGenerativeAI(model=models["gemini"]["2.0-flash"])

import asyncio

async def main():
    # url = "https://baristagame.com/277de22fe896491097a20a136376882e"
    # url = "https://autoro.io/"
    url = "https://everforth.co.jp/"
    agent = Agent(
        task=(
            f"I'm a student. I'm writing my resume in Japanese. "
            f"Browse this URL {url}, get the information of that company, "
            f"pay attention to the company culture, values, and mission etc."
            f"also look for their products, services, and any unique aspects "
            f"randomly browse some pages to get a good understanding of the company. "
            f"and help me write 志望動機 in Japanese for it. "
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