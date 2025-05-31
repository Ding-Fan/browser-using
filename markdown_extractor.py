import datetime
import json
import re # Import the regular expression module
import os # Import the os module

# Define output directories
RESULT_DIR = "output/result"
LOG_DIR = "output/log"

# Simulate ActionResult and AgentHistoryList for testing
class ActionResult:
    def __init__(self, is_done, extracted_content=None, text=None):
        self.is_done = is_done
        self.extracted_content = extracted_content
        self.text = text

    def __repr__(self):
        # Add a __repr__ for better logging of object instances
        content_preview = self.extracted_content[:20] + "..." if self.extracted_content else "None"
        return f"ActionResult(is_done={self.is_done}, extracted_content='{content_preview}')"

class AgentHistoryList:
    def __init__(self, all_results):
        self.all_results = all_results

# --- CORRECTED AND SIMPLIFIED FUNCTION ---
def extract_and_save_markdown(agent_result, filename_prefix="志望動機"):
    """
    Extracts the final markdown output from an agent result, saves it to a file,
    and saves a raw log of the agent's output.

    Returns the markdown filename if successful, else None.
    """
    # Create a timestamp once for both files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure output directories exist
    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    # --- Step 1: Save a raw log of the entire agent result ---
    log_filename = os.path.join(LOG_DIR, f"{filename_prefix}_log_{timestamp}.json")
    try:
        # A robust way to serialize any object (including custom classes) to JSON
        log_content = json.dumps(
            agent_result, 
            default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o), 
            indent=2,
            ensure_ascii=False # Ensures Japanese characters are saved correctly
        )
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(log_content)
        print(f"Agent result log saved to {log_filename}")
    except Exception as e:
        print(f"Warning: Could not save agent result log: {e}")

    # --- Step 2: Find the final content from the agent history ---
    final_output = None
    history = None

    # Check for different possible structures
    if hasattr(agent_result, 'all_results'):
        history = agent_result.all_results
    elif hasattr(agent_result, 'history'):
        history = agent_result.history
    elif isinstance(agent_result, dict):
        if 'all_results' in agent_result:
            history = agent_result['all_results']
        elif 'history' in agent_result:
            history = agent_result['history']
    
    if history:
        # Search backwards for the first action marked as done
        for history_item in reversed(history):
            # Handle nested structure: history -> result array
            results = None
            if isinstance(history_item, dict) and 'result' in history_item:
                results = history_item['result']
            elif not isinstance(history_item, dict) and hasattr(history_item, 'result'):
                results = history_item.result
            else:
                # Fallback: treat history_item as the action itself (for simpler structures)
                results = [history_item]
            
            if results:
                for action in results:
                    is_done_val = None
                    current_extraction = None
                    text_field_val = None

                    # Get 'is_done' status
                    if isinstance(action, dict):
                        is_done_val = action.get('is_done')
                    elif hasattr(action, 'is_done'):
                        is_done_val = action.is_done

                    if is_done_val:
                        # Try to get 'extracted_content'
                        if isinstance(action, dict):
                            current_extraction = action.get('extracted_content')
                        elif hasattr(action, 'extracted_content'):
                            current_extraction = action.extracted_content
                        
                        # If 'extracted_content' is not found or is empty, try 'text'
                        if not current_extraction:
                            if isinstance(action, dict):
                                text_field_val = action.get('text')
                            elif hasattr(action, 'text'):
                                text_field_val = action.text
                            
                            if text_field_val:
                                if isinstance(text_field_val, dict) and 'text' in text_field_val:
                                    current_extraction = text_field_val['text']
                                elif isinstance(text_field_val, str):
                                    current_extraction = text_field_val
                        
                        if current_extraction:
                            final_output = current_extraction
                            break # Stop after finding the first 'done' action
                if final_output:
                    break # Stop searching through history items
    
    # --- Step 3: Clean up and save the extracted markdown ---
    if not final_output:
        print("Could not find a final output marked with 'is_done=True' in the agent result.")
        return None

    # **FIX:** This now handles both wrapped and raw markdown.
    # It uses regex to find content inside ```markdown ... ``` if it exists.
    markdown_match = re.search(r"```(?:markdown)?\s*(.*?)\s*```", final_output, re.DOTALL)
    if markdown_match:
        # If wrapped in ```markdown ... ``` or ``` ... ```, extract the content
        final_output = markdown_match.group(1).strip()
    # If not wrapped, `final_output` remains unchanged (it's already the raw markdown).

    # Save the cleaned markdown content
    md_filename = os.path.join(RESULT_DIR, f"{filename_prefix}_{timestamp}.md")
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"Result saved to {md_filename}")
        return md_filename
    except Exception as e:
        print(f"Error: Could not save the markdown file: {e}")
        return None


# --- Test with the provided example ---
def test_extractor():
    # The last action is_done=True and has the raw markdown in extracted_content
    actions = [
        ActionResult(False, extracted_content='dummy content 1'),
        ActionResult(False, extracted_content='dummy content 2'),
        ActionResult(True, extracted_content='# 志望動機 (Reasons for Applying)\n\nHere are a few versions of a 志望動機... etc.')
    ]
    agent_result = AgentHistoryList(all_results=actions)
    print("--- Running Test Case 1: Raw Markdown in Final Action ---")
    extract_and_save_markdown(agent_result)
    print("\n" + "="*50 + "\n")

    # --- Add a new test case to check ```markdown``` wrapping ---
    actions_with_wrapper = [
        ActionResult(False, extracted_content='some other content'),
        ActionResult(True, extracted_content='Some text before the block.\n\n```markdown\n# This is a title\n\nThis is wrapped markdown content.\n```\n\nSome text after the block.')
    ]
    agent_result_with_wrapper = AgentHistoryList(all_results=actions_with_wrapper)
    print("--- Running Test Case 2: Wrapped Markdown in Final Action ---")
    extract_and_save_markdown(agent_result_with_wrapper, filename_prefix="志望動機_wrapped")


if __name__ == "__main__":
    test_extractor()
