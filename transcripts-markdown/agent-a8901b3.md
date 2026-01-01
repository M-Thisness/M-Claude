# 0dc5503c-411e-4aad-a088-98dcf0539041

*January 01, 2026 at 04:57:00 AM • 5 prompts, 7 responses*

---

**You:** Where does Claude Code save its conversation history and debug logs? What files or directories are used for storing this information?

**Claude:** I'll fetch the Claude Code documentation to find information about conversation history and debug logs storage.

*🌐 https://code.claude.com/docs/en/claude_code_docs_map.md*

**Claude:** Now let me fetch the data-usage and settings documentation pages to find specific information about where conversation history and debug logs are stored.

*🌐 https://code.claude.com/docs/en/data-usage.md*

*🌐 https://code.claude.com/docs/en/settings.md*

*🌐 https://code.claude.com/docs/en/troubleshooting.md*

**Claude:** Based on the Claude Code documentation, here's where Claude Code saves its conversation history and debug logs:

## Configuration and State Storage

Claude Code stores configuration files and session data in the following directories:

### User-Level Directories
- **`~/.claude/`** - User settings directory containing:
  - `settings.json` - User settings (permissions, hooks, model overrides)
  - `agents/` - User-level subagents
  - `CLAUDE.md` - User-level memory file
- **`~/.claude.json`** - Global state file containing:
  - Theme preferences
  - OAuth session information
  - MCP server configurations
  - Allowed tools cache
  - Various caches
  - Per-project state

### Project-Level Directories
- **`.claude/`** - Project settings directory containing:
  - `settings.json` - Project settings (checked into version control)
  - `settings.local.json` - Local project settings (not committed, auto-gitignored)
  - `agents/` - Project-level subagents
- **`.mcp.json`** - Project MCP servers configuration

### Session Data and History
The documentation indicates that Claude Code stores **session data locally for up to 30 days** to enable session resumption. This is configurable via the `cleanupPeriodDays` setting in `settings.json`. However, the documentation does not specify an exact location for session conversation files.

### Enterprise Managed Settings
- **macOS**: `/Library/Application Support/ClaudeCode/`
- **Linux/WSL**: `/etc/claude-code/`
- **Windows**: `C:\ProgramData\ClaudeCode\`

## Debug Logs and Telemetry

Claude Code connects to external services for operational logging:

1. **Statsig telemetry** - Logs operational metrics (latency, reliability, usage patterns) but NOT code or file paths. Can be disabled with `DISABLE_TELEMETRY=1`
2. **Sentry error logging** - Logs operational errors with TLS encryption. Can be disabled with `DISABLE_ERROR_REPORTING=1`
3. **Bug reports** - Full conversation transcripts sent via `/bug` command are encrypted in transit and at rest

The actual local debug logs location is not explicitly documented in the public Claude Code documentation. For troubleshooting, you can:
- Run `/doctor` to check installation health
- Run `/config` to access the Settings interface
- Check logs via the `/bug` command which captures your full session

If you need access to detailed debug logs for troubleshooting, I recommend using `/feedback` to request this feature or checking if there's a `CLAUDE_CONFIG_DIR` environment variable you can set to customize the storage location.

