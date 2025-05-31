#!/usr/bin/env python3

import json
from markdown_extractor import extract_and_save_markdown

def test_log_processing():
    # Load the actual log file
    log_filename = "志望動機_log_20250531_200228.json"
    
    try:
        with open(log_filename, "r", encoding="utf-8") as f:
            agent_result = json.load(f)
        
        print(f"Loaded log file: {log_filename}")
        print(f"Agent result type: {type(agent_result)}")
        print(f"Keys in agent result: {list(agent_result.keys()) if isinstance(agent_result, dict) else 'Not a dict'}")
        
        # Process the log with the extractor
        result_filename = extract_and_save_markdown(agent_result, filename_prefix="志望動機_from_log")
        
        if result_filename:
            print(f"✅ Successfully extracted and saved to: {result_filename}")
        else:
            print("❌ Failed to extract markdown from log")
            
    except FileNotFoundError:
        print(f"❌ Log file not found: {log_filename}")
    except Exception as e:
        print(f"❌ Error processing log: {e}")

if __name__ == "__main__":
    test_log_processing()
