#!/bin/bash
# PostToolUse hook: after Claude edits a file, run the check that matches it.
# Python under model/ or tests/ -> make test; LaTeX under paper/ -> make paper.
# A failure exits 2 so the output goes back to Claude and it fixes the problem.
f=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty')
cd "$CLAUDE_PROJECT_DIR" || exit 0
case "$f" in
  */model/*.py|*/tests/*.py) cmd="make test" ;;
  */paper/*.tex|*/paper/sections/*.tex) cmd="make paper" ;;
  *) exit 0 ;;
esac
if ! out=$($cmd 2>&1); then
  echo "$cmd failed after editing $f:" >&2
  echo "$out" | tail -30 >&2
  exit 2
fi
exit 0
