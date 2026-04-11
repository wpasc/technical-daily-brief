#!/bin/sh
# SessionStart hook: inject engaged task context if present
input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // ""')

engaged_file="$cwd/.claude/engaged-task"

if [ -f "$engaged_file" ]; then
  task_name=$(head -1 "$engaged_file")
  task_path=$(sed -n '2p' "$engaged_file")

  # Try to read latest status entry
  status_file="$cwd/$task_path/status.md"
  status_snippet=""
  if [ -f "$status_file" ]; then
    # Grab the first ## entry (latest status)
    status_snippet=$(awk '/^## /{if(found)exit; found=1} found{print}' "$status_file" | head -5)
  fi

  context="Engaged task from previous session: $task_name"
  if [ -n "$status_snippet" ]; then
    context="$context\nLatest status:\n$status_snippet"
  fi
  context="$context\nRun /engage to reload full task context, or /engage {other task} to switch."

  printf '%s' "$context"
fi

exit 0
