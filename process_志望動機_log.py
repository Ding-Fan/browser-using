"""
Script to process the browser automation log and extract the final 志望動機 content.
"""

import json
from markdown_extractor import extract_and_save_markdown

def load_and_process_log(log_filename):
    """Load the JSON log file and process it with the markdown extractor."""
    try:
        with open(log_filename, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        print(f"Successfully loaded log file: {log_filename}")
        
        # Extract the content using the markdown extractor
        result_filename = extract_and_save_markdown(log_data, filename_prefix="志望動機_final")
        
        if result_filename:
            print(f"✅ Successfully extracted and saved 志望動機 to: {result_filename}")
            return result_filename
        else:
            print("❌ Failed to extract content from the log file")
            return None
            
    except Exception as e:
        print(f"❌ Error processing log file: {e}")
        return None

if __name__ == "__main__":
    # Process the browser automation log file
    log_file = "志望動機_log_20250531_200228.json"
    process_result = load_and_process_log(log_file)
    
    if process_result:
        print("\n" + "="*60)
        print("🎉 志望動機 extraction completed successfully!")
        print("="*60)
        
        # Also display the content for quick verification
        try:
            with open(process_result, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n📝 Extracted Content Preview:")
            print("-" * 40)
            print(content[:500] + "..." if len(content) > 500 else content)
        except Exception as e:
            print(f"Could not preview content: {e}")
    else:
        print("\n❌ Failed to process the 志望動機 log file")
