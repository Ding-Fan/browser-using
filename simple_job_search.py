from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import json
import datetime

# Read GOOGLE_API_KEY into env
load_dotenv()

async def search_single_platform(platform_name: str, platform_url: str, job_title: str, location: str = "", max_jobs: int = 5):
    """
    Search for jobs on a single platform
    """
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
    
    task = f"""
    Go to {platform_url}.
    Search for "{job_title}" jobs {f"in {location}" if location else ""}.
    
    For the first {max_jobs} job listings you find, extract:
    
    🎯 **JOB DETAILS:**
    - Job Title
    - Company Name  
    - Location (note if remote/hybrid)
    - Salary Range (if shown)
    - Experience Level Required
    - Posted Date
    
    💻 **TECHNICAL REQUIREMENTS:**
    - Programming Languages
    - Frameworks/Libraries
    - Tools & Platforms
    - Cloud Services
    - Databases
    
    📝 **OTHER INFO:**
    - Job Type (Full-time, Contract, etc.)
    - Benefits mentioned
    - Company size/type
    
    Format each job as:
    ---
    JOB #X:
    Title: [job title]
    Company: [company name]
    Location: [location]
    ... (other details)
    ---
    
    Be thorough in extracting technical skills and requirements.
    """
    
    print(f"🔍 Searching {platform_name}...")
    agent = Agent(task=task, llm=llm)
    results = await agent.run()
    return results

async def quick_job_search():
    """
    Quick job search across multiple platforms
    """
    # 🔧 CONFIGURE YOUR SEARCH HERE
    JOB_TITLE = "Full Stack Developer"  # Change this
    LOCATION = ""  # Leave empty for anywhere, or specify like "San Francisco"
    MAX_JOBS_PER_SITE = 5
    
    print("🚀 AUTOMATED JOB SEARCH STARTING...")
    print(f"Job Title: {JOB_TITLE}")
    print(f"Location: {LOCATION if LOCATION else 'Anywhere'}")
    print("-" * 50)
    
    # Search platforms
    platforms = [
        ("LinkedIn Jobs", "https://www.linkedin.com/jobs/"),
        ("Indeed", "https://www.indeed.com/"),
        ("AngelList (Wellfound)", "https://wellfound.com/jobs"),
    ]
    
    all_results = {}
    
    for platform_name, platform_url in platforms:
        try:
            results = await search_single_platform(
                platform_name, platform_url, JOB_TITLE, LOCATION, MAX_JOBS_PER_SITE
            )
            all_results[platform_name] = results
            print(f"✅ {platform_name} search completed")
        except Exception as e:
            print(f"❌ Error searching {platform_name}: {str(e)}")
            all_results[platform_name] = f"Error: {str(e)}"
    
    return all_results, JOB_TITLE, LOCATION

async def analyze_results(search_results, job_title, location):
    """
    Analyze all search results and create summary with keywords
    """
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
    
    # Combine all results into one text
    combined_results = ""
    for platform, results in search_results.items():
        combined_results += f"\n\n=== {platform.upper()} RESULTS ===\n"
        combined_results += str(results)
    
    analysis_task = f"""
    You are analyzing job search results for "{job_title}" positions{f" in {location}" if location else ""}.
    
    Here are the job listings found:
    {combined_results}
    
    Create a comprehensive analysis with:
    
    📊 **MARKET OVERVIEW:**
    - Total jobs found across platforms
    - Salary ranges (if available)
    - Remote vs On-site opportunities
    - Experience levels in demand
    
    🔥 **TOP SKILLS & TECHNOLOGIES:**
    (Count frequency and list most mentioned)
    - Programming Languages:
    - Frameworks/Libraries:
    - Cloud Platforms:
    - Databases:
    - Tools & Software:
    - Soft Skills:
    
    🏢 **COMPANY INSIGHTS:**
    - Types of companies hiring
    - Company sizes
    - Industries represented
    
    🎯 **KEYWORD PAIRS FOR APPLICATIONS:**
    (Most effective combinations for resumes/cover letters)
    - Technical combinations: (e.g., "React + TypeScript", "AWS + Docker")
    - Skill pairs: (e.g., "Leadership + Agile", "API + Microservices")
    - Industry terms: 
    
    💡 **ACTIONABLE INSIGHTS:**
    - Most in-demand skills to learn
    - Salary negotiation insights
    - Best platforms for this role
    - Market trends observed
    
    🚀 **NEXT STEPS RECOMMENDATIONS:**
    - Skills to prioritize learning
    - Platforms to focus applications on
    - Profile optimization suggestions
    
    Make this practical and actionable for job seekers!
    """
    
    print("📊 Analyzing results and generating insights...")
    agent = Agent(task=analysis_task, llm=llm)
    analysis = await agent.run()
    return analysis

async def main():
    """
    Main execution function
    """
    try:
        # Step 1: Search for jobs
        search_results, job_title, location = await quick_job_search()
        
        # Step 2: Analyze results
        analysis = await analyze_results(search_results, job_title, location)
        
        # Step 3: Save results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "search_date": datetime.datetime.now().isoformat(),
            "job_title": job_title,
            "location": location,
            "raw_results": search_results,
            "analysis": analysis
        }
        
        filename = f"job_analysis_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # Step 4: Display results
        print("\n" + "="*80)
        print("🎉 JOB SEARCH ANALYSIS COMPLETE!")
        print("="*80)
        print(analysis)
        print("\n" + "="*80)
        print(f"📁 Full results saved to: {filename}")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        print("Check your internet connection and API configuration.")

if __name__ == "__main__":
    asyncio.run(main())
