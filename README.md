# AI Terminal Assistant

A cross-platform command-line AI assistant that helps you with terminal commands and system tasks. It uses OpenRouter's API to provide AI-powered command suggestions and explanations directly in your terminal, working on Windows, macOS, and Linux.

## ✨ Features

- **Cross-Platform**: Works on Windows (PowerShell/CMD), macOS, and Linux
- **Natural Language to Commands**: Convert your natural language requests into terminal commands
- **Interactive Mode**: Chat with the AI assistant directly in your terminal
- **Command Safety**: Warns before executing potentially destructive commands
- **OS Detection**: Automatically detects your operating system and shell
- **Fallback Models**: Automatically switches between different AI models if one fails
- **Command History**: Saves your conversation history for context

## 🚀 Installation

### Windows

1. **Prerequisites**:
   - Install [Python 3.8 or later](https://www.python.org/downloads/windows/) (check "Add Python to PATH" during installation)
   - Install [Git for Windows](https://git-scm.com/download/win)

2. Open Command Prompt or PowerShell and run:
   ```powershell
   # Clone the repository
   git clone https://github.com/yourusername/ai-terminal.git
   cd ai-terminal
   
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variable (replace with your API key)
   [System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'your-api-key-here', [System.EnvironmentVariableTarget]::User)
   
   # Add to PATH (restart terminal after this)
   $currentPath = [Environment]::GetEnvironmentVariable('Path', [System.EnvironmentVariableTarget]::User)
   $newPath = "$pwd;" + $currentPath
   [Environment]::SetEnvironmentVariable('Path', $newPath, [System.EnvironmentVariableTarget]::User)
   ```

### Linux/macOS

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ai-terminal.git
   cd ai-terminal
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. The setup script will:
   - Create a configuration directory at `~/.ai_config/`
   - Ask for your OpenRouter API key
   - Set up a Python virtual environment
   - Install required dependencies
   - Create a symlink in `~/bin/` for easy access (Linux/macOS only)

## 🔑 Getting an API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/keys) and sign up for an account
2. Create a new API key
3. Provide this key during the setup process or set it as an environment variable:
   - **Windows (PowerShell)**:
     ```powershell
     [System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'your-api-key-here', [System.EnvironmentVariableTarget]::User)
     ```
   - **Linux/macOS**:
     ```bash
     echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc  # or ~/.zshrc
     source ~/.bashrc  # or ~/.zshrc
     ```

## 🛠️ Usage

### Interactive Mode
```bash
# Windows
python ai.py

# Linux/macOS
ai
```

### Single Command Mode
```bash
# Windows
python ai.py "how do I list files sorted by modification time?"

# Linux/macOS
ai "how do I list files sorted by modification time?"
```

### Examples
- Show running processes:
  ```
  ai "show me running processes"
  ```
- Find large files:
  ```
  ai "how do I find large files in the current directory?"
  ```
- Network information:
  ```
  ai "what's my public IP address?"
  ```
- Windows-specific:
  ```
  ai "list all services in Windows"
  ```

## ⚙️ Configuration

### File Locations
- **API Key**: 
  - Windows: `%APPDATA%\ai_terminal\.env`
  - Linux/macOS: `~/.ai_config/.env`
- **Command History**:
  - Windows: `%APPDATA%\ai_terminal\history.json`
  - Linux/macOS: `~/.ai_terminal_history.json`
- **Maximum History**: Limited to 50 most recent interactions

### Customization
You can modify the following in `ai.py`:
- `PRIMARY_MODEL`: Change the default AI model
- `FALLBACK_MODELS`: Adjust the list of fallback models
- `MAX_HISTORY`: Change the number of history items to keep

## 🔄 Updating

To update the AI Terminal Assistant:

```bash
cd ~/ai-terminal
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## ⚠️ Safety Features

- **Destructive Command Confirmation**: You'll be prompted to confirm before running potentially harmful commands
- **Command Validation**: The AI will warn you about potentially dangerous operations
- **Timeouts**: Commands that run too long will be automatically terminated

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Uses [OpenRouter.ai](https://openrouter.ai/) for AI model access
- Built with Python's standard library and [python-dotenv](https://github.com/theskumar/python-dotenv)
