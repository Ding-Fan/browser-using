"""
Japan Job Search Automation with Enhanced Filtering

This script provides comprehensive job search across Japanese platforms with:
- Keyword filtering for specific company types/benefits
- Company size preferences
- Predefined search profiles for common job search strategies

USAGE EXAMPLES:

1. Quick startup search:
   Set SEARCH_PROFILE = "startup_lover"

2. Remote work focus:
   Set SEARCH_PROFILE = "remote_worker"

3. Custom search:
   Set SEARCH_PROFILE = None and configure CUSTOM_KEYWORDS and CUSTOM_STAFF_COUNT

Available Search Profiles:
- startup_lover: Targets startups and growing companies
- remote_worker: Focuses on remote work opportunities  
- international_focus: International companies with English environment
- work_life_balance: Companies with good work-life balance
- beginner_friendly: Entry-level and training-focused positions
- tech_giant: Large established tech companies
- freelancer_friendly: Companies open to freelancers and side work

Keywords Examples:
- スタートアップ (startup), ベンチャー (venture), リモートワーク (remote work)
- 外資系 (foreign company), 英語 (English), フレックス (flexible hours)
- 未経験 (no experience), 新卒 (new graduate), 副業OK (side job OK)

Staff Count Options:
- "1-10", "11-50", "51-100", "101-500", "500+", "1000+"
- Or combinations like "1-50", "51-200"
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
import json
import datetime

# Read GOOGLE_API_KEY into env
load_dotenv()

class JapanJobSearcher:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
        
    async def search_japanese_platform(self, platform_name, platform_url, job_role, location, japanese_level="Business", keywords=None, staff_count=None):
        """
        Search Japanese job platforms with Japan-specific parameters
        """
        
        # Platform-specific search strategies
        platform_strategies = {
            "Rikunabi Next": "Focus on new graduate and mid-career positions. Look for '転職' (career change) opportunities.",
            "Doda": "Enterprise-focused platform. Look for both Japanese and international companies.",
            "Green": "IT/Tech-focused platform. Look for startup and tech company positions.",
            "Wantedly": "Startup and modern company culture platform. Look for 'やりがい' (fulfilling work) positions.",
            "Bizreach": "Executive and high-skill positions. Look for management and senior roles.",
            "Indeed Japan": "Mixed platform. Look for both Japanese and international postings.",
            "CareerCross": "Bilingual and international opportunities in Japan."
        }
        
        strategy = platform_strategies.get(platform_name, "General job search platform.")
        
        # Build additional search criteria
        additional_criteria = ""
        if keywords:
            keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            additional_criteria += f"\n- Keywords to focus on: {keywords_str}"
        if staff_count:
            additional_criteria += f"\n- Preferred company size: {staff_count} employees"
        
        task = f"""
        Go to {platform_url} and search for "{job_role}" jobs in "{location}, Japan".
        
        Platform Strategy: {strategy}
        
        Search Parameters:
        - Job Role: {job_role}
        - Location: {location}
        - Japanese Level: {japanese_level}{additional_criteria}
        
        For each job found (aim for 5-7 jobs), extract:
        
        🏢 **BASIC INFORMATION:**
        - Job Title (in English and Japanese if available)
        - Company Name
        - Location (Remote/Hybrid/On-site)
        - Employment Type (正社員/契約社員/派遣 etc.)
        - Experience Level Required
        - Salary Range (JPY)
        
        🌍 **INTERNATIONAL REQUIREMENTS:**
        - Japanese Language Level Required (N1, N2, Business, Native, etc.)
        - English Level Required
        - Visa Sponsorship Available
        - International team or Japanese team
        
        💻 **TECHNICAL REQUIREMENTS:**
        - Programming Languages
        - Frameworks/Libraries
        - Cloud Platforms (AWS, Azure, GCP)
        - Development Tools
        - Methodologies (Agile, Scrum, etc.)
        
        🏢 **COMPANY CULTURE:**
        - Company Size (number of employees)
        - Industry Sector
        - Work Style (Traditional Japanese vs International)
        - Benefits mentioned
        - Career development opportunities
        
        📋 **SPECIAL NOTES:**
        - Any unique requirements for Japanese market
        - Cultural expectations mentioned
        - Remote work policies
        - Training/learning opportunities
        {f"- Relevance to keywords: {keywords}" if keywords else ""}
        {f"- Company size match for {staff_count} preference" if staff_count else ""}
        
        {f"IMPORTANT: Pay special attention to jobs matching these criteria: {keywords}" if keywords else ""}
        {f"IMPORTANT: Prioritize companies with {staff_count} employees when filtering results." if staff_count else ""}
        
        Format each job clearly and note any Japan-specific requirements or benefits.
        """
        
        print(f"🔍 Searching {platform_name} for {job_role} positions...")
        agent = Agent(task=task, llm=self.llm)
        result = await agent.run()
        return result

    async def comprehensive_japan_search(self, job_role="Web Developer", location="Tokyo", japanese_level="N2", keywords=None, staff_count=None):
        """
        Comprehensive job search across Japanese platforms
        """
        
        # 🇯🇵 Core Japanese job platforms
        japanese_platforms = [
            ("Rikunabi Next", "https://next.rikunabi.com/"),
            ("Doda", "https://doda.jp/"),
            ("Green (IT/Tech)", "https://www.green-japan.com/"),
            ("Wantedly", "https://www.wantedly.com/"),
        ]
        
        # 🌍 International-friendly platforms in Japan
        international_platforms = [
            ("CareerCross", "https://www.careercross.com/"),
            ("Indeed Japan", "https://jp.indeed.com/"),
            ("LinkedIn Japan", "https://www.linkedin.com/jobs/"),
        ]
        
        print(f"🇯🇵 Starting comprehensive Japan job search...")
        print(f"Job Role: {job_role}")
        print(f"Location: {location}")
        print(f"Japanese Level: {japanese_level}")
        if keywords:
            keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            print(f"Keywords: {keywords_str}")
        if staff_count:
            print(f"Preferred Company Size: {staff_count} employees")
        print("-" * 70)
        
        all_results = {}
        
        # Search Japanese platforms first
        print("🏯 Searching Japanese platforms...")
        for platform_name, platform_url in japanese_platforms[:3]:  # Limit to avoid rate limits
            try:
                result = await self.search_japanese_platform(
                    platform_name, platform_url, job_role, location, japanese_level, keywords, staff_count
                )
                all_results[platform_name] = result
                print(f"✅ {platform_name} completed")
                await asyncio.sleep(7)  # Respectful delay
            except Exception as e:
                print(f"❌ {platform_name} failed: {str(e)}")
                all_results[platform_name] = f"Search failed: {str(e)}"
        
        # Search international platforms
        print("\n🌍 Searching international platforms...")
        for platform_name, platform_url in international_platforms[:2]:
            try:
                result = await self.search_japanese_platform(
                    platform_name, platform_url, job_role, location, japanese_level, keywords, staff_count
                )
                all_results[platform_name] = result
                print(f"✅ {platform_name} completed")
                await asyncio.sleep(7)
            except Exception as e:
                print(f"❌ {platform_name} failed: {str(e)}")
                all_results[platform_name] = f"Search failed: {str(e)}"
        
        return all_results
    
    async def analyze_japan_market(self, search_results, job_role, location, japanese_level, keywords=None, staff_count=None):
        """
        Analyze Japan job market with cultural and linguistic insights
        """
        
        combined_results = ""
        for platform, results in search_results.items():
            combined_results += f"\n\n{'='*20} {platform.upper()} {'='*20}\n"
            combined_results += str(results)
        
        # Build search context for analysis
        search_context = f"""
        Search Parameters:
        - Job Role: {job_role}
        - Location: {location}
        - Japanese Level: {japanese_level}
        """
        
        if keywords:
            keywords_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            search_context += f"- Target Keywords: {keywords_str}\n"
        
        if staff_count:
            search_context += f"- Preferred Company Size: {staff_count} employees\n"
        
        analysis_task = f"""
        Analyze the Japanese job market for "{job_role}" positions in {location} from multiple platforms:
        
        {search_context}
        
        SEARCH RESULTS:
        {combined_results}
        
        Provide detailed analysis covering:
        
        🇯🇵 **JAPAN MARKET OVERVIEW:**
        - Total opportunities found across platforms
        - Salary ranges in JPY (and USD equivalent)
        - Japanese vs International companies ratio
        - Remote work availability in Japan
        - Visa sponsorship opportunities
        {f"- Match rate for keywords: {keywords}" if keywords else ""}
        {f"- Companies matching size preference ({staff_count})" if staff_count else ""}
        
        🗣️ **LANGUAGE REQUIREMENTS ANALYSIS:**
        - Japanese level distribution (N5 to Native)
        - English requirements
        - Bilingual opportunities
        - Communication expectations
        - Best opportunities for {japanese_level} level Japanese
        
        💻 **TECHNICAL SKILLS DEMAND:**
        (Frequency analysis across all platforms)
        - Programming Languages: [count and percentage]
        - Frameworks/Libraries: [most demanded]
        - Cloud Platforms: [AWS vs Azure vs GCP in Japan]
        - Development Tools: [popular in Japanese companies]
        - Methodologies: [Agile adoption in Japan]
        {f"- Relevance of target keywords ({keywords}) in market" if keywords else ""}
        
        🏢 **COMPANY CULTURE INSIGHTS:**
        - Traditional Japanese companies vs International
        - Startup scene in Japan
        - Work-life balance trends
        - Career progression paths
        - Training and development opportunities
        {f"- Analysis of {staff_count} sized companies (if found)" if staff_count else ""}
        
        🎯 **PLATFORM EFFECTIVENESS:**
        - Best platforms for {job_role} roles
        - Japanese platforms vs International platforms
        - Success rates by platform
        - Application strategies by platform
        {f"- Which platforms best match your criteria (keywords: {keywords}, size: {staff_count})" if keywords or staff_count else ""}
        
        💡 **ACTIONABLE RECOMMENDATIONS:**
        
        **For Technical Skills:**
        - Top 3 skills to prioritize for Japan market
        - Certifications valued in Japan
        - Tools specific to Japanese companies
        
        **For Language/Cultural Preparation:**
        - Japanese study recommendations
        - Business etiquette essentials
        - Interview preparation tips
        - Networking strategies in Japan
        
        **For Job Applications:**
        - CV/Resume format for Japan
        - Cover letter strategies
        - Interview process expectations
        - Salary negotiation in Japan
        
        🚀 **NEXT STEPS ROADMAP:**
        - 30-day action plan
        - Language learning milestones
        - Skill development priorities
        - Networking activities
        - Application timeline
        
        Focus on practical, Japan-specific advice that accounts for cultural nuances and market realities.
        """
        
        print("📊 Analyzing Japan job market comprehensively...")
        agent = Agent(task=analysis_task, llm=self.llm)
        analysis = await agent.run()
        return analysis

def get_search_profiles():
    """
    Predefined search profiles for different job search strategies
    """
    profiles = {
        "startup_lover": {
            "keywords": ["スタートアップ", "ベンチャー", "成長企業"],
            "staff_count": "1-50",
            "description": "Targeting startups and growing companies"
        },
        
        "remote_worker": {
            "keywords": ["リモートワーク", "在宅勤務", "フルリモート", "テレワーク"],
            "staff_count": None,
            "description": "Focusing on remote work opportunities"
        },
        
        "international_focus": {
            "keywords": ["外資系", "英語", "グローバル", "多国籍"],
            "staff_count": "100+",
            "description": "International companies and English environment"
        },
        
        "work_life_balance": {
            "keywords": ["フレックス", "ワークライフバランス", "残業なし", "有給"],
            "staff_count": "51-500",
            "description": "Companies with good work-life balance"
        },
        
        "beginner_friendly": {
            "keywords": ["未経験", "新卒", "研修充実", "教育制度"],
            "staff_count": "101+",
            "description": "Entry-level and training-focused companies"
        },
        
        "tech_giant": {
            "keywords": ["大手", "上場企業", "安定", "福利厚生"],
            "staff_count": "1000+",
            "description": "Large established tech companies"
        },
        
        "freelancer_friendly": {
            "keywords": ["副業OK", "業務委託", "フリーランス", "契約"],
            "staff_count": None,
            "description": "Companies open to freelancers and side work"
        }
    }
    return profiles

def select_search_profile(profile_name=None):
    """
    Select a predefined search profile or return custom configuration
    """
    profiles = get_search_profiles()
    
    if profile_name and profile_name in profiles:
        profile = profiles[profile_name]
        print(f"📋 Using '{profile_name}' profile: {profile['description']}")
        return profile["keywords"], profile["staff_count"]
    
    # Return custom configuration if no profile selected
    return None, None

async def main():
    """
    Main function for Japan-focused job search
    """
    searcher = JapanJobSearcher()
    
    # 🎯 CONFIGURATION - Customize these settings
    JOB_ROLE = "Web Developer"  # Change to your target role
    LOCATION = "Tokyo"  # Tokyo, Osaka, Kyoto, Remote, etc.
    JAPANESE_LEVEL = "N2"  # N5, N4, N3, N2, N1, Business, Native
    
    # 🎯 CONFIGURATION - Choose your search strategy
    
    # Option 1: Use a predefined profile
    # Available profiles: "startup_lover", "remote_worker", "international_focus", 
    #                    "work_life_balance", "beginner_friendly", "tech_giant", "freelancer_friendly"
    SEARCH_PROFILE = None  # Change this to use different profiles, or set to None for custom
    
    # Option 2: Custom configuration (used if SEARCH_PROFILE is None)
    CUSTOM_KEYWORDS = [
        "スタートアップ",  # Startup companies
        "リモートワーク",  # Remote work
        # "外資系",         # Foreign companies
        # "フレックス",      # Flexible hours
        # "副業OK",         # Side jobs allowed
        "英語",           # English environment
        # "新卒",           # New graduate
        # "未経験",         # No experience required
    ]
    CUSTOM_STAFF_COUNT = "1-25"  # Small to medium companies
    
    # Get search parameters
    if SEARCH_PROFILE:
        KEYWORDS, STAFF_COUNT = select_search_profile(SEARCH_PROFILE)
    else:
        KEYWORDS = CUSTOM_KEYWORDS
        STAFF_COUNT = CUSTOM_STAFF_COUNT
        print("📋 Using custom search configuration")
    
    try:
        # Step 1: Search across platforms
        print("🇯🇵 JAPAN JOB MARKET RESEARCH STARTING...")
        search_results = await searcher.comprehensive_japan_search(
            job_role=JOB_ROLE,
            location=LOCATION,
            japanese_level=JAPANESE_LEVEL,
            keywords=KEYWORDS,
            staff_count=STAFF_COUNT
        )

        # Step 2: Analyze results
        analysis = await searcher.analyze_japan_market(
            search_results, JOB_ROLE, LOCATION, JAPANESE_LEVEL, KEYWORDS, STAFF_COUNT
        )
        
        # Step 3: Save results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "search_date": datetime.datetime.now().isoformat(),
            "job_role": JOB_ROLE,
            "location": LOCATION,
            "japanese_level": JAPANESE_LEVEL,
            "platform_results": search_results,
            "market_analysis": analysis
        }
        
        filename = f"japan_job_search_{JOB_ROLE.replace(' ', '_')}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # Step 4: Display results
        print("\n" + "="*80)
        print("🇯🇵 JAPAN JOB MARKET ANALYSIS COMPLETE!")
        print("="*80)
        print(analysis)
        print("\n" + "="*80)
        print(f"📁 Complete results saved to: {filename}")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error during Japan job search: {str(e)}")
        print("Please check your internet connection and API configuration.")

if __name__ == "__main__":
    asyncio.run(main())
