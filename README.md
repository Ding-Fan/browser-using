# Job Search Automation with Browser-Use

This project contains Python scripts to automate job searching and analysis using AI-powered web automation.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install browser-use langchain-google-genai python-dotenv
   ```

2. **Set up your Google API key in `.env`:**
   ```
   GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Run the job search:**
   ```bash
   python quick_job_research.py
   ```

## 📁 Files Overview

### `quick_job_research.py` (🌟 Start Here)
- **Purpose**: Simple, focused job search on LinkedIn
- **What it does**: Searches for specific role, extracts skills/requirements, provides keyword analysis
- **Best for**: Getting started, testing the system, quick market research

### `simple_job_search.py` (Advanced)
- **Purpose**: Multi-platform job search (LinkedIn, Indeed, AngelList)
- **What it does**: Searches multiple sites, compares results, generates comprehensive analysis
- **Best for**: Thorough market research, comparing opportunities across platforms

### `job_search.py` (Full Featured)
- **Purpose**: Complete job search automation system
- **What it does**: Advanced search, detailed analysis, result saving, trending insights
- **Best for**: Regular job hunting, building a job database, market trend analysis

## 🎯 How to Use

### Basic Usage (Recommended to start):
```python
# Edit quick_job_research.py and change these lines:
JOB_ROLE = "Python Developer"  # Your target job
LOCATION = "San Francisco"     # Your preferred location

# Then run:
python quick_job_research.py
```

### Advanced Usage:
```python
# Edit simple_job_search.py for multi-platform search:
JOB_TITLE = "Full Stack Developer"
LOCATION = "Remote"
MAX_JOBS_PER_SITE = 10

python simple_job_search.py
```

## 📊 What You'll Get

### Keyword Analysis:
- Most in-demand programming languages
- Popular frameworks and tools
- Essential soft skills
- Trending technologies

### Market Insights:
- Salary ranges
- Experience level requirements
- Remote work availability
- Top hiring companies

### Actionable Recommendations:
- Skills to prioritize learning
- Resume keyword optimization
- Best job boards for your field
- Profile improvement suggestions

## 🔧 Customization

### Target Different Roles:
- "Data Scientist"
- "DevOps Engineer" 
- "Product Manager"
- "UX Designer"
- "Machine Learning Engineer"

### Location Options:
- "Remote"
- "New York, NY"
- "San Francisco, CA"
- "London, UK"
- "" (anywhere)

### Platform Selection:
- LinkedIn Jobs
- Indeed
- AngelList/Wellfound
- Glassdoor
- Stack Overflow Jobs

## 🛠️ Troubleshooting

### Common Issues:
1. **Rate limiting**: Add delays between requests
2. **Captcha protection**: Some sites may block automation
3. **API limits**: Google Gemini has usage quotas

### Solutions:
- Use VPN if blocked
- Reduce `MAX_JOBS` number
- Add `time.sleep()` between searches
- Check your API key validity

## 📈 Advanced Features

### Save Results:
```python
# Results are automatically saved as JSON files
# Format: job_analysis_YYYYMMDD_HHMMSS.json
```

### Schedule Regular Searches:
```python
# Add to cron job for daily/weekly searches
0 9 * * 1 cd /path/to/project && python quick_job_research.py
```

### Custom Analysis:
```python
# Modify the analysis prompts to focus on:
# - Specific technologies
# - Company types
# - Salary negotiations
# - Career progression paths
```

## 🎯 Tips for Best Results

1. **Be Specific**: Use exact job titles like "Senior React Developer" vs "Developer"
2. **Check Multiple Locations**: Remote jobs often have more opportunities
3. **Regular Updates**: Job markets change quickly, run searches weekly
4. **Keyword Optimization**: Use the extracted keywords in your resume and applications
5. **Company Research**: Follow up on interesting companies found in results

## 🤝 Contributing

Feel free to:
- Add new job platforms
- Improve analysis prompts
- Add export formats (CSV, Excel)
- Create visualization dashboards
- Add salary prediction models

---

**Happy Job Hunting! 🚀**
# browser-using
