# ea6b9704-440b-478b-bcc7-3705480cec17

*December 31, 2025 at 05:06:52 AM • 13 prompts, 14 responses*

---

**You:** Research Chrome's Native Messaging API:
1. How does Chrome's Native Messaging API work technically?
2. What are the key components (manifest files, native host, message format)?
3. How does a browser extension communicate with a native application?
4. What's the message protocol and data format?
5. Where are native messaging host manifests stored on Linux?
6. What would be needed to implement a similar system for another Chromium-based browser?

Focus on technical implementation details that would help build a compatible system.

**Claude:** I'll research Chrome's Native Messaging API for you, focusing on the technical implementation details.

*🔍 Chrome Native Messaging API technical implementation 2025*

*🔍 Chrome Native Messaging manifest format protocol specification*

*🔍 Chrome Native Messaging host manifest Linux location path*

*🌐 https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging*

*🌐 https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging*

*🔍 Chrome Native Messaging message format stdin stdout 32-bit length example code*

*🔍 Chromium source code Native Messaging implementation browser extension*

*🔍 implement Native Messaging compatible Chromium-based browser Edge Brave requirements*

*🌐 https://github.com/simov/native-messaging*

*🌐 https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging*

*🔍 "native messaging" struct.pack struct.unpack Python example complete code*

*🔍 Chrome Native Messaging registry path Windows HKLM HKCU complete paths*

**Claude:** Based on my research, here's a comprehensive technical overview of Chrome's Native Messaging API:

## 1. How Chrome's Native Messaging API Works Technically

Chrome's Native Messaging API enables browser extensions to communicate with native applications on the host system. Here's the technical flow:

- **Process Isolation**: Chrome starts each native messaging host in a **separate process** from the browser
- **Communication Channel**: Uses **standard input (stdin)** and **standard output (stdout)** for bidirectional communication
- **Message Serialization**: All messages are **JSON-serialized** and **UTF-8 encoded**
- **Length Prefix Protocol**: Each message is preceded by a **32-bit unsigned integer** in **native byte order** (little-endian/big-endian) indicating the message length
- **Two Connection Modes**:
  - **Persistent**: `runtime.connectNative()` creates a Port object, keeping the host process alive for multiple messages
  - **One-shot**: `runtime.sendNativeMessage()` spawns a new host process per message, only handling the first response

## 2. Key Components

### A. Extension Manifest (manifest.json)

Extensions must declare the native messaging permission:

```json
{
  "manifest_version": 3,
  "permissions": ["nativeMessaging"]
}
```

**Important**: Native messaging APIs are **NOT available in content scripts** - only in extension pages and service workers.

### B. Native Host Manifest

A JSON configuration file with these required fields:

```json
{
  "name": "com.my_company.my_application",
  "description": "My Application",
  "path": "/absolute/path/to/native-messaging-host",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://knldjmfmopnpolahpmmgbagdohdnhkik/"
  ]
}
```

**Field Requirements**:
- **name**: Lowercase alphanumeric, underscores, dots only. Cannot start/end with dot or contain consecutive dots. This is the identifier passed to `runtime.connectNative()`
- **description**: Human-readable description
- **path**: 
  - **Linux/macOS**: MUST be absolute path
  - **Windows**: Can be relative path
- **type**: MUST be `"stdio"` (only valid value)
- **allowed_origins**: Array of extension IDs. **NO wildcards allowed**

### C. Native Application Binary

The native host application receives:
- **First argument**: Caller origin (e.g., `chrome-extension://[extension-id]`)
- **Windows only**: Second argument: `--parent-window=<decimal_handle>` (for UI window parenting; 0 for service workers)

## 3. Communication Protocol

### Extension to Native Host (JavaScript):

```javascript
// Persistent connection
var port = chrome.runtime.connectNative('com.my_company.my_application');
port.onMessage.addListener(function(msg) {
  console.log('Received:', msg);
});
port.onDisconnect.addListener(function() {
  console.log('Disconnected');
});
port.postMessage({text: 'Hello, my_application'});

// One-shot message
chrome.runtime.sendNativeMessage(
  'com.my_company.my_application',
  {text: 'Hello'},
  function(response) {
    console.log('Received:', response);
  }
);
```

### Native Host Implementation (Python):

```python
#!/usr/bin/env python3
import sys
import json
import struct

def send_message(message):
    """Send message to Chrome extension"""
    # Encode as JSON UTF-8
    encoded_message = json.dumps(message).encode('utf-8')
    
    # Write 32-bit message length in native byte order
    sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
    
    # Write the message
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()

def read_message():
    """Read message from Chrome extension"""
    # Read 4-byte message length
    text_length_bytes = sys.stdin.buffer.read(4)
    
    if len(text_length_bytes) == 0:
        sys.exit(0)
    
    # Unpack as unsigned 32-bit integer
    text_length = struct.unpack('I', text_length_bytes)[0]
    
    # Read message content
    text = sys.stdin.buffer.read(text_length).decode('utf-8')
    
    return json.loads(text)

def main():
    # CRITICAL: Set binary mode on Windows
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    
    # Read incoming message
    received_message = read_message()
    
    # Process and send response
    response = {"echo": received_message}
    send_message(response)

if __name__ == '__main__':
    main()
```

**C/C++ equivalent (Windows)**:
```cpp
// MUST set binary mode on Windows
__setmode(_fileno(stdout), _O_BINARY);
__setmode(_fileno(stdin), _O_BINARY);
```

## 4. Message Protocol and Data Format

### Binary Message Format:

```
[4 bytes: uint32 length][N bytes: UTF-8 JSON message]
```

- **Byte 0-3**: Message length as 32-bit unsigned integer in **native byte order** (use `@I` format in Python struct, not `!I` network byte order)
- **Byte 4-N**: UTF-8 encoded JSON payload

