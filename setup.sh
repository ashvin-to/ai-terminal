#!/bin/bash

echo "🚀 Setting up Terminal AI Assistant..."

# Ensure script runs from repo root
cd "$(dirname "$0")"

# Create config folder
mkdir -p ~/.ai_config

# Prompt API key
echo "🔑 Get your OpenRouter API key at https://openrouter.ai/keys"
read -s -p "👇 Paste it below (input hidden): " API_KEY
echo
echo "OPENROUTER_API_KEY=\"$API_KEY\"" > ~/.ai_config/.env
echo "🔐 API key saved to ~/.ai_config/.env"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create ~/bin if it doesn’t exist
mkdir -p ~/bin

# Create wrapper script
cat > ~/bin/ai <<EOF
#!/bin/bash
source ~/ai-terminal/venv/bin/activate
python ~/ai-terminal/ai.py "\$@"
EOF

chmod +x ~/bin/ai

echo "✅ Installation complete! Run with: ai \"your prompt\""
