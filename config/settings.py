import os
from datetime import datetime
import streamlit as st

# Model and Search Settings
DEFAULT_MODEL = "claude-sonnet-4-20250514"  # Latest stable Claude model
ANTHROPIC_API_KEY = "your API KEY"
MAX_TOKENS = 10000  # Max tokens for Claude Sonnet
MAX_RESULTS = 10  # Limit to 10 articles
SEARCH_DEPTH = "advanced"

def get_api_key(key_name: str) -> str:
    """Get API key from session state or environment"""
    print(f"[settings] Attempting to get API key: {key_name}")
    
    # First try session state
    if key_name in st.session_state and st.session_state[key_name]:
        print(f"[settings] Found {key_name} in session state, length: {len(st.session_state[key_name])}")
        return st.session_state[key_name]
    
    # Then try environment variables
    env_value = os.getenv(key_name)
    if env_value:
        print(f"[settings] Found {key_name} in environment variables, length: {len(env_value)}")
        st.session_state[key_name] = env_value
        return env_value
    
    print(f"[settings] ⚠️ {key_name} not found in session state or environment")
    return ""

def validate_api_keys() -> bool:
    """Validate required API keys"""    
    required_keys = {
        "ANTHROPIC_API_KEY": "Claude API Key",
        "TAVILY_API_KEY": "Tavily API Key"
    }
    
    missing_keys = []
    for env_key, display_name in required_keys.items():
        if not get_api_key(env_key):
            missing_keys.append(display_name)
    
    if missing_keys:
        st.error(f"Missing required API keys: {', '.join(missing_keys)}")
        with st.expander("⚙️ Configure API Keys"):
            for env_key, display_name in required_keys.items():
                if not get_api_key(env_key):
                    value = st.text_input(
                        display_name,
                        type="password",
                        key=env_key,
                        help=f"Enter your {display_name}"
                    )
                    if value:
                        st.session_state[env_key] = value
        return False
    return True

# Shared memory for agents
class RAGMemory:
    def __init__(self):
        self._memory = {}
        self._last_modified = {}
    
    def set(self, key: str, value: any):
        """Set a value in memory with timestamp"""
        self._memory[key] = value
        self._last_modified[key] = datetime.now().isoformat()
    
    def get(self, key: str, default=None):
        """Get a value from memory"""
        return self._memory.get(key, default)
    
    def get_last_modified(self, key: str) -> str:
        """Get last modification time for a key"""
        return self._last_modified.get(key)
    
    def clear(self):
        """Clear all memory"""
        self._memory.clear()
        self._last_modified.clear()
    
    def check_memory_status(self) -> dict:
        """Get memory status"""
        return {
            "keys": list(self._memory.keys()),
            "last_modified": self._last_modified
        }

# Initialize shared memory
rag_memory = RAGMemory()
