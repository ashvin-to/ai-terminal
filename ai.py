
import os
import sys
import re
import json
import signal
import atexit
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import dotenv
from openai import OpenAI
from collections import deque

# Platform 
SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == 'windows'
IS_LINUX = SYSTEM == 'linux'
IS_MAC = SYSTEM == 'darwin'

# Config paths 
if IS_WINDOWS:
    CONFIG_DIR = os.path.join(os.getenv('APPDATA', ''), 'ai_terminal')
    HISTORY_FILE = os.path.join(CONFIG_DIR, 'history.json')
    API_KEY_FILE = os.path.join(CONFIG_DIR, '.env')
else:
    CONFIG_DIR = os.path.expanduser('~/.ai_config')
    HISTORY_FILE = os.path.expanduser('~/.ai_terminal_history.json')
    API_KEY_FILE = os.path.join(CONFIG_DIR, '.env')

# if config dir does not exist, create it
os.makedirs(CONFIG_DIR, exist_ok=True)

MAX_HISTORY = 15 # context data 


def get_api_key():
    '''
    Load API key from .env file
    '''
    if os.path.exists(API_KEY_FILE):
        dotenv.load_dotenv(API_KEY_FILE)
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("❌ Error: OPENROUTER_API_KEY not found.")
        print("Run `ai-setup` to configure your API key.")
        sys.exit(1)
    return key

def detect_os() -> str:
    """Detect the operating system and return a normalized name."""
    if IS_WINDOWS:
        return 'windows'
    elif IS_MAC:
        return 'macos'
    
    # Linux distribution detection
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                data = f.read().lower()
            if "arch" in data:
                return "arch"
            elif any(x in data for x in ["ubuntu", "debian", "pop"]):
                return "debian"
            elif "fedora" in data or "rhel" in data or "centos" in data:
                return "fedora"
    except Exception:
        pass
    
    return "linux"

os_type = detect_os()

# add your model to your liking these are the free model make sure to check the openrouter website for the latest models and change in the models. 

PRIMARY_MODEL = "qwen/qwen3-coder:free"
FALLBACK_MODELS = [
    "google/gemma-3n-e2b-it:free",
    "deepseek/deepseek-chat-v3.1:free",
    "mistralai/mistral-small-3.2-24b-instruct:free",
    "nousresearch/deephermes-3-llama-3-8b-preview:free",
    "meta-llama/llama-3.3-8b-instruct:free",
    "qwen/qwen3-coder:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
]

DESTRUCTIVE_KEYWORDS = [
    "rm ", "shutdown", "reboot", "poweroff", "init 0", "halt", "mkfs", "dd ",
    "kill -9", "systemctl stop", "systemctl disable"
]

def confirm_command(cmd):
    for keyword in DESTRUCTIVE_KEYWORDS:
        if keyword in cmd:
            confirm = input(f"⚠️ Destructive command: '{cmd}'\nRun? (yes/no): ").strip().lower()
            return confirm == "yes"
    return True

def execute_command(command: str) -> str:
    """Execute a shell command and return the output."""
    try:
        if not confirm_command(command):
            return "❌ Command aborted."
            
        # shell
        shell = True
        if IS_WINDOWS:
            # powershell
            if command.startswith('cd '):
                # directory change
                try:
                    os.chdir(command[3:].strip())
                    return f"Changed directory to {os.getcwd()}"
                except Exception as e:
                    return f"❌ Error changing directory: {e}"
            
            # powershell commands
            command = f'powershell -NoProfile -Command "{command}"'
        
        # execute the command
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            timeout=60,
            cwd=os.getcwd()
        )
        
        output = result.stdout.strip() or result.stderr.strip()
        return output if output else "Command executed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return "❌ Command timed out after 60 seconds."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def extract_command(text):
    fenced = re.findall(r"```(?:sh|bash)?\n([\s\S]*?)```", text, re.DOTALL)
    if fenced:
        return "\n".join(line.strip() for line in fenced[0].splitlines() if line.strip())
    inline = re.findall(r"\$ ([^\n]+)", text)
    if inline:
        return inline[0].strip()
    return None

def get_system_message() -> Dict[str, str]:
    """Generate the system message with OS-specific instructions."""
    os_instructions = {
        'windows': (
            "You are a PowerShell/CMD assistant on Windows. "
            "Use PowerShell syntax for commands. "
            "For directory operations, use 'cd' or 'Set-Location'. "
            "Use '\' for paths or escape them with '`' in PowerShell."
        ),
        'macos': (
            "You are a terminal assistant on macOS. "
            "Use standard Unix commands. "
            "Note that some commands may differ from Linux."
        ),
        'linux': (
            f"You are a terminal assistant on {os_type} Linux. "
            "Use standard Unix commands."
        )
    }
    
    instructions = os_instructions.get(os_type, "You are a terminal assistant.")
    
    return {
        "role": "system",
        "content": (
            f"{instructions} Rules:\n"
            "1. Use ```bash ...``` only for real shell commands.\n"
            "2. For explanations, use plain text — no echo, no code blocks.\n"
            "3. Warn before destructive actions.\n"
            "4. Be concise. One command at a time unless asked.\n"
            "5. Always use the most compatible commands for the current OS."
        )
    }

def load_history():
    '''
    load the old conversation for giving the context to the model
    '''
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
            if not history or history[0]["role"] != "system":
                return [get_system_message()]
            return history
        except Exception as e:
            print(f"⚠️ Failed to load history: {e}")
    return [get_system_message()]

def save_history(history):
    '''Save the history of the conversation to a file'''
    dq = deque(history, maxlen=MAX_HISTORY)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(dq), f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save history: {e}")

def get_ai_response(client, messages):
    # model resonse
    for model in [PRIMARY_MODEL] + FALLBACK_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=30
            )
            return response.choices[0].message.content.strip(), model
        except Exception as e:
            print(f"⚠️ Model {model} failed: {e}")
            continue
    return None, None

def run_once(client, user_input, history):
    '''
    run the model once and get the response
    '''
    history.append({"role": "user", "content": user_input})
    print("Assistant is thinking...\n")

    response, used_model = get_ai_response(client, history)
    if not response:
        print("❌ All models failed. Check network or API key.")
        return

    cmd = extract_command(response)
    if cmd:
        print(f"🔧 Running: {cmd}")
        output = execute_command(cmd)
        print(f"\n{output}")
        history.append({"role": "assistant", "content": response})
        history.append({"role": "user", "content": f"Command: {cmd}\nOutput: {output}"})
    else:
        print(response)
        history.append({"role": "assistant", "content": response})
    save_history(history)

def interactive_mode(client, history):
    '''
    interactive mode 
    '''
    print("💬 Interactive mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        if not user_input:
            continue
        run_once(client, user_input, history)

def main():
    # ctrl+c stops the execution
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    api_key = get_api_key()
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    history = load_history()

    # use - ai for one time response 
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        run_once(client, user_input, history)
        sys.exit(0)

    # use - 'ai' for interactive mode
    interactive_mode(client, history)
    save_history(history)

if __name__ == "__main__":
    main()
