from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio

# Read GOOGLE_API_KEY into env
load_dotenv()

async def search_single_platform(platform_name, platform_url, job_role, location, llm):
    """
    Search a single job platform
    """
    task = f"""
    Go to {platform_url} and search for "{job_role}" jobs in "{location}".
    
    Extract information from the first 5-8 job postings you find:
    
    🏢 **BASIC INFO:**
    - Job Title
    - Company Name
    - Location (Remote/Hybrid/On-site)
    - Experience Level
    - Salary (if shown)
    
    💻 **TECHNICAL SKILLS:**
    - Programming Languages
    - Frameworks/Tools
    - Technologies
    - Certifications
    
    📋 **REQUIREMENTS:**
    - Years of experience
    - Education requirements
    - Language requirements (for Japanese sites)
    - Key responsibilities
    
    Format each job clearly and extract all technical keywords mentioned.
    """
    
    print(f"🔍 Searching {platform_name}...")
    agent = Agent(task=task, llm=llm)
    result = await agent.run()
    return result

async def targeted_job_search():
    """
    Multi-platform job search focusing on Japanese job market
    """
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
    
    # 🎯 CUSTOMIZE YOUR SEARCH HERE
    JOB_ROLE = "Web Developer"  # ← Change this to your target role
    LOCATION = "Tokyo"  # ← Change location or leave as "Remote"
    
    # 🇯🇵 JAPANESE JOB PLATFORMS
    japanese_platforms = [
        ("Rikunabi Next", "https://next.rikunabi.com/"),
        ("Doda", "https://doda.jp/"),
        ("Green (IT Focus)", "https://www.green-japan.com/"),
        ("Wantedly", "https://www.wantedly.com/"),
        ("Bizreach", "https://www.bizreach.jp/"),
    ]
    
    # 🌍 INTERNATIONAL PLATFORMS
    international_platforms = [
        ("LinkedIn Jobs", "https://www.linkedin.com/jobs/"),
        ("Indeed Japan", "https://jp.indeed.com/"),
        ("CareerCross", "https://www.careercross.com/"),
    ]
    
    # Combine platforms - you can comment out sections you don't want
    all_platforms = japanese_platforms + international_platforms
    
    
    print(f"🔍 Searching for {JOB_ROLE} positions in Japan...")
    print(f"📍 Location: {LOCATION}")
    print("🚀 Starting multi-platform job market research...")
    print("-" * 60)
    
    all_results = {}
    
    # Search each platform
    for platform_name, platform_url in all_platforms[:4]:  # Limit to first 4 to avoid rate limits
        try:
            result = await search_single_platform(platform_name, platform_url, JOB_ROLE, LOCATION, llm)
            all_results[platform_name] = result
            print(f"✅ {platform_name} search completed")
            await asyncio.sleep(2)  # Small delay between searches
        except Exception as e:
            print(f"❌ Error searching {platform_name}: {str(e)}")
            all_results[platform_name] = f"Error: {str(e)}"
    
    # Comprehensive analysis of all results
    combined_results = ""
    for platform, results in all_results.items():
        combined_results += f"\n\n=== {platform.upper()} RESULTS ===\n"
        combined_results += str(results)
    
    analysis_task = f"""
    Analyze job search results for "{JOB_ROLE}" positions in Japan from multiple platforms:
    
    {combined_results}
    
    Provide comprehensive analysis:
    
    📊 **JAPAN JOB MARKET OVERVIEW:**
    - Total jobs found across platforms
    - Salary ranges (in JPY if available)
    - Remote vs On-site opportunities
    - Experience levels in demand
    - Language requirements (Japanese level needed)
    
    🔥 **TOP SKILLS & TECHNOLOGIES:**
    (Count frequency across all platforms)
    - Programming Languages: [with frequency count]
    - Frameworks/Libraries: [with frequency count]
    - Cloud Platforms: [with frequency count]
    - Tools & Software: [with frequency count]
    - Soft Skills: [with frequency count]
    
    🏢 **COMPANY INSIGHTS:**
    - Types of companies hiring (startups vs enterprises)
    - Japanese vs international companies
    - Industries represented
    - Company sizes
    
    🎯 **KEYWORD PAIRS FOR APPLICATIONS:**
    (Most effective combinations for Japanese job market)
    - Technical combinations: (e.g., "React + TypeScript", "AWS + Docker")
    - Skill pairs: (e.g., "Leadership + Communication", "API + Microservices")
    - Japan-specific terms: (e.g., "Business level Japanese", "Global team")
    
    🇯🇵 **JAPAN-SPECIFIC INSIGHTS:**
    - Japanese language requirements
    - Work culture expectations
    - Visa sponsorship availability
    - Best platforms for foreigners
    - Salary comparison with global standards
    
    💡 **ACTIONABLE INSIGHTS:**
    - Most in-demand skills to learn
    - Japanese language level needed
    - Best platforms to focus on
    - Profile optimization for Japanese market
    - Networking opportunities
    
    🚀 **NEXT STEPS FOR JAPAN JOB MARKET:**
    - Skills to prioritize learning
    - Language study recommendations
    - Cultural preparation tips
    - Application strategy suggestions
    
    Make this practical and actionable for someone targeting the Japanese job market!
    """
    
    print("📊 Analyzing Japan job market results...")
    analysis_agent = Agent(task=analysis_task, llm=llm)
    final_analysis = await analysis_agent.run()
    
    print("\n" + "="*80)
    print("🇯🇵 JAPAN JOB MARKET ANALYSIS RESULTS")
    print("="*80)
    print(final_analysis)
    print("="*80)
    
    return final_analysis

if __name__ == "__main__":
    asyncio.run(targeted_job_search())
