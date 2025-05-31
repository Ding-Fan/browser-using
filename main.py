from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv

# Read GOOGLE_API_KEY into env
load_dotenv()

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')

import asyncio

async def main():
    agent = Agent(
        task="I'm a student. From this URL https://curriculum-rust-one.vercel.app/ , according current time, tell me what is the course right now.",
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())