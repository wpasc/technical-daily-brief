#!/bin/sh
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Git branch (skip lock to avoid interference)
branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.checkStat=never symbolic-ref --short HEAD 2>/dev/null)
fi

# Engaged task
task=""
if [ -f "$cwd/.claude/engaged-task" ]; then
  task=$(head -1 "$cwd/.claude/engaged-task")
fi

# Shorten cwd: replace $HOME with ~
home="$HOME"
short_cwd="${cwd#$home}"
if [ "$short_cwd" != "$cwd" ]; then
  short_cwd="~$short_cwd"
fi

# Context usage indicator
ctx_part=""
if [ -n "$used" ]; then
  ctx_int=$(printf "%.0f" "$used")
  ctx_part=" | ctx:${ctx_int}%"
fi

# Git branch indicator
git_part=""
if [ -n "$branch" ]; then
  git_part=" | $branch"
fi

# Task indicator
task_part=""
if [ -n "$task" ]; then
  task_part=" | task:$task"
fi

printf "%s | %s%s%s%s" "$model" "$short_cwd" "$git_part" "$task_part" "$ctx_part"
