#!/bin/bash

# INTERCEPTOR v2: Universal AI Memory Proxy
# Works for Gemini, Codex, Claude, and more.

COMMAND="$1"
TOPIC=$(basename "$PWD")

echo "🛰️  BaseMem: Memory Proxy active for '$TOPIC'..."

# 1. RUN THE AI COMMAND
# We let the AI work first. 
"$@"

# 2. DISCOVER IDENTITY (AFTER session ends)
# We look for the most recently modified JSON file in all known AI temp paths.
echo "🔍 BaseMem: Hunting for recent session logs..."

SEARCH_PATHS=(
    "$HOME/.gemini/tmp/*/chats/*.json"
    "$HOME/.codex/tmp/*.json"
    "$HOME/.claude/tmp/*.json"
    "/tmp/ai-chats/*.json"
)

# Find the newest file across all paths
NEWEST_FILE=$(ls -t ${SEARCH_PATHS[@]} 2>/dev/null | head -n 1)

if [ -z "$NEWEST_FILE" ]; then
    echo "⚠️  BaseMem: Could not find a recent log file. Skipping sync."
    exit 0
fi

# Extract the ID suffix from the filename
# Example: session-2026-04-19-a6aea9a0.json -> a6aea9a0
AGENT_ID=$(echo "$NEWEST_FILE" | rev | cut -d'-' -f1 | cut -d'.' -f2 | rev)

echo "💾 BaseMem: Found log from Agent [$AGENT_ID]. Syncing to Graph..."

# 3. PERFORM THE SYNC
kb session sync "$TOPIC" --agent-id "$AGENT_ID"

echo "✅ Galaxy Updated."
