import json
from pathlib import Path
from core.config import SimulationConfig

def deep_compare(d1, d2, path=""):
    """
    Recursively compares two dictionaries and returns a list of differences.
    """
    diffs = []
    
    # Check for keys in d1 but not in d2
    for key in d1:
        new_path = f"{path}.{key}" if path else key
        if key not in d2:
            diffs.append(f"MISSING in final config: {new_path} (Value: {d1[key]})")
        elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
            diffs.extend(deep_compare(d1[key], d2[key], new_path))
        elif d1[key] != d2[key]:
            diffs.append(f"DIFFERENCE at {new_path}: Default={d1[key]}, Final={d2[key]}")
            
    # Check for keys in d2 but not in d1
    for key in d2:
        new_path = f"{path}.{key}" if path else key
        if key not in d1:
            diffs.append(f"ADDED in final config: {new_path} (Value: {d2[key]})")
            
    return diffs

def main():
    # Load default configs
    default_data = SimulationConfig.load_defaults()
    
    # Load final config (which merges with defaults)
    final_config_path = Path("core/configs/config_final.json")
    if not final_config_path.exists():
        print(f"Error: {final_config_path} not found.")
        return
        
    final_config = SimulationConfig.from_json(str(final_config_path))
    final_data = final_config.config_data
    
    print(f"Comparing default configuration with {final_config_path}...\n")
    
    differences = deep_compare(default_data, final_data)
    
    if not differences:
        print("No differences found.")
    else:
        print(f"Found {len(differences)} differences:")
        for diff in sorted(differences):
            print(f"  - {diff}")

if __name__ == "__main__":
    main()
