import json
import random

DTC_FILE = 'dtc_codes.json'

def load_codes_from_file():
    """Loads the DTC codes from the local JSON file."""
    try:
        with open(DTC_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{DTC_FILE}' not found.")
        print("Please run the 'scrape_dtc_codes.py' script first to generate it.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{DTC_FILE}'. The file might be corrupted.")
        return None

def generate_random_dtcs(all_codes, count=3):
    """
    Selects a random sample of DTCs from the provided list.
    
    Returns a list of tuples, e.g., [('P0301', 'Cylinder 1 Misfire Detected'), ...]
    """
    if not all_codes or len(all_codes) < count:
        return []
        
    # Get a list of all available codes (e.g., ['P0001', 'P0002', ...])
    code_keys = list(all_codes.keys())
    
    # Randomly select 'count' number of codes from the list
    randomly_selected_keys = random.sample(code_keys, k=count)
    
    # Build the final list with codes and their descriptions
    simulated_errors = []
    for key in randomly_selected_keys:
        description = all_codes[key]
        simulated_errors.append((key, description))
        
    return simulated_errors

if __name__ == "__main__":
    print("--- Motorcycle DTC Simulator ---")
    
    available_codes = load_codes_from_file()
    
    if available_codes:
        # Simulate a random number of errors between 1 and 4
        num_errors_to_simulate = random.randint(1, 4)
        
        print(f"\nSimulating {num_errors_to_simulate} random error(s)...\n")
        
        random_errors = generate_random_dtcs(available_codes, count=num_errors_to_simulate)
        
        if random_errors:
            print("🚨 Simulated Trouble Codes Found! 🚨")
            for code, desc in random_errors:
                print(f"  -> Code: {code}, Description: {desc}")
        else:
            print("👍 No simulated trouble codes generated.")