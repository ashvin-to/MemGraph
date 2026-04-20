#!/bin/bash

# BaseMem Galaxy: Uninstaller
# Reverses setup.sh changes while preserving user data by default.

set -e

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DATA_DIR="$HOME/.basemem"
PURGE_DATA=0
PURGE_ENV=0
ASSUME_YES=0

usage() {
    cat <<EOF
Usage: ./uninstall.sh [options]

Options:
  --purge-data   Remove $DATA_DIR (sessions + database)
  --purge-env    Remove $BASE_DIR/venv
  -y, --yes      Skip confirmation prompts
  -h, --help     Show this help
EOF
}

confirm() {
    if [ "$ASSUME_YES" -eq 1 ]; then
        return 0
    fi

    local prompt="$1"
    read -r -p "$prompt [y/N]: " answer
    case "$answer" in
        y|Y|yes|YES) return 0 ;;
        *) return 1 ;;
    esac
}

remove_line_from_file() {
    local file="$1"
    local pattern="$2"

    [ -f "$file" ] || return 0

    local tmp
    tmp="$(mktemp)"
    awk -v pat="$pattern" 'index($0, pat) == 0 { print }' "$file" > "$tmp"
    mv "$tmp" "$file"
}

remove_if_contains_marker() {
    local file="$1"
    local marker="$2"
    [ -f "$file" ] || return 0

    if grep -q "$marker" "$file"; then
        rm -f "$file"
        echo "Removed $file"
    else
        echo "Skipped $file (content does not match BaseMem marker)"
    fi
}

for arg in "$@"; do
    case "$arg" in
        --purge-data) PURGE_DATA=1 ;;
        --purge-env) PURGE_ENV=1 ;;
        -y|--yes) ASSUME_YES=1 ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            usage
            exit 1
            ;;
    esac
done

echo "Uninstalling BaseMem Galaxy components..."

# 1. Remove global kb wrapper if it points to this installation.
if [ -f "/usr/local/bin/kb" ]; then
    if grep -q "$BASE_DIR/kb.py" "/usr/local/bin/kb"; then
        if confirm "Remove /usr/local/bin/kb?"; then
            sudo rm -f /usr/local/bin/kb
            echo "Removed /usr/local/bin/kb"
        fi
    else
        echo "Skipped /usr/local/bin/kb (does not point to this BaseMem install)"
    fi
fi

# 2. Remove generated ai-wrapper script if it is BaseMem's wrapper.
remove_if_contains_marker "$BASE_DIR/ai-wrapper.sh" "Universal AI memory proxy for BaseMem planets and moons"

# 3. Remove injected global protocol files when they contain BaseMem marker text.
remove_if_contains_marker "$HOME/.gemini/GEMINI.md" "BaseMem Global Executive Protocol"
remove_if_contains_marker "$HOME/.codex/CODEX.md" "BaseMem Global Executive Protocol"
remove_if_contains_marker "$HOME/.claude/CLAUDE.md" "BaseMem Global Executive Protocol"
remove_if_contains_marker "$BASE_DIR/AGENTS.md" "BaseMem Global Executive Protocol"

# 4. Remove installed skill.
SKILL_DIR="$HOME/.gemini/extensions/superpowers/skills/basemem-memory"
if [ -d "$SKILL_DIR" ]; then
    if confirm "Remove BaseMem skill at $SKILL_DIR?"; then
        rm -rf "$SKILL_DIR"
        echo "Removed $SKILL_DIR"
    fi
fi

# 5. Remove shell aliases added by setup.sh.
for conf in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.config/fish/config.fish"; do
    [ -f "$conf" ] || continue
    remove_line_from_file "$conf" "$BASE_DIR/ai-wrapper.sh gemini"
    remove_line_from_file "$conf" "$BASE_DIR/ai-wrapper.sh codex"
    remove_line_from_file "$conf" "$BASE_DIR/ai-wrapper.sh claude"
    echo "Updated aliases in $conf"
done

# 6. Optional: remove virtual environment created by setup.sh.
if [ "$PURGE_ENV" -eq 1 ] && [ -d "$BASE_DIR/venv" ]; then
    if confirm "Remove $BASE_DIR/venv?"; then
        rm -rf "$BASE_DIR/venv"
        echo "Removed $BASE_DIR/venv"
    fi
fi

# 7. Optional: remove BaseMem data directory.
if [ "$PURGE_DATA" -eq 1 ] && [ -d "$DATA_DIR" ]; then
    if confirm "Remove $DATA_DIR? This deletes DB and sessions."; then
        rm -rf "$DATA_DIR"
        echo "Removed $DATA_DIR"
    fi
fi

echo "------------------------------------------------"
echo "BaseMem uninstall complete."
echo "Open a new shell session to refresh aliases/commands."
echo "------------------------------------------------"
