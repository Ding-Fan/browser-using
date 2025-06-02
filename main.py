from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import json
import os
import re
from langchain_deepseek import ChatDeepSeek
from typing import Optional
from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr
from langchain_core.messages import AIMessage

from markdown_extractor import extract_and_save_markdown

# https://github.com/browser-use/browser-use/issues/567#issuecomment-2710518976
# from langchain_community.chat_models import ChatOpenAI

def parse_openrouter_response(text: str) -> str:
    """
    Parse OpenRouter response to remove problematic tool call tokens and extract clean content.
    
    Args:
        text: Raw response text from OpenRouter model
        
    Returns:
        Cleaned text suitable for browser-use agent
    """
    if not isinstance(text, str):
        return str(text)
    
    original_length = len(text)
    
    # Remove tool call start/end tokens that cause parsing issues
    tool_call_patterns = [
        r'<\|tool_call_start_id\|>[^<]*<\|tool_call_end\|>',
        r'<\|tool_call_start\|>[^<]*<\|tool_call_end\|>',
        r'<\|start_header_id\|>[^<]*<\|end_header_id\|>',
        r'<\|eot_id\|>',
        r'<\|begin_of_text\|>',
        r'<\|end_of_text\|>',
        r'<\|assistant\|>',
        r'<\|user\|>',
        r'<\|system\|>',
    ]
    
    cleaned_text = text
    removed_patterns = []
    
    for pattern in tool_call_patterns:
        matches = re.findall(pattern, cleaned_text, flags=re.DOTALL | re.IGNORECASE)
        if matches:
            removed_patterns.extend(matches)
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up extra whitespace and newlines
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    # If we removed problematic patterns, log it
    if removed_patterns and len(cleaned_text) != original_length:
        print(f"Parser: Removed {len(removed_patterns)} problematic token(s), cleaned {original_length} -> {len(cleaned_text)} chars")
    
    # If the response looks like it contains JSON with tool calls, try to extract the content
    try:
        # Look for JSON-like structures and extract content
        json_match = re.search(r'\{[^{}]*"content"[^{}]*\}', cleaned_text, re.DOTALL)
        if json_match:
            potential_json = json_match.group()
            try:
                parsed = json.loads(potential_json)
                if isinstance(parsed, dict) and 'content' in parsed:
                    print("Parser: Extracted content from JSON structure")
                    return parsed['content']
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    
    return cleaned_text


# Read environment variables
load_dotenv()

# LLM Configuration - Change these two lines to switch models
PROVIDER = "openrouter"  # Options: "google", "deepseek", "openrouter"
MODEL = "llama"         # For google: "2.5-flash", "2.0-flash-exp", "2.0-flash", "1.5-pro", "1.5-flash", "1.5"
                       # For deepseek: "chat"
                       # For openrouter: "llama" (or any other model available on OpenRouter)

