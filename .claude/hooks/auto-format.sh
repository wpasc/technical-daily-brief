#!/usr/bin/env bash
# Auto-format hook for PostToolUse (Edit|Write)
file_path=$(cat | jq -r ".tool_input.file_path // empty")
if [ -z "$file_path" ] || [ ! -f "$file_path" ]; then
  exit 0
fi
case "$file_path" in
  *.py)
    ruff format "$file_path" 2>/dev/null
    ;;
esac
exit 0