### Message Size Limits:

- **From native host → Chrome**: Maximum **1 MB** (1,048,576 bytes)
- **From Chrome → native host**: Maximum **64 MiB** (67,108,864 bytes)

### Critical Implementation Details:

1. **Native byte order**: Use `struct.pack('@I', length)` in Python, NOT `struct.pack('!I', length)` (network order)
2. **Windows binary mode**: Default `O_TEXT` mode corrupts messages by replacing line breaks
3. **Flush stdout**: Always flush after writing to ensure immediate delivery
4. **No line buffering**: Messages are binary protocol, not line-based

## 5. Native Messaging Host Manifest Storage on Linux

### System-wide locations:

```
/etc/opt/chrome/native-messaging-hosts/com.my_company.my_application.json
/etc/chromium/native-messaging-hosts/com.my_company.my_application.json
```

### User-specific locations (preferred for non-admin installs):

```
~/.config/google-chrome/NativeMessagingHosts/com.my_company.my_application.json
~/.config/chromium/NativeMessagingHosts/com.my_company.my_application.json
```

**Important**: 
- Filename MUST match the `name` field in the manifest exactly
- The native binary MUST have execute permissions (`chmod +x`)
- Manifest MUST have read permissions

### Windows Registry Paths (for comparison):

**Google Chrome:**
```
HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}
HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}
```

**Registry command example:**
```cmd
REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.my_company.my_app" /ve /t REG_SZ /d "C:\path\to\manifest.json" /f
```

## 6. Implementing for Other Chromium-Based Browsers

### Browser-Specific Manifest Locations

**Microsoft Edge (Linux):**
- System: `/etc/opt/edge/native-messaging-hosts/`
- User: `~/.config/microsoft-edge/NativeMessagingHosts/`

**Microsoft Edge (Windows Registry):**
Edge searches in this order:
```
1. HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\{host_name}
2. HKEY_CURRENT_USER\SOFTWARE\Chromium\NativeMessagingHosts\{host_name}
3. HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}
4. HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Edge\NativeMessagingHosts\{host_name}
5. HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Chromium\NativeMessagingHosts\{host_name}
6. HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Google\Chrome\NativeMessagingHosts\{host_name}
7. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\{host_name}
8. HKEY_LOCAL_MACHINE\SOFTWARE\Chromium\NativeMessagingHosts\{host_name}
9. HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}
```

**Brave, Vivaldi, etc.** typically use:
- Linux: `~/.config/{browser-name}/NativeMessagingHosts/`
- Windows: Similar registry fallback pattern

### Requirements for Chromium-Based Browser Compatibility:

1. **Protocol Compatibility**: The stdin/stdout binary protocol is **identical across all Chromium browsers**

2. **Multi-Store Extension Support**: If distributing on multiple stores (Chrome Web Store + Edge Add-ons), include **all extension IDs** in the manifest:

```json
{
  "allowed_origins": [
    "chrome-extension://chrome_web_store_extension_id/",
    "chrome-extension://edge_addons_extension_id/"
  ]
}
```

3. **Multiple Browser Support**: Install manifests in multiple locations or use registry fallbacks:

```python
# Install script for multi-browser support on Linux
browsers = [
    '~/.config/google-chrome/NativeMessagingHosts/',
    '~/.config/chromium/NativeMessagingHosts/',
    '~/.config/microsoft-edge/NativeMessagingHosts/',
    '~/.config/brave/NativeMessagingHosts/',
    '~/.config/vivaldi/NativeMessagingHosts/'
]

for browser_path in browsers:
    manifest_path = os.path.join(browser_path, 'com.my_company.my_app.json')
    # Install manifest to each location
```

4. **No Code Changes Needed**: The native host binary and protocol remain **100% identical** across all Chromium-based browsers

5. **Browser Detection** (optional): Native host can identify the calling browser by parsing the first command-line argument:
   - `chrome-extension://[id]` for Chrome/Chromium
   - Same format for Edge (Edge uses `chrome-extension://` scheme too)

### Example Multi-Browser Native Host Manifest:

```json
{
  "name": "com.example.crossbrowser_app",
  "description": "Cross-browser native messaging host",
  "path": "/usr/local/bin/my_native_host",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/",
    "chrome-extension://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/",
    "chrome-extension://cccccccccccccccccccccccccccccc/"
  ]
}
```

### Testing Checklist:

- Test binary mode on Windows (verify no line ending corruption)
- Test absolute paths on Linux/macOS
- Verify message size limits (1 MB from host, 64 MiB to host)
- Test both connection types (persistent and one-shot)
- Verify permission errors are handled gracefully
- Test disconnection handling (port.onDisconnect)
- Verify JSON parsing errors don't crash the host

## Sources:

- [Native messaging | Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging)
- [Native messaging - Mozilla | MDN](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)
- [Native Messaging | Apps | Chrome for Developers](https://developer.chrome.com/docs/apps/nativeMessaging/)
- [Native Messaging - Google Chrome](https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html)
- [Native messaging - Microsoft Edge Developer documentation | Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging)
- [GitHub - simov/native-messaging: Native Messaging Host Protocol for Browser Extensions](https://github.com/simov/native-messaging)
- [Native Messaging as bridge between web and desktop | by Daniel Belz | fme DevOps Stories | Medium](https://medium.com/fme-developer-stories/native-messaging-as-bridge-between-web-and-desktop-d288ea28cfd7)
- [Web-to-App Communication: The Native Messaging API – text/plain](https://textslashplain.com/2020/09/04/web-to-app-communication-the-native-messaging-api/)
- [GitHub - GoogleChrome/developer.chrome.com](https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/extensions/mv3/nativeMessaging/index.md)

