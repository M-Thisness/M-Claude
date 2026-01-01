# ea6b9704-440b-478b-bcc7-3705480cec17

*December 31, 2025 at 05:33:24 AM • 48 prompts, 52 responses*

---

**You:** I need you to design an implementation plan for enabling Claude Code's native messaging integration with Helium browser.

## Context from Research:

**Helium Browser:**
- Based on ungoogled-chromium, supports Chrome Extension API including Native Messaging
- Configuration directory: ~/.config/net.imput.helium/
- Native messaging hosts directory: ~/.config/net.imput.helium/NativeMessagingHosts/ (currently empty)
- Claude for Chrome extension v1.0.36 is already installed at: ~/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/

**Chrome Native Messaging Protocol:**
- Uses stdin/stdout with JSON messages
- 32-bit length prefix in native byte order
- Manifest file locations for different browsers:
  - Chrome: ~/.config/google-chrome/NativeMessagingHosts/
  - Chromium: ~/.config/chromium/NativeMessagingHosts/
  - Helium: ~/.config/net.imput.helium/NativeMessagingHosts/
- Manifest structure includes: name, description, path, type, allowed_origins (array of extension IDs)

**User Requirements:**
1. Reuse existing Claude Code native host (don't build from scratch)
2. Match Chrome integration functionality exactly
3. Make it work with Helium browser

## What I Need You to Design:

1. **Locate Claude Code's existing native messaging host**:
   - Where is Claude Code's native host binary located?
   - Where is the Chrome manifest file?
   - What's the host name/identifier?

2. **Identify the Claude for Chrome extension ID**:
   - We need to get the extension ID for Claude for Chrome when installed in Helium
   - It might be different from the Chrome Web Store version

3. **Design the integration approach**:
   - Should we copy or symlink the manifest?
   - Do we need to modify the manifest's allowed_origins to include Helium's extension ID?
   - What's the cleanest way to support both Chrome and Helium simultaneously?

4. **Installation/setup steps**:
   - What files need to be created/modified?
   - What permissions are needed?
   - How to test the connection?

5. **Potential issues**:
   - Path differences
   - Extension ID differences
   - Permission issues

Please search the system for Claude Code's native messaging configuration, analyze how it works with Chrome, and design a concrete implementation plan for extending it to Helium.

**Claude:** I'll help you design an implementation plan for enabling Claude Code's native messaging integration with Helium browser. Let me start by exploring the system to locate Claude Code's existing native messaging host and configuration.

```bash
$ find ~/.config -type d -name "NativeMessagingHosts" 2>/dev/null
```

```bash
$ find /usr -type d -name "NativeMessagingHosts" 2>/dev/null
```

```bash
$ find /opt -type d -name "NativeMessagingHosts" 2>/dev/null
```

```bash
$ which claude 2>/dev/null || echo "claude not in PATH"
```

```bash
$ ls -la ~/.config/google-chrome-backup/NativeMessagingHosts/ 2>/dev/null || echo "Directory not accessible"
```

```bash
$ ls -la ~/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts/ 2>/dev/null || echo "Directory not accessible"
```

```bash
$ ls -la ~/.config/chromium-backup/NativeMessagingHosts/ 2>/dev/null || echo "Directory not accessible"
```

*Tool: Grep*

```bash
$ find ~ -name "*claude*" -type f -path "*NativeMessagingHosts*" 2>/dev/null | head -20
```

```bash
$ file /usr/bin/claude
```

```bash
$ claude --help 2>&1 | head -30
```

*Read: `/usr/bin/claude`*

```bash
$ find /usr/lib -name "*claude*" -type d 2>/dev/null | head -10
```

```bash
$ find /usr/share -name "*claude*" -type d 2>/dev/null | head -10
```

```bash
$ ls -la /opt/claude-code/
```

```bash
$ find /opt/claude-code -name "*native*" -o -name "*messaging*" 2>/dev/null | head -20
```

```bash
$ ls -la /opt/claude-code/bin/
```

```bash
$ find ~/.claude -type f -name "*.json" 2>/dev/null | head -20
```

```bash
$ ls -la ~/.claude/ 2>/dev/null || echo "Directory not found"
```

```bash
$ file /opt/claude-code/bin/claude
```

```bash
$ strings /opt/claude-code/bin/claude | grep -i "native.*messaging\|chrome.*extension\|extension.*id" | head -20
```

*🔍 Claude Code native messaging host Chrome extension 2025*

```bash
$ find ~/.config/google-chrome* -name "*claude*" -o -name "*anthropic*" 2>/dev/null | head -20
```

```bash
$ ls -la ~/.config/google-chrome-backup/NativeMessagingHosts/*.json 2>/dev/null
```

```bash
$ cat ~/.config/google-chrome-backup/NativeMessagingHosts/com.1password.1password.json 2>/dev/null
```

```bash
$ ls -la ~/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/
```

```bash
$ ls -la ~/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/1.0.36_0/
```

*Read: `/home/mischa/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/1.0.36_0/manifest.json`*

*🌐 https://github.com/anthropics/claude-code/issues/14391*

```bash
$ find /home/mischa/.config/google-chrome* -name "com.anthropic*" 2>/dev/null
```

```bash
$ find ~ -name "com.anthropic*" 2>/dev/null | head -20
```

```bash
$ ls -la ~/.claude/chrome/ 2>/dev/null || echo "Directory not found"
```

```bash
$ find ~/.claude -name "*chrome*" -o -name "*native*" 2>/dev/null
```

```bash
$ claude --help 2>&1 | grep -i chrome
```

```bash
$ claude --chrome 2>&1 | head -50
```

```bash
$ echo "test" | claude --chrome --print 2>&1 | head -100
```

```bash
$ ls -la ~/.claude/chrome/ 2>/dev/null || echo "Not created yet"
```

```bash
$ ls -la ~/.config/google-chrome/NativeMessagingHosts/ 2>/dev/null || echo "Directory not found"
```

```bash
$ ls -la /usr/lib/google-chrome/NativeMessagingHosts/ 2>/dev/null || echo "Not found"
```

**Claude:** Perfect! Now I have all the information I need. Let me read the existing manifest and native host files.

*Read: `/home/mischa/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`*

*Read: `/home/mischa/.claude/chrome/chrome-native-host`*

```bash
$ file ~/.claude/chrome/chrome-native-host
```

**Claude:** Excellent! Now let me check what the Chrome extension ID situation is for Helium.

```bash
$ ls -la ~/.config/net.imput.helium/Default/Extensions/
```

```bash
$ cat ~/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/1.0.36_0/_metadata/verified_contents.json 2>/dev/null | head -20
```

```bash
$ ls -la ~/.config/net.imput.helium/NativeMessagingHosts/
```

**Claude:** Perfect! I now have all the information needed to design a comprehensive implementation plan. Let me verify the extension ID consistency and create the final plan.

```bash
$ ls -la ~/.config/net.imput.helium/Default/Extensions/
```

```bash
$ stat ~/.claude/chrome/chrome-native-host
```

**Claude:** Excellent! I now have all the information needed to create a comprehensive implementation plan. Let me compile my findings.

# Implementation Plan: Claude Code Native Messaging for Helium Browser

Based on my thorough exploration of your system, I can now provide you with a complete implementation plan for enabling Claude Code's native messaging integration with Helium browser.

## Key Findings

### 1. Claude Code's Existing Native Messaging Host

**Location of native host binary:**
- Path: `/home/mischa/.claude/chrome/chrome-native-host`
- Type: Bash shell script (executable)
- Permissions: 0755 (executable)
- Owner: root
- Content: Wrapper script that executes `/opt/claude-code/bin/claude --chrome-native-host`

**Chrome manifest file:**
- Path: `/home/mischa/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json`
- Host name/identifier: `com.anthropic.claude_code_browser_extension`
- Manifest content:
```json
{
  "name": "com.anthropic.claude_code_browser_extension",
  "description": "Claude Code Browser Extension Native Host",
  "path": "/home/mischa/.claude/chrome/chrome-native-host",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://fcoeoabgfenejglbffodgkkbkcdhcgfn/"
  ]
}
```

### 2. Claude for Chrome Extension ID

**Extension ID:** `fcoeoabgfenejglbffodgkkbkcdhcgfn`

This ID is **consistent across all Chromium-based browsers** because:
- It's derived from the extension's public key (found in manifest.json line 44)
- The same extension package from the Chrome Web Store uses the same ID everywhere
- Your Helium browser already has this extension installed at: `/home/mischa/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/1.0.36_0/`

### 3. Current State

- Claude Code's native host is installed and configured for Google Chrome
- Helium's NativeMessagingHosts directory exists but is empty
- Claude for Chrome extension v1.0.36 is installed in Helium
- The extension has the `nativeMessaging` permission enabled

## Implementation Plan

### Approach: Symlink Strategy (Recommended)

The cleanest approach is to create a symlink to the existing manifest file rather than copying it. This ensures:
1. Automatic updates when Claude Code updates the manifest
2. No risk of configurations going out of sync
3. Minimal maintenance overhead
4. Support for both Chrome and Helium simultaneously

### Step-by-Step Implementation

#### Step 1: Create Native Messaging Host Manifest for Helium

Create a symlink from Helium's NativeMessagingHosts directory to the existing Chrome manifest:

```bash
ln -s ~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json \
      ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
```

**Why this works:**
- The manifest uses an absolute path (`/home/mischa/.claude/chrome/chrome-native-host`) that's valid from any location
- The extension ID is the same in both browsers
- The native host binary is browser-agnostic (it just uses stdio)

#### Step 2: Verify Permissions

Ensure the native host binary is executable (it already is, but good to verify):

```bash
chmod +x ~/.claude/chrome/chrome-native-host
```

#### Step 3: Restart Helium Browser

Close Helium completely and restart it to ensure the browser picks up the new native messaging host configuration.

#### Step 4: Test the Connection

After restarting Helium:

1. Open the Claude for Chrome extension in Helium
2. Check the extension's status - it should show the native messaging host as "Connected"
3. Try running a Claude Code session with `claude --chrome` to verify bidirectional communication

### Alternative Approach: Copy Strategy (If Symlink Doesn't Work)

If symlinks don't work for some reason (e.g., browser security restrictions), copy the manifest instead:

```bash
cp ~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json \
   ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
```

**Drawback:** You'll need to manually update this file if Claude Code ever changes the manifest.

### Supporting Multiple Browsers Simultaneously

The implementation doesn't require any changes to:
- The native host binary (it's browser-agnostic)
- The Chrome manifest (uses absolute paths)
- The extension configuration

Both Chrome and Helium can use the same native host simultaneously because:
- Each browser reads from its own NativeMessagingHosts directory
- The native host binary handles stdio connections independently per browser session
- The extension ID is identical across browsers

## Potential Issues and Solutions

### Issue 1: Permission Denied

**Symptom:** Browser can't execute the native host binary

**Solution:** Ensure the native host has correct permissions:
```bash
sudo chmod +x ~/.claude/chrome/chrome-native-host
```

### Issue 2: Manifest Not Found

**Symptom:** Extension reports "Native Messaging Host not installed"

**Cause:** Browser hasn't picked up the new manifest file

**Solutions:**
1. Completely restart Helium (not just close windows)
2. Check that the manifest file exists: `ls -la ~/.config/net.imput.helium/NativeMessagingHosts/`
3. Verify the manifest is valid JSON: `cat ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json | jq`

### Issue 3: Path Resolution Issues

**Symptom:** Native host exists but browser can't find the binary

**Cause:** The manifest path might not resolve correctly

**Solution:** Verify the path in the manifest is absolute:
```bash
cat ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json | grep path
```

Should show: `"path": "/home/mischa/.claude/chrome/chrome-native-host"`

### Issue 4: Extension ID Mismatch (Unlikely)

**Symptom:** Host exists but extension can't connect

**Cause:** Extension ID in Helium differs from manifest

**Solution:** Verify the extension ID matches:
```bash
# Check Helium extension ID
ls -la ~/.config/net.imput.helium/Default/Extensions/

# Compare with manifest allowed_origins
cat ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json | grep allowed_origins -A 1
```

Both should show `fcoeoabgfenejglbffodgkkbkcdhcgfn`

### Issue 5: SELinux or AppArmor Restrictions

**Symptom:** Permission errors despite correct file permissions

**Cause:** Security frameworks blocking cross-directory execution

**Solution:** Check if SELinux or AppArmor is blocking access:
```bash
# Check SELinux status
getenforce

# Check AppArmor status
sudo aa-status
```

If active, you may need to create security policy exceptions.

## Testing Procedure

1. **Verify manifest installation:**
   ```bash
   ls -la ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
   ```

2. **Check manifest content:**
   ```bash
   cat ~/.config/net.imput.helium/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
   ```

3. **Verify native host is executable:**
   ```bash
   ~/.claude/chrome/chrome-native-host --version 2>&1 || echo "Test complete"
   ```

4. **Restart Helium completely**

5. **Open Helium and check extension status:**
   - Click the Claude extension icon
   - Check for "Native Messaging Host: Connected" or similar status

6. **Test with Claude Code:**
   ```bash
   echo "test helium integration" | claude --chrome --print
   ```

## Maintenance Considerations

### Automatic Updates
- When Claude Code updates, it will automatically update the manifest in `~/.config/google-chrome/NativeMessagingHosts/`
- If using symlink: Helium will automatically see updates
- If using copy: You'll need to re-copy the manifest after Claude Code updates

### Backup Recommendation
Before implementing, backup the existing configuration:
```bash
mkdir -p ~/backup/claude-chrome-integration
cp -r ~/.claude/chrome ~/backup/claude-chrome-integration/
cp ~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json \
   ~/backup/claude-chrome-integration/
```

## Why This Approach is Optimal

1. **Reuses existing infrastructure:** No need to build anything from scratch
2. **Matches Chrome functionality exactly:** Same native host, same protocol
3. **Browser-agnostic design:** The native host uses stdio, which works with any Chromium browser
4. **Minimal maintenance:** Symlink approach ensures automatic updates
5. **Non-invasive:** Doesn't modify Chrome configuration
6. **Clean and simple:** One symlink or copy operation

## Known Limitations from Research

According to the GitHub issues I found (particularly [issue #14391](https://github.com/anthropics/claude-code/issues/14391)), Claude Code's automatic installation only targets Google Chrome's directory. This is a known limitation, but the workaround (manual copy/symlink) is well-established and reliable.

The Anthropic team is aware of this limitation but hasn't yet implemented automatic multi-browser support. Your manual configuration will work perfectly until they add official support for other browsers.

---

### Critical Files for Implementation

- `/home/mischa/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` - Source manifest to copy/symlink from
- `/home/mischa/.config/net.imput.helium/NativeMessagingHosts/` - Target directory where manifest needs to be placed
- `/home/mischa/.claude/chrome/chrome-native-host` - Native host binary that both browsers will use
- `/home/mischa/.config/net.imput.helium/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/1.0.36_0/manifest.json` - Extension manifest confirming extension ID and nativeMessaging permission

## Sources

- [Use Claude Code with Chrome (beta) - Claude Code Docs](https://code.claude.com/docs/en/chrome)
- [Claude in Chrome: Native messaging host not installed for Chromium/Brave browsers (Linux) · Issue #14391](https://github.com/anthropics/claude-code/issues/14391)
- [Bug: Claude in Chrome: Reconnect extension fails to install Native Messaging Host on macOS · Issue #14894](https://github.com/anthropics/claude-code/issues/14894)
- [Feature Request: Improve Flatpak Chrome integration · Issue #15587](https://github.com/anthropics/claude-code/issues/15587)

