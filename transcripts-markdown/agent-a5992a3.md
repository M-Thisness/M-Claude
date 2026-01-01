# de73bc86-61f0-4c55-98af-c43cf612e3f6

*January 01, 2026 at 05:26:47 AM • 12 prompts, 17 responses*

---

**You:** Where does Claude Code store the full conversation history including both user prompts and Claude's responses? I can see history.jsonl has user prompts, but where are the full conversation transcripts with Claude's responses stored locally?

**Claude:** I'll help you find where Claude Code stores the full conversation history. Let me first check the Claude Code documentation and then explore your local setup.

*🌐 https://code.claude.com/docs/en/claude_code_docs_map.md*

*Tool: Glob*

*Read: `/home/mischa/.claude`*

❌ Error:
```
EISDIR: illegal operation on a directory, read
```

**Claude:** I can see there are `.jsonl` files in `/home/mischa/.claude/projects/`. Let me examine a couple of those to understand the structure:

*Read: `/home/mischa/.claude/projects/-home-mischa/31f4b3f9-e7fa-459b-acd2-ceaaa9b74d5a.jsonl`*

*Tool: Grep*

*🌐 https://code.claude.com/docs/en/memory.md*

**Claude:** Let me look at an actual conversation file to see what's stored:

*Read: `/home/mischa/.claude/projects/-home-mischa/de73bc86-61f0-4c55-98af-c43cf612e3f6.jsonl`*

*Tool: Glob*

❌ Error:
```
File content (82402 tokens) exceeds maximum allowed tokens (25000). Please use offset and limit parameters to read specific portions of the file, or use the GrepTool to search for specific content.
```

**Claude:** Perfect! I found both the global history file and the session files. Let me examine them more closely:

*Read: `/home/mischa/.claude/history.jsonl`*

*Read: `/home/mischa/.claude/projects/-home-mischa/de73bc86-61f0-4c55-98af-c43cf612e3f6.jsonl`*

**Claude:** Perfect! Now I have a complete picture. Let me examine one more file to show the structure:

*Read: `/home/mischa/.claude/debug/187e63fb-1e58-43d2-a2d6-d0aeeb7a81d0.txt`*

**Claude:** Perfect! Now I have a complete understanding. Let me provide you with a comprehensive answer.

Based on my investigation of your Claude Code setup, here's where conversation history is stored:

## Full Conversation Storage Locations

Claude Code stores conversation data in multiple locations:

### 1. **User Prompts (What You Saw)**
- **Location:** `/home/mischa/.claude/history.jsonl`
- **Content:** User prompts only, with metadata (timestamp, session ID, project path)
- **Format:** JSONL (newline-delimited JSON)

This is the file you found that contains just your prompts.

### 2. **Full Conversation Transcripts (Both Prompts & Responses)**
- **Location:** `/home/mischa/.claude/projects/-home-mischa/*.jsonl`
- **Content:** Complete conversation history with:
  - User messages
  - Claude's responses (including thinking, text, and tool usage)
  - Tool results and outputs
  - Metadata (UUIDs, timestamps, tokens, models used)
- **Format:** JSONL per session (named by session UUID)

Each `.jsonl` file in this directory represents a separate session and contains the full bidirectional conversation.

### 3. **Debug Logs (Session-Level Diagnostics)**
- **Location:** `/home/mischa/.claude/debug/*.txt`
- **Content:** Debug output for each session (named by session UUID)
- **Use:** Performance metrics, LSP manager logs, tool execution details

### Directory Structure Summary
```
~/.claude/
├── history.jsonl                    # Global prompt history
├── projects/
│   └── -home-mischa/
│       └── [SESSION-UUID].jsonl    # Full conversation transcripts
├── debug/
│   └── [SESSION-UUID].txt          # Session debug logs
├── file-history/                    # File modification tracking
├── todos/                           # Session todos
└── shell-snapshots/                 # Shell environment snapshots
```

## How to Access Full Conversations

To get your complete conversation history including Claude's responses, examine the JSONL files in `/home/mischa/.claude/projects/-home-mischa/`. Each file contains:

1. **User messages** with the full content
2. **Assistant responses** with model details (model used, token counts, cache information)
3. **Tool usage** records (bash commands, file reads, etc.)
4. **File history snapshots** tracking changes

For example, the file `/home/mischa/.claude/projects/-home-mischa/de73bc86-61f0-4c55-98af-c43cf612e3f6.jsonl` contains a complete session transcript with both your prompts and Claude's full responses including thinking, text content, and all tool interactions.

These `.jsonl` files contain all the conversation data you're looking for, not just the prompts stored in `history.jsonl`.