def get_llm(provider: str, model: str):
    """Initialize and return the specified LLM model"""
    
    if provider == "google":
        # https://ai.google.dev/gemini-api/docs/rate-limits
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
        # https://platform.deepseek.com/usage
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
    
    elif provider == "openrouter":

        openrouter_models = {
            "llama": "meta-llama/llama-3.1-8b-instruct:free",  # More stable free model
            "llama-maverick": "meta-llama/llama-4-maverick:free",  # Original model (might have issues)
            "qwen": "qwen/qwen-2.5-7b-instruct:free",  # Alternative free model
            "phi": "microsoft/phi-3-mini-128k-instruct:free",  # Microsoft's model
            # Add more models as needed
        }
        if model not in openrouter_models:
            raise ValueError(f"Unsupported OpenRouter model: {model}. Available options: {list(openrouter_models.keys())}")

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        class ChatOpenRouter(ChatOpenAI):
            openai_api_key: Optional[SecretStr] = Field(
                alias="api_key", default_factory=secret_from_env("OPENROUTER_API_KEY", default=None)
            )
            @property
            def lc_secrets(self) -> dict[str, str]:
                return {"openai_api_key": "OPENROUTER_API_KEY"}

            def __init__(self,
                        openai_api_key: Optional[str] = None,
                        **kwargs):
                openai_api_key = openai_api_key or os.environ.get("OPENROUTER_API_KEY")
                super().__init__(base_url="https://openrouter.ai/api/v1", openai_api_key=openai_api_key, **kwargs)
            
            def _generate(self, messages, stop=None, run_manager=None, **kwargs):
                """Override _generate to parse OpenRouter responses"""
                try:
                    # Call the parent _generate method
                    result = super()._generate(messages, stop, run_manager, **kwargs)
                    
                    # Parse each generation's text
                    for generation in result.generations:
                        if hasattr(generation, 'text'):
                            generation.text = parse_openrouter_response(generation.text)
                        if hasattr(generation, 'message') and hasattr(generation.message, 'content'):
                            generation.message.content = parse_openrouter_response(generation.message.content)
                    
                    return result
                except Exception as e:
                    print(f"Error in OpenRouter response generation: {e}")
                    # Fallback to parent method
                    return super()._generate(messages, stop, run_manager, **kwargs)
            
            async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
                """Override _agenerate to parse OpenRouter responses (async version)"""
                try:
                    # Call the parent _agenerate method
                    result = await super()._agenerate(messages, stop, run_manager, **kwargs)
                    
                    # Parse each generation's text
                    for generation in result.generations:
                        if hasattr(generation, 'text'):
                            generation.text = parse_openrouter_response(generation.text)
                        if hasattr(generation, 'message') and hasattr(generation.message, 'content'):
                            generation.message.content = parse_openrouter_response(generation.message.content)
                    
                    return result
                except Exception as e:
                    print(f"Error in OpenRouter async response generation: {e}")
                    # Fallback to parent method
                    return await super()._agenerate(messages, stop, run_manager, **kwargs)



        return ChatOpenRouter(
            model_name=openrouter_models[model],  
            # temperature=0.1,  # Lower temperature for more consistent responses
            # max_tokens=4096,
            # model_kwargs={
                # "tool_choice": "auto",  # Allows the model to decide when to use tools
                # "response_format": {"type": "text"}  # Force text format to avoid JSON issues
            # }
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}. Available options: ['google', 'deepseek', 'openrouter']")

# Initialize the selected LLM
llm = get_llm(PROVIDER, MODEL)


async def run_agent_with_fallback(task: str, llm, max_retries: int = 2):
    """
    Run the browser-use agent with fallback mechanisms for parsing errors.
    
    Args:
        task: The task description for the agent
        llm: The language model to use
        max_retries: Maximum number of retries if parsing fails
        
    Returns:
        The agent result or error message
    """
    for attempt in range(max_retries + 1):
        try:
            print(f"Attempt {attempt + 1}/{max_retries + 1} - Running agent...")
            
            agent = Agent(task=task, llm=llm)
            result = await agent.run()
            
            # Additional parsing if needed for OpenRouter responses
            if PROVIDER == "openrouter" and isinstance(result, str):
                result = parse_openrouter_response(result)
            
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a parsing error related to tool calls
            if any(keyword in error_msg for keyword in ['tool_call', 'json', 'parsing', 'malformed']):
                print(f"Parsing error detected on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries:
                    print("Retrying with different approach...")
                    # For retries, we could modify the LLM parameters
                    continue
                else:
                    print("Max retries reached. Falling back to error message.")
                    return f"Error: Failed to parse model response after {max_retries + 1} attempts. Last error: {e}"
            else:
                # If it's not a parsing error, don't retry
                raise e
    
    return "Error: Unexpected failure in agent execution."


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

    task_description = (
        f"I'm a student. I'm writing my resume in Japanese. "
        f"Here is my personal information and background:\n\n{about_me}\n\n"
        f"Please follow these instructions for writing 志望動機:\n\n{motivation_instructions}\n\n"
        f"{browse_instruction}"
        f"Based on both my background and the company information, "
        f"help me write 志望動機 in Japanese for it. "
        f"You should create short, medium, and long versions.\n"
        f"At the end, provide a Analyse section of the company.\n"
        f"Output the result in markdown format, with clear section headers for each version."
    )

    # Use the fallback mechanism for robust execution
    result = await run_agent_with_fallback(task_description, llm)
    print(result)

    # Use the reusable extractor to save markdown
    extract_and_save_markdown(result)

asyncio.run(main())