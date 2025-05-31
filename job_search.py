from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import json
import datetime
from typing import List, Dict, Any, Optional

# Read GOOGLE_API_KEY into env
load_dotenv()

class JobSearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
        self.search_results = []
    
    async def search_jobs(self, job_title: str, location: str = "", remote_ok: bool = True, max_jobs: int = 10):
        """
        Search for jobs on multiple platforms and return structured results
        """
        
        # LinkedIn job search
        linkedin_task = f"""
        Go to LinkedIn Jobs (https://www.linkedin.com/jobs/).
        Search for "{job_title}" jobs {f"in {location}" if location else ""}.
        {"Include remote jobs in the search." if remote_ok else ""}
        
        For the first {max_jobs} job listings, extract the following information:
        1. Job title
        2. Company name
        3. Location (including if it's remote/hybrid)
        4. Salary range (if available)
        5. Key requirements/skills mentioned
        6. Experience level required
        7. Job posting date
        8. Job URL/link
        
        Format the output as a structured list where each job is clearly separated.
        Focus on technical skills, programming languages, frameworks, and tools mentioned.
        """
        
        print(f"🔍 Searching LinkedIn for {job_title} positions...")
        linkedin_agent = Agent(task=linkedin_task, llm=self.llm)
        linkedin_results = await linkedin_agent.run()
        
        # Indeed job search
        indeed_task = f"""
        Go to Indeed (https://www.indeed.com/).
        Search for "{job_title}" jobs {f"in {location}" if location else ""}.
        {"Include remote jobs in the search." if remote_ok else ""}
        
        For the first {max_jobs} job listings, extract the following information:
        1. Job title
        2. Company name
        3. Location (including if it's remote/hybrid)
        4. Salary range (if available)
        5. Key requirements/skills mentioned
        6. Experience level required
        7. Job posting date
        8. Job URL/link
        
        Format the output as a structured list where each job is clearly separated.
        Focus on technical skills, programming languages, frameworks, and tools mentioned.
        """
        
        print(f"🔍 Searching Indeed for {job_title} positions...")
        indeed_agent = Agent(task=indeed_task, llm=self.llm)
        indeed_results = await indeed_agent.run()
        
        return {
            "linkedin": linkedin_results,
            "indeed": indeed_results,
            "search_params": {
                "job_title": job_title,
                "location": location,
                "remote_ok": remote_ok,
                "max_jobs": max_jobs,
                "search_date": datetime.datetime.now().isoformat()
            }
        }
    
    async def analyze_and_summarize(self, search_results: Dict[str, Any]):
        """
        Analyze the search results and create a comprehensive summary with keywords
        """
        
        analysis_task = f"""
        Analyze the following job search results and create a comprehensive summary:
        
        LINKEDIN RESULTS:
        {search_results['linkedin']}
        
        INDEED RESULTS:
        {search_results['indeed']}
        
        Provide a structured analysis including:
        
        1. **SUMMARY STATISTICS:**
           - Total jobs found
           - Salary ranges (min, max, average if available)
           - Location distribution
           - Remote/hybrid opportunities
        
        2. **TOP SKILLS & TECHNOLOGIES (with frequency):**
           - Programming languages mentioned
           - Frameworks and libraries
           - Tools and platforms
           - Soft skills
        
        3. **EXPERIENCE LEVELS:**
           - Entry level positions
           - Mid-level positions
           - Senior positions
        
        4. **TOP COMPANIES:**
           - List of companies hiring
           - Company types (startup, enterprise, etc.)
        
        5. **KEY INSIGHTS:**
           - Market trends observed
           - Most in-demand skills
           - Salary trends
           - Remote work availability
        
        6. **KEYWORD PAIRS for job applications:**
           - Technical keyword combinations
           - Industry buzzwords
           - Skills to highlight on resume
        
        Format the output in a clear, organized manner with bullet points and sections.
        """
        
        print("📊 Analyzing search results...")
        analysis_agent = Agent(task=analysis_task, llm=self.llm)
        analysis = await analysis_agent.run()
        
        return analysis
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None):
        """
        Save search results to a JSON file
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_search_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to {filename}")
        return filename

async def main():
    """
    Main function to run the job search automation
    """
    job_searcher = JobSearchAgent()
    
    # Configuration - modify these based on your preferences
    JOB_TITLE = "Python Developer"  # Change this to your desired job title
    LOCATION = "New York"  # Change this to your preferred location (or leave empty for all)
    REMOTE_OK = True  # Set to False if you don't want remote jobs
    MAX_JOBS = 15  # Number of jobs to analyze per platform
    
    print("🚀 Starting automated job search...")
    print(f"Searching for: {JOB_TITLE}")
    print(f"Location: {LOCATION if LOCATION else 'Anywhere'}")
    print(f"Remote OK: {REMOTE_OK}")
    print(f"Max jobs per platform: {MAX_JOBS}")
    print("-" * 50)
    
    try:
        # Step 1: Search for jobs
        search_results = await job_searcher.search_jobs(
            job_title=JOB_TITLE,
            location=LOCATION,
            remote_ok=REMOTE_OK,
            max_jobs=MAX_JOBS
        )
        
        # Step 2: Analyze and summarize
        analysis = await job_searcher.analyze_and_summarize(search_results)
        
        # Step 3: Combine results
        final_results = {
            "search_results": search_results,
            "analysis": analysis
        }
        
        # Step 4: Save to file
        filename = job_searcher.save_results(final_results)
        
        # Step 5: Display summary
        print("\n" + "="*60)
        print("📋 JOB SEARCH ANALYSIS COMPLETE")
        print("="*60)
        print(analysis)
        print("\n" + "="*60)
        print(f"Full results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error during job search: {str(e)}")
        print("Please check your internet connection and API keys.")

if __name__ == "__main__":
    asyncio.run(main())
