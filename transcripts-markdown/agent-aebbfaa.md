# ea6b9704-440b-478b-bcc7-3705480cec17

*December 31, 2025 at 05:02:18 AM • 5 prompts, 8 responses*

---

**You:** The user has Claude for Chrome installed and running in their Helium browser (Chromium-based). They want to know how to link Claude Code to the Claude for Chrome extension. Is there integration between Claude Code CLI and the Claude for Chrome browser extension? How do they connect or work together?

**Claude:** I'll help you find information about the integration between Claude Code and the Claude for Chrome extension. Let me fetch the official Claude Code documentation.

*🌐 https://code.claude.com/docs/en/claude_code_docs_map.md*

**Claude:** Let me search the Claude Code documentation for information about browser extensions and Claude for Chrome integration.

*🔍 Claude for Chrome extension integration with Claude Code CLI*

*🌐 https://code.claude.com/docs/en/overview.md*

**Claude:** Great! I found official documentation about this integration. Let me fetch the dedicated Chrome integration documentation.

*🌐 https://code.claude.com/docs/en/chrome*

**Claude:** Perfect! I now have comprehensive information to answer your question.

## Integration Between Claude Code CLI and Claude for Chrome

Yes, there is a direct integration between Claude Code and the Claude for Chrome browser extension. They work together seamlessly to give you AI-powered browser automation from your terminal.

### How It Works

The integration uses Chrome's **Native Messaging API** to enable communication between Claude Code (running in your terminal) and the Claude in Chrome extension. This allows Claude Code to:
- Control browser tabs and navigate pages
- Read page content and console errors
- Perform actions like clicking, typing, and form submission
- Extract and manipulate DOM state
- Record browser interactions

### Setting Up the Integration

Here are the steps to connect them:

1. **Prerequisites**
   - Google Chrome browser (note: currently only Google Chrome is supported; Brave, Arc, and other Chromium-based browsers including Helium are not yet supported)
   - Claude in Chrome extension (v1.0.36 or later)
   - Claude Code CLI (v2.0.73 or later)
   - A paid Claude plan (Pro, Team, or Enterprise)

2. **Installation**
   ```bash
   # Update Claude Code to latest version
   claude update
   ```

3. **Launch with Chrome enabled**
   ```bash
   claude --chrome
   ```
   This starts Claude Code with browser integration active.

4. **Verify the connection**
   ```bash
   /chrome
   ```
   This checks connection status and lets you configure settings.

### Important Note About Your Setup

**The integration currently works with Google Chrome only.** It is not yet supported on Brave, Arc, or other Chromium-based browsers. Since you mention using Helium (a Chromium-based browser), the Claude for Chrome extension unfortunately won't be able to connect to Claude Code through the native messaging host at this time.

If you need to use this feature, you would need to install Google Chrome as well and use that browser specifically for the Claude Code integration.

### Useful Capabilities Once Connected

- Live debugging of web apps with console error reading
- Automated form testing and filling
- Data extraction from web pages
- Multi-site workflow automation
- Testing locally hosted applications (like localhost:3000)

### Enable by Default

If you find yourself using `--chrome` frequently, you can make it the default:
```bash
/chrome
```
Then select "Enabled by default" (note: this increases context usage).

Sources:
- [Use Claude Code with Chrome (beta) - Claude Code Docs](https://code.claude.com/docs/en/chrome)
- [Claude for Chrome - Anthropic Blog](https://www.anthropic.com/news/claude-for-chrome)
- [Claude in Chrome](https://claude.com/chrome)

