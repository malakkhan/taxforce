import os
import sys
import toml
from pathlib import Path

sys.path.append(os.path.dirname(__file__))  

DASHBOARD_DIR = Path(__file__).resolve().parent
LAUNCHED_ENV_VAR = "TAXFORCE_DASHBOARD_LAUNCHED"

def parse_config_to_flags() -> list[str]:
    config_path = DASHBOARD_DIR / ".streamlit" / "config.toml"
    if not config_path.exists(): 
        return []
    
    config = toml.load(config_path)
    flags = []
    for section, values in config.items():
        if isinstance(values, dict):
            for key, val in values.items():
                if isinstance(val, bool):
                    val = str(val).lower()
                flags.append(f"--{section}.{key}={val}")
    return flags

def is_streamlit_call():
    return 'streamlit.runtime.scriptrunner' in sys.modules

def added_config():
    return os.environ.get(LAUNCHED_ENV_VAR) == "1"

def start_dashboard():
    if is_streamlit_call() and added_config():
        from dashboard.app import main
        main()
    else:
        os.environ[LAUNCHED_ENV_VAR] = "1"
        os.chdir(DASHBOARD_DIR)
        script_path = str(DASHBOARD_DIR / "app.py")
        flags = parse_config_to_flags()
        os.execvp('streamlit', ['streamlit', 'run', script_path] + flags)

__all__ = ["start_dashboard"]

