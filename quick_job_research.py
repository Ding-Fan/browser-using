from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio

# Read GOOGLE_API_KEY into env
load_dotenv()

async def targeted_job_search():
    """
    Focused job search with keyword extraction - perfect for getting started
    """
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
    
    # 🎯 CUSTOMIZE YOUR SEARCH HERE
    JOB_ROLE = "Data Scientist"  # ← Change this to your target role
    LOCATION = "Remote"  # ← Change location or leave as "Remote"
    
    task = f"""
    I want to research {JOB_ROLE} job opportunities. Please do the following:
    
    1. **Go to LinkedIn Jobs** (https://www.linkedin.com/jobs/)
    2. **Search for:** "{JOB_ROLE}" jobs in "{LOCATION}"
    3. **Analyze the first 10 job postings** you find
    
    For each job, extract:
    🏢 **BASIC INFO:**
    - Job Title
    - Company Name
    - Location (Remote/Hybrid/On-site)
    - Experience Level
    - Salary (if shown)
    
    💻 **TECHNICAL SKILLS MENTIONED:**
    - Programming Languages
    - Frameworks/Tools
    - Technologies
    - Certifications requested
    
    📋 **REQUIREMENTS:**
    - Years of experience
    - Education requirements
    - Key responsibilities
    
    After analyzing all jobs, provide:
    
    📊 **SUMMARY & KEYWORDS:**
    
    **Most Mentioned Skills** (with count):
    - Programming Languages: [list with frequency]
    - Tools/Frameworks: [list with frequency] 
    - Cloud Platforms: [list with frequency]
    - Soft Skills: [list with frequency]
    
    **Keyword Pairs for Resume/Applications:**
    - [skill1] + [skill2]
    - [tool] + [methodology]
    - [technology] + [industry term]
    
    **Market Insights:**
    - Average experience required
    - Salary ranges found
    - Remote work percentage
    - Top hiring companies
    
    **Action Items:**
    - Top 3 skills to learn/improve
    - Best platforms to apply on
    - Profile optimization tips
    
    Make this actionable and specific for someone looking for {JOB_ROLE} roles!
    """
    
    print(f"🔍 Searching for {JOB_ROLE} positions...")
    print(f"📍 Location: {LOCATION}")
    print("🚀 Starting automated job market research...")
    print("-" * 60)
    
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    
    print("\n" + "="*80)
    print("🎯 JOB MARKET ANALYSIS RESULTS")
    print("="*80)
    print(result)
    print("="*80)
    
    return result

if __name__ == "__main__":
    asyncio.run(targeted_job_search())
