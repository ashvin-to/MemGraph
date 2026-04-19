#!/bin/bash

# BaseMem "Shared Brain" Setup Script
# Turns your local project into a global system tool for AI agents.

echo "🌌 Initializing BaseMem Centralized Brain..."

# 1. Get the absolute path of this project
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "✓ System location: $BASE_DIR"

# 2. Set up the virtual environment
if [ ! -d "$BASE_DIR/venv" ]; then
    echo "⏳ Creating virtual environment..."
    python3 -m venv "$BASE_DIR/venv"
fi

# 3. Install core dependencies
echo "⏳ Installing lightweight dependencies..."
"$BASE_DIR/venv/bin/pip" install -q -r "$BASE_DIR/requirements.txt"

# 4. Create the Central Sessions folder
mkdir -p "$BASE_DIR/sessions"
echo "✓ Created central session store: $BASE_DIR/sessions"

# 5. Create the Global 'kb' command
echo "⏳ Creating global 'kb' command..."
WRAPPER_CONTENT="#!/bin/bash
$BASE_DIR/venv/bin/python3 $BASE_DIR/kb.py \"\$@\""

echo "$WRAPPER_CONTENT" | sudo tee /usr/local/bin/kb > /dev/null
sudo chmod +x /usr/local/bin/kb

# 6. Create the AI Proxy Wrapper
echo "⏳ Creating 'ai-proxy' for automated memory..."
cat <<EOF > "$BASE_DIR/ai-wrapper.sh"
#!/bin/bash
# BaseMem AI Proxy Wrapper
COMMAND="\$1"
TOPIC=\$(basename "\$PWD")

# 1. Run the AI
"\$@"

# 2. Auto-Discovery & Sync (After chat ends)
SEARCH_PATHS=(
    "\$HOME/.gemini/tmp/*/chats/*.json"
    "\$HOME/.codex/tmp/*.json"
    "\$HOME/.claude/tmp/*.json"
)
NEWEST_FILE=\$(ls -t \${SEARCH_PATHS[@]} 2>/dev/null | head -n 1)

if [ ! -z "\$NEWEST_FILE" ]; then
    AGENT_ID=\$(echo "\$NEWEST_FILE" | rev | cut -d'-' -f1 | cut -d'.' -f2 | rev)
    echo "💾 BaseMem: Syncing history for Agent [\$AGENT_ID]..."
    kb session sync "\$TOPIC" --agent-id "\$AGENT_ID"
fi
EOF
chmod +x "$BASE_DIR/ai-wrapper.sh"

echo "------------------------------------------------"
echo "✅ SETUP COMPLETE!"
echo "🚀 The 'kb' command is now global."
echo ""
echo "💡 MANDATORY: Add these aliases to your ~/.bashrc or config.fish:"
echo "   alias gemini='$BASE_DIR/ai-wrapper.sh gemini'"
echo "   alias codex='$BASE_DIR/ai-wrapper.sh codex'"
echo "------------------------------------------------"
