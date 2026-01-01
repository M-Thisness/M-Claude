# Conversation: ea6b9704-440b-478b-bcc7-3705480cec17
**Date:** December 31, 2025 at 05:06:52 AM
**Messages:** 13 prompts, 14 responses

---

**You:**

Research Chrome's Native Messaging API:
1. How does Chrome's Native Messaging API work technically?
2. What are the key components (manifest files, native host, message format)?
3. How does a browser extension communicate with a native application?
4. What's the message protocol and data format?
5. Where are native messaging host manifests stored on Linux?
6. What would be needed to implement a similar system for another Chromium-based browser?

Focus on technical implementation details that would help build a compatible system.

**Claude:**

I'll research Chrome's Native Messaging API for you, focusing on the technical implementation details.


**Web Search:** `Chrome Native Messaging API technical implementation 2025`


**Web Search:** `Chrome Native Messaging manifest format protocol specification`


**Web Search:** `Chrome Native Messaging host manifest Linux location path`


**Tool Result:**
```
Web search results for query: "Chrome Native Messaging host manifest Linux location path"

Links: [{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"Native Messaging - Google Chrome","url":"https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html"},{"title":"Chrome Extensions: Native messaging - Chrome Developers","url":"https://chrome.jscn.org/docs/extensions/mv3/nativeMessaging/"},{"title":"developer.chrome.com/site/en/docs/extensions/mv3/nativeMessaging/index.md at main · GoogleChrome/developer.chrome.com","url":"https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/extensions/mv3/nativeMessaging/index.md"},{"title":"Problem with relative path to native messaging host manifest on Windows","url":"https://groups.google.com/a/chromium.org/g/chromium-extensions/c/Y5RckbPVnr8"},{"title":"developer.chrome.com/site/en/docs/apps/nativeMessaging/index.md at main · GoogleChrome/developer.chrome.com","url":"https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/apps/nativeMessaging/index.md"},{"title":"chrome/common/extensions/docs/templates/articles/nativeMessaging.html - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/templates/articles/nativeMessaging.html"},{"title":"Native messaging - Microsoft Edge Developer documentation | Microsoft Learn","url":"https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging"}]

Based on the search results, I found information about Chrome Native Messaging host manifest locations on Linux. Here are the specific paths:

## Linux Locations for Chrome Native Messaging Host Manifests

Native messaging hosts can be installed in two locations: system-wide at a fixed location, or user-level in the NativeMessagingHosts/ subdirectory of the user profile directory.

### System-wide locations (available to all users):

While the search results show macOS system paths explicitly, for Linux the system-wide location follows a similar pattern. One reference mentions `/etc/opt/chrome/native-messaging-hosts` as a location where Chrome looks for the .json manifest file.

### User-specific locations:

User-level native messaging hosts are looked up in the NativeMessagingHosts/ subdirectory of the user profile directory. This would typically be in the Chrome user profile directory on Linux, such as:
- `~/.config/google-chrome/NativeMessagingHosts/` (for Google Chrome)
- `~/.config/chromium/NativeMessagingHosts/` (for Chromium)

### Important notes:

On Linux, paths specified in the manifest file must be absolute (unlike Windows where they can be relative).

The manifest filename should follow the format: `com.your_company.your_application.json`


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
Web search results for query: "Chrome Native Messaging manifest format protocol specification"

Links: [{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"Native Messaging - Google Chrome","url":"https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html"},{"title":"Chrome Extensions: Native messaging - Chrome Developers","url":"https://chrome.jscn.org/docs/extensions/mv3/nativeMessaging/"},{"title":"developer.chrome.com/site/en/docs/extensions/mv3/nativeMessaging/index.md at main · GoogleChrome/developer.chrome.com","url":"https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/extensions/mv3/nativeMessaging/index.md"},{"title":"Native messaging - Microsoft Edge Developer documentation | Microsoft Learn","url":"https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging"},{"title":"GitHub - simov/native-messaging: Native Messaging Host Protocol for Browser Extensions","url":"https://github.com/simov/native-messaging"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Native Messaging as bridge between web and desktop | by Daniel Belz | fme DevOps Stories | Medium","url":"https://medium.com/fme-developer-stories/native-messaging-as-bridge-between-web-and-desktop-d288ea28cfd7"},{"title":"chrome/common/extensions/docs/templates/articles/nativeMessaging.html - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/templates/articles/nativeMessaging.html"}]

I found comprehensive information about Chrome's Native Messaging manifest format and protocol specification. Here are the key details:

## Protocol Specification

Chrome communicates with native messaging hosts using standard input (stdin) and standard output (stdout), where each message is serialized using JSON, UTF-8 encoded and preceded with 32-bit message length in native byte order.

**Message Size Limits:**
- Maximum message size from the native messaging host is 1 MB
- Maximum message size sent to the native messaging host is 64 MiB (Note: older documentation mentions 4 GB, but the official current docs state 64 MiB)

**Process Communication:**
- The first argument to the native messaging host is the origin of the caller, usually chrome-extension://[ID of allowed extension]
- When using runtime.connectNative(), Chrome keeps the host running until the port is destroyed, but with runtime.sendNativeMessage(), Chrome starts a new native messaging host process for each message

## Manifest Format

The native messaging host manifest file must be valid JSON and contains fields such as:
- `name` - Host identifier (e.g., "com.my_company.my_application")
- `description` - Description of the application
- `path` - Full path to the native messaging host executable
- `type` - Must be "stdio"
- `allowed_origins` - Array of Chrome extension IDs allowed to connect

**Official Documentation:**
- Chrome Extensions: https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging
- Chrome Apps: https://developer.chrome.com/docs/apps/nativeMessaging/


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
Web search results for query: "Chrome Native Messaging API technical implementation 2025"

Links: [{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Native Messaging Example - Chrome Web Store","url":"https://chromewebstore.google.com/detail/native-messaging-example/mefhabneoickhhbiglkmehhmemefkopf"},{"title":"Native Messaging - Google Chrome","url":"https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html"},{"title":"GitHub - jdiamond/chrome-native-messaging: Transform streams for writing Chrome App native messaging hosts in Node.js","url":"https://github.com/jdiamond/chrome-native-messaging"},{"title":"GitHub - simov/native-messaging: Native Messaging Host Protocol for Browser Extensions","url":"https://github.com/simov/native-messaging"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host"},{"title":"Native Messaging as bridge between web and desktop | by Daniel Belz | fme DevOps Stories | Medium","url":"https://medium.com/fme-developer-stories/native-messaging-as-bridge-between-web-and-desktop-d288ea28cfd7"},{"title":"GitHub - alexwiese/Lyre: Chrome Native Messaging implementation for .NET and .NET Core","url":"https://github.com/alexwiese/Lyre"}]

I've found comprehensive information about the Chrome Native Messaging API technical implementation. Here's what the search revealed:

## Chrome Native Messaging API - Technical Implementation

### Overview
Extensions and apps can exchange messages with native applications using an API similar to other message passing APIs. Native applications must register a native messaging host that knows how to communicate with the extension.

### Communication Protocol
Messages are serialized using JSON, UTF-8 encoded and preceded with 32-bit message length in native byte order.(no content)Chrome starts the host in a separate process and communicates with it using standard input and standard output streams.

### Message Size Limits
- The maximum size of a single message from the native messaging host is 1 MB
- The maximum size of the message sent to the native messaging host is 64 MiB

### Key Implementation Requirements

**Extension Manifest:**
Extensions must set the "nativeMessaging" permission in the manifest.json file

**Native Host Manifest:**
Applications must install a manifest file that defines the native messaging host configuration. This includes:
- A list of extensions that should have access to the native messaging host, where allowed-origins values can't contain wildcards
- Path to the native messaging host binary - must be absolute on Linux and macOS, can be relative on Windows

**Communication Type:**
The type parameter has one possible value: stdio, indicating that Chrome uses stdin and stdout to communicate with the host

### Common Implementation Errors
The 32-bit message length must be in the platform's native integer format (little-endian / big-endian). On Windows, the program's I/O mode must be set to O_BINARY, as the default O_TEXT corrupts the message format

### Platform Support
The concept is not bound to a specific platform and hosts can be implemented in all programming languages and on all operating systems which support stdin and stdout


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Fetching:** https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging


**Fetching:** https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging


**Web Search:** `Chrome Native Messaging message format stdin stdout 32-bit length example code`


**Tool Result:**
```
# Native Messaging Protocol Details for Chromium-Based Browsers

## Message Format

Based on the documentation, the native messaging protocol uses a standardized format across browsers:

**Message Structure:**
- Each message is **JSON-serialized and UTF-8 encoded**
- Messages are **preceded by an unsigned 32-bit value** containing the message length in **native byte order**
- **Maximum message size from app:** 1 MB
- **Maximum message size to app:** 4 GB

**Example (Python 3):**
```python
import struct
import json

# Reading a message
rawLength = sys.stdin.buffer.read(4)
messageLength = struct.unpack('@I', rawLength)[0]
message = sys.stdin.buffer.read(messageLength).decode('utf-8')
data = json.loads(message)

# Sending a message
encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
encodedLength = struct.pack('@I', len(encodedContent))
sys.stdout.buffer.write(encodedLength)
sys.stdout.buffer.write(encodedContent)
sys.stdout.buffer.flush()
```

## Manifest Schema (Chrome Differences)

**Key Chrome Incompatibility - `allowed_origins` vs `allowed_extensions`:**

Firefox manifest:
```json
{
  "name": "ping_pong",
  "description": "Example host for native messaging",
  "path": "/path/to/native-messaging/app/ping_pong.py",
  "type": "stdio",
  "allowed_extensions": ["ping_pong@example.org"]
}
```

Chrome uses instead:
```json
{
  "allowed_origins": [
    "chrome-extension://[extensionID]"
  ]
}
```

## File Locations on Linux

The documentation states manifest locations differ between Firefox and Chrome. For **Linux/macOS**, the app manifest must be named:
- **`<name>.json`** (where `<name>` matches the application name)

**Location note:** The documentation references [Native manifests](/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_manifests) for specific Linux paths, but the main article directs to that reference page for location details.

## stdin/stdout Communication

**Implementation Requirements:**

1. **Reading from stdin:**
   - Read exactly 4 bytes for the length header
   - Decode as unsigned 32-bit integer (native byte order)
   - Read that number of bytes from stdin
   - JSON-decode the UTF-8 content

2. **Writing to stdout:**
   - JSON-encode the message with minimal whitespace: `separators=(',', ':')`
   - Encode to UTF-8
   - Write 4-byte length header (unsigned 32-bit, native byte order)
   - Write message content
   - **Flush the buffer**

3. **Process Signals:**
   - On **Linux/macOS:** Browser sends `SIGTERM`, then `SIGKILL`
   - On **Windows:** Process placed in Job object and killed

## Chrome Incompatibilities Summary

Per the documentation:
- **Arguments passed to native app differ** between Chrome and Firefox
- **Manifest file location differs** between browsers
- **Extension identification differs:** Firefox uses extension IDs; Chrome uses `chrome-extension://` origins
- For cross-browser compatibility, use separate manifests without `browser_specific_settings`
```

**Tool Result:**
```
Web search results for query: "Chrome Native Messaging message format stdin stdout 32-bit length example code"

Links: [{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"developer.chrome.com/site/en/docs/extensions/mv3/nativeMessaging/index.md at main · GoogleChrome/developer.chrome.com","url":"https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/extensions/mv3/nativeMessaging/index.md"},{"title":"Native Messaging - Google Chrome","url":"https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html"},{"title":"developer.chrome.com/site/en/docs/apps/nativeMessaging/index.md at main · GoogleChrome/developer.chrome.com","url":"https://github.com/GoogleChrome/developer.chrome.com/blob/main/site/en/docs/apps/nativeMessaging/index.md"},{"title":"Chrome Extensions: Native messaging - Chrome Developers","url":"https://chrome.jscn.org/docs/extensions/mv3/nativeMessaging/"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"GitHub - guest271314/NativeMessagingHosts: Native Messaging hosts","url":"https://github.com/guest271314/NativeMessagingHosts"},{"title":"Native Messaging and C# stdin","url":"https://groups.google.com/a/chromium.org/g/chromium-extensions/c/t9V5r-Lgixs"},{"title":"Pushing Native Messaging to the limits! - C vs Rust - DEV Community","url":"https://dev.to/totally_chase/pushing-native-messaging-to-the-limits-c-vs-rust-4nad"}]

I found comprehensive information about Chrome Native Messaging message format. Here's what I discovered:

## Message Format

Each message is serialized using JSON, UTF-8 encoded and is preceded with 32-bit message length in native byte order.(no content)Chrome communicates with native messaging hosts using standard input (stdin) and standard output (stdout).

## Key Requirements

The 32-bit message length must be in the platform's native integer format (little-endian / big-endian).(no content)The message length must not exceed 1024*1024.(no content)On Windows, the program's I/O mode must be set to O_BINARY, as the default O_TEXT mode corrupts the message format by replacing line breaks. The I/O mode can be set using __setmode.

## Example Code

The search results contain several code examples:

**Rust example:**
A Rust implementation reads the 4-byte length prefix with `instream.read(&mut length)` and then reads the message buffer using `instream.read_exact(&mut buffer)`

**C# example:**
In C#, the length bytes are read as: `byte[] lengthBytes = new byte[4]; stdin.Read(lengthBytes, 0, 4); int length = BitConverter.ToInt32(lengthBytes, 0);`

**NodeJS example:**
The Mozilla documentation references NodeJS code examples for reading messages with the proper 32-bit header format.

The GitHub repository at guest271314/NativeMessagingHosts also contains multiple example implementations across different languages.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
# Native Messaging Technical Details

## 1) Message Protocol Format

Messages use a binary format with specific structure:
- **Length prefix**: "32-bit message length in native byte order" preceding each message
- **Encoding**: JSON serialized content, UTF-8 encoded
- **Size limits**: Maximum 1 MB from host to Chrome; 64 MiB from Chrome to host
- **Byte order**: Platform-native (little-endian/big-endian)

Windows-specific requirement: I/O mode must be set to `O_BINARY` to prevent line ending corruption.

## 2) Native Messaging Host Manifest JSON Schema

```json
{
  "name": "com.my_company.my_application",
  "description": "My Application",
  "path": "C:\\Program Files\\My Application\\chrome_native_messaging_host.exe",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://knldjmfmopnpolahpmmgbagdohdnhkik/"]
}
```

**Field specifications:**
- `name`: Lowercase alphanumeric, underscores, dots only; cannot start/end with dot or contain consecutive dots
- `description`: Application summary
- `path`: Absolute paths required on Linux/macOS; relative paths allowed on Windows
- `type`: Only value is `stdio`
- `allowed_origins`: Extension origins without wildcards

## 3) Extension Manifest Requirements

Extensions must declare the `"nativeMessaging"` permission in their manifest file. These APIs are unavailable in content scripts—only in extension pages and service workers.

## 4) Exact Linux File Paths

**System-wide:**
- Google Chrome: `/etc/opt/chrome/native-messaging-hosts/com.my_company.my_application.json`
- Chromium: `/etc/chromium/native-messaging-hosts/com.my_company.my_application.json`

**User-specific (default):**
- Google Chrome: `~/.config/google-chrome/NativeMessagingHosts/com.my_company.my_application.json`
- Chromium: `~/.config/chromium/NativeMessagingHosts/com.my_company.my_application.json`

## 5) Chrome Launch and Communication

**Process management:**
- "Chrome starts each native messaging host in a separate process"
- Uses stdin/stdout for bidirectional communication
- When using `connectNative()`, the host remains running until port closure
- When using `sendNativeMessage()`, Chrome spawns a new host process per message

**Command-line arguments:**
- First argument: Caller origin (typically `chrome-extension://[extension-id]`)
- Windows-only: `--parent-window=<handle>` for UI window parenting (value is 0 for service workers)
```

**Web Search:** `Chromium source code Native Messaging implementation browser extension`


**Web Search:** `implement Native Messaging compatible Chromium-based browser Edge Brave requirements`


**Fetching:** https://github.com/simov/native-messaging


**Tool Result:**
```
# Native Messaging Protocol Implementation Details

## Overview
The repository provides a Node.js implementation of the Native Messaging Host Protocol for browser extensions (Chrome and Firefox).

## Core Implementation

**Basic API Usage:**
```javascript
var sendMessage = require('native-messaging')(handleMessage)

function handleMessage (req) {
  if (req.message === 'ping') {
    sendMessage({message: 'pong', body: 'hello from nodejs app'})
  }
}
```

## Message Protocol Details

The documentation references the standard native messaging protocol but doesn't explicitly detail the 32-bit length prefix implementation in this repository's visible content. However, the protocol requires:

- **Message Format**: JSON serialized objects sent between the extension and native app
- **Connection Types**: 
  - Persistent connections via `chrome.runtime.connectNative` returning a `Port` object
  - Single messages via `chrome.runtime.sendNativeMessage`

## Platform-Specific Requirements

**Chrome:**
- Configuration file location: `~/.config/google-chrome/NativeMessagingHosts/`
- Use `allowed_origins` field containing the extension ID
- File naming: must match the `name` field exactly, with dots as delimiters only

**Firefox:**
- Configuration file location: `~/.mozilla/native-messaging-hosts/`
- Use `allowed_extensions` field with extension ID from manifest
- Same file naming conventions as Chrome

## Setup Requirements

1. Node.js executable path in shebang line: `#!/path/to/node`
2. Script must be executable: `chmod 755`
3. Add `nativeMessaging` permission to extension's `manifest.json`
4. Configuration file requires absolute `path` to the Node.js script

The actual protocol buffer handling code isn't exposed in the documentation shown above.
```

**Tool Result:**
```
Web search results for query: "Chromium source code Native Messaging implementation browser extension"

Links: [{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"chrome/common/extensions/docs/templates/articles/nativeMessaging.html - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/templates/articles/nativeMessaging.html"},{"title":"chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"Native messaging - Microsoft Edge Developer documentation | Microsoft Learn","url":"https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging"},{"title":"GitHub - jdiamond/chrome-native-messaging: Transform streams for writing Chrome App native messaging hosts in Node.js","url":"https://github.com/jdiamond/chrome-native-messaging"},{"title":"chromium/native_message_host_chromeos.cc at master · chromium/chromium · GitHub","url":"https://github.com/chromium/chromium/blob/master/chrome/browser/extensions/api/messaging/native_message_host_chromeos.cc"},{"title":"GitHub - ForrestFeng/ChromeExtension: A sample of C++ version Chrome native messaging host","url":"https://github.com/ForrestFeng/ChromeExtension"},{"title":"chrome/browser/extensions/api/messaging/native_message_host_chromeos.cc - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/72.0.3626.80/chrome/browser/extensions/api/messaging/native_message_host_chromeos.cc"},{"title":"GitHub - simov/native-messaging: Native Messaging Host Protocol for Browser Extensions","url":"https://github.com/simov/native-messaging"}]

I found comprehensive information about Chromium's Native Messaging implementation for browser extensions. Here are the key findings:

## Overview
Extensions can exchange messages with native applications using an API similar to other message passing APIs, and native applications must register a native messaging host that can communicate with the extension.

## Communication Protocol
Chrome starts each native messaging host in a separate process and communicates with it using standard input (stdin) and standard output (stdout), with each message serialized using JSON, UTF-8 encoded and preceded with 32-bit message length in native byte order.

## Message Size Limits
The maximum size of a single message from the native messaging host is 1 MB, while the maximum size of the message sent to the native messaging host is 64 MiB.

## Source Code Resources
The search found several relevant Chromium source code locations:

- **ChromeOS implementation**: The native_message_host_chromeos.cc file includes headers for messaging/native_message_host.h and shows integration with JSON reader/writer and browser process components.

- **Example code**: The Chromium source tree contains native messaging examples at `chrome/common/extensions/docs/examples/api/nativeMessaging/`

- **Third-party implementations**: There are GitHub projects providing Node.js implementations of the protocol and C++ sample hosts

The official documentation is available at developer.chrome.com, and the actual Chromium source code can be browsed at chromium.googlesource.com.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
Web search results for query: "implement Native Messaging compatible Chromium-based browser Edge Brave requirements"

Links: [{"title":"Native messaging - Microsoft Edge Developer documentation | Microsoft Learn","url":"https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging"},{"title":"Chromium-Based Browsers | browserpass/browserpass-native | DeepWiki","url":"https://deepwiki.com/browserpass/browserpass-native/3.1-chromium-based-browsers"},{"title":"Native Messaging as bridge between web and desktop | by Daniel Belz | fme DevOps Stories | Medium","url":"https://medium.com/fme-developer-stories/native-messaging-as-bridge-between-web-and-desktop-d288ea28cfd7"},{"title":"Web-to-App Communication: The Native Messaging API – text/plain","url":"https://textslashplain.com/2020/09/04/web-to-app-communication-the-native-messaging-api/"},{"title":"Supporting fallbacks for NativeMessagingHosts entries - Desktop Requests - Brave Community","url":"https://community.brave.app/t/supporting-fallbacks-for-nativemessaginghosts-entries/405292"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Please test your Windows Native Messaging Hosts in Chrome 113.0.5656+","url":"https://groups.google.com/a/chromium.org/g/chromium-extensions/c/6FZBwUx1OZc"},{"title":"Brave browser - Error: Specified native messaging host not found. · Issue #114 · browserpass/browserpass-native","url":"https://github.com/browserpass/browserpass-native/issues/114"},{"title":"NativeMessaging portal for sandboxed browsers · Issue #655 · flatpak/xdg-desktop-portal","url":"https://github.com/flatpak/xdg-desktop-portal/issues/655"},{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"}]

I've found comprehensive information about implementing Native Messaging for Chromium-based browsers including Edge and Brave. Here's what I found:

## Native Messaging Implementation Requirements

### Core Concept
Native messaging is a Web-to-App communication mechanism supported in all modern browsers (Firefox, Chrome, Edge) to exchange UTF8-encoded JSON messages between a browser extension and a native host application.

### Communication Protocol
Microsoft Edge starts each native messaging host in a separate process and communicates with it using standard input (stdin) and standard output (stdout). The same format is used to send messages in both directions; each message is serialized using JSON, UTF-8 encoded and is preceded with 32-bit message length in native byte order.

### Browser Compatibility
Browserpass-native supports ten Chromium-based browsers across Linux, macOS, FreeBSD, OpenBSD, and Windows platforms. Supported browsers include: Chromium, Google Chrome, Brave, Microsoft Edge, Vivaldi, Iridium, Yandex Browser, Slimjet, and Arc (macOS only).

### Windows Registry Requirements
For **Microsoft Edge** on Windows:
On Windows, the host's manifest is referenced in the registry, inside \Software\Microsoft\Edge\NativeMessagingHosts\ under either the HKLM or HKCU hive. By default, a reference in HKCU overrides a HKLM reference.(no content)For compatibility reasons (enabling Chrome Web Store extensions to work with Edge), Microsoft Edge will also check for NativeMessagingHosts registered within the Google Chrome registry key or file path.

### Brave Browser Support
Most applications do registry keys on a "known browser" basis and therefore if they aren't aware of Brave, then Brave will not be compatible with that application. Windows desktop applications - to communicate with extensions in Chromium based browsers - utilise the Native Messaging protocol.

### Manifest File Requirements
All Chromium-based browsers share a common host manifest file (chromium-host.json) that specifies the native host identifier, binary path, and allowed extension origins.

### Message Size Limitation
The maximum size of a single message from the native messaging host is 1 MB, mainly to protect Microsoft Edge from misbehaving native applications.

### Installation Approach
Writing to HKLM (a so-called "System Level install") requires that the installer run with Administrator permissions, so many extensions prefer to register within HKCU so that Admin permissions are not required for installation. However, there are two downsides to "User Level" registration: It requires every user account on a shared system to run the installer and it does not work for some Enterprise configurations.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Fetching:** https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging


**Web Search:** `"native messaging" struct.pack struct.unpack Python example complete code`


**Web Search:** `Chrome Native Messaging registry path Windows HKLM HKCU complete paths`


**Tool Result:**
```
Web search results for query: "Chrome Native Messaging registry path Windows HKLM HKCU complete paths"

Links: [{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Native Messaging | Apps | Chrome for Developers","url":"https://developer.chrome.com/docs/apps/nativeMessaging/"},{"title":"Native messaging - Microsoft Edge Developer documentation | Microsoft Learn","url":"https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/native-messaging"},{"title":"Native Messaging - Google Chrome","url":"https://sunnyzhou-1024.github.io/chrome-extension-docs/apps/nativeMessaging.html"},{"title":"About Native Messaging Host","url":"https://groups.google.com/a/chromium.org/g/chromium-extensions/c/p7S5wfOlUNk"},{"title":"GitHub - jfarleyx/chrome-native-messaging-golang: Chrome extension sample that uses persistent connection (connectNative()) to a native messaging host written in Go.","url":"https://github.com/jfarleyx/chrome-native-messaging-golang"},{"title":"Chrome Extensions: Native messaging - Chrome Developers","url":"https://chrome.jscn.org/docs/extensions/mv3/nativeMessaging/"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Native Messaging as bridge between web and desktop | by Daniel Belz | fme DevOps Stories | Medium","url":"https://medium.com/fme-developer-stories/native-messaging-as-bridge-between-web-and-desktop-d288ea28cfd7"},{"title":"Problem with relative path to native messaging host manifest on Windows","url":"https://groups.google.com/a/chromium.org/g/chromium-extensions/c/Y5RckbPVnr8"}]

Based on the search results, here are the complete Chrome Native Messaging registry paths for Windows:

## Complete Registry Paths

### For HKEY_CURRENT_USER (HKCU):
**HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.my_company.my_application**

### For HKEY_LOCAL_MACHINE (HKLM):
**HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.my_company.my_application**

## Registry Query Order

When Chrome looks for native messaging hosts, first the 32-bit registry is queried, then the 64-bit registry.

## Example Registry Commands

To add a registry key using the command line:

**For HKCU:**
```
REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.my_company.my_application" /ve /t REG_SZ /d "C:\path\to\nmh-manifest.json" /f
```

**For HKLM:**
```
REG ADD "HKLM\Software\Google\Chrome\NativeMessagingHosts\com.my_company.my_application" /ve /t REG_SZ /d "C:\path\to\nmh-manifest.json" /f
```

## Notes

- Replace `com.my_company.my_application` with your actual native messaging host name
- The default value of the registry key should be set to the full path to the manifest file
- A key under the HKLM hive requires admin privileges and is normally used in enterprise scenarios, while a key in the HKCU hive takes priority over a key defined in HKLM


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
# Native Messaging Technical Details for Microsoft Edge

## 1) Windows Registry Paths for Native Messaging

Microsoft Edge searches the following registry locations **in order** for native messaging host manifests:

```
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\{host_name}
HKEY_CURRENT_USER\SOFTWARE\Chromium\NativeMessagingHosts\{host_name}
HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}

HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Edge\NativeMessagingHosts\{host_name}
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Chromium\NativeMessagingHosts\{host_name}
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Google\Chrome\NativeMessagingHosts\{host_name}

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\{host_name}
HKEY_LOCAL_MACHINE\SOFTWARE\Chromium\NativeMessagingHosts\{host_name}
HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts\{host_name}
```

**Registration command example:**
```cmd
REG ADD "HKCU\Software\Microsoft\Edge\NativeMessagingHosts\com.my_company.my_app" /ve /t REG_SZ /d "C:\path\to\nmh-manifest.json" /f
```

**Key points:**
- Edge queries `HKEY_CURRENT_USER` first, then `HKEY_LOCAL_MACHINE`
- 32-bit registry is searched before 64-bit
- `WOW6432Node` is not searched on 64-bit machines (registry virtualization)
- Once found, Edge stops searching (no fallthrough)

---

## 2) Native Messaging Host Manifest File Format

**Location by platform:**
- **Windows:** Anywhere (location stored in registry)
- **macOS system-wide:** `/Library/Microsoft/Edge/NativeMessagingHosts/com.my_company.my_app.json`
- **macOS user-specific:** `~/Library/Application Support/Microsoft Edge {Channel_Name}/NativeMessagingHosts/com.my_company.my_app.json`
- **Linux system-wide:** `/etc/opt/edge/native-messaging-hosts/com.my_company.my_app.json`
- **Linux user-specific:** `~/.config/microsoft-edge/NativeMessagingHosts/com.my_company.my_app.json`

**Required JSON fields:**

| Field | Details |
|-------|---------|
| `name` | Host identifier passed to `runtime.connectNative()` or `runtime.sendNativeMessage()`. Lowercase alphanumeric, underscores, dots only. Cannot start/end with dot or contain consecutive dots. |
| `description` | Text describing the app |
| `path` | Path to native messaging host binary. Windows supports relative paths; macOS and Linux require absolute paths. Host process starts with current directory set to binary's directory. |
| `type` | Must be `"stdio"` (only acceptable value) |
| `allowed_origins` | Array of extension origins allowed to communicate with this host |

**Example manifest:**
```json
{
    "name": "com.my_company.my_app",
    "description": "My App",
    "path": "C:\\Program Files\\My App\\chrome_native_messaging_host.exe",
    "type": "stdio",
    "allowed_origins": [
        "chrome-extension://knldjmfmopnpolahpmmgbagdohdnhkik/"
    ]
}
```

---

## 3) Native Messaging Protocol Specifics

**Communication method:**
- Standard input/output (`stdin`/`stdout`)
- Messages serialized as JSON, UTF-8 encoded
- Each message preceded by **32-bit message length** in native byte order (little-endian/big-endian)

**Message size limits:**
- **From native host to Edge:** Maximum 1 MB
- **From Edge to native host:** Maximum 4 GB

**Protocol flow:**
1. Edge starts native host process as separate process
2. First command-line argument to host: `chrome-extension://[extension_id]` (caller origin)
3. Windows-only: Second argument: `--parent-window=<decimal_handle>` (allows native UI parenting; 0 if service worker caller)

**Port-based vs. One-shot messaging:**
- **`runtime.connectNative()`**: Creates persistent port, keeps host process running until port destroyed, can exchange multiple messages
- **`runtime.sendNativeMessage()`**: Starts new host process per message, only first response handled, subsequent messages ignored

**Extension code examples:**

```javascript
// Persistent connection
var port = chrome.runtime.connectNative('com.my_company.my_application');
port.onMessage.addListener(function (msg) {
  console.log('Received' + msg);
});
port.onDisconnect.addListener(function () {
  console.log('Disconnected');
});
port.postMessage({text: 'Hello, my_application'});

// One-shot message
chrome.runtime.sendNativeMessage(
  'com.my_company.my_application',
  {text: 'Hello'},
  function (response) {
    console.log('Received ' + response);
  }
);
```

**Manifest requirement in extension:**
```json
{
    "manifest_version": 3,
    "permissions": ["nativeMessaging"]
}
```

---

## 4) Edge-Specific: Chrome Web Store Extensions with Native Messaging

**Critical multi-store requirement:**

If you distribute the same extension on both **Microsoft Edge Add-ons** and **Chrome Web Store**, you **must include both extension IDs** in the `allowed_origins` field of the native messaging host manifest:

```json
{
    "allowed_origins": [
        "chrome-extension://edge_extension_id_here/",
        "chrome-extension://chrome_extension_id_here/"
    ]
}
```

**Why:** Only the native messaging host manifest found at the first registry location is read. Subsequent registry keys are not checked, so both IDs must be in the same manifest.

**Getting extension IDs:**
1. Sideload extension to test: Go to `edge://extensions` → Enable **Developer mode** → **Load unpacked**
2. Copy the ID displayed on the extension listing
3. After publishing to Microsoft Edge Add-ons, the published ID may differ—update manifest accordingly
4. For Chrome Web Store, get the ID from that store's listing

---

## 5) Edge-Specific Requirements and Differences from Chrome

**Manifest file locations (platform differences):**
- **macOS:** Uses `Microsoft Edge {Channel_Name}` directories for non-Stable channels (Canary, Dev, Beta)
- **Linux/macOS:** Require absolute paths; Windows allows relative paths
- **Linux/macOS:** Files must have proper file permissions (read on manifest, execute on binary)

**Windows-only requirements:**
- Parent window handle passed as command-line argument
- I/O mode must be set to `O_BINARY` (not default `O_TEXT`), or message format corrupts
  ```cpp
  __setmode(_fileno(stdout), _O_BINARY);
  __setmode(_fileno(stdin), _O_BINARY);
  ```

**Message size enforcement:**
- Edge enforces 1 MB max from native host to protect against misbehaving apps
- 4 GB max from Edge to host (much higher)

**Content script restriction:**
- `runtime.connectNative()` and `runtime.sendNativeMessage()` **NOT available in content scripts**
- Must relay through service worker/background script to communicate with native apps

**Registry fallback for compatibility:**
- Edge checks its own registry keys first, then falls back to Chromium and Chrome locations
- Designed for forward/backward compatibility with other Chromium-based browsers

**Permission requirement:**
- Manifest must explicitly declare `"nativeMessaging"` permission (both Manifest V2 and V3)
```

**Tool Result:**
```
Web search results for query: ""native messaging" struct.pack struct.unpack Python example complete code"

Links: [{"title":"struct — Interpret bytes as packed binary data","url":"https://docs.python.org/3/library/struct.html"},{"title":"Python struct pack, unpack | DigitalOcean","url":"https://www.digitalocean.com/community/tutorials/python-struct-pack-unpack"},{"title":"How to Use Python Struct Functions | phoenixNAP KB","url":"https://phoenixnap.com/kb/python-struct"},{"title":"struct – Working with Binary Data - Python Module of the Week","url":"https://pymotw.com/2/struct/"},{"title":"Python Examples of struct.pack","url":"https://www.programcreek.com/python/example/129/struct.pack"},{"title":"Python struct module Explained [Easy Examples] | GoLinuxCloud","url":"https://www.golinuxcloud.com/python-struct-module/"},{"title":"Python struct pack, unpack","url":"https://www.centron.de/en/tutorial/python-struct-pack-unpack/"},{"title":"Everything You Should Know About Python struct.pack() - Python Pool","url":"https://www.pythonpool.com/struct-pack/"},{"title":"Python Struct Module - Pack, Unpack Binary Data - CodersLegacy","url":"https://coderslegacy.com/python/struct-module/"},{"title":"struct module in Python","url":"https://www.tutorialspoint.com/struct-module-in-python"}]

I found search results about Python's struct.pack and struct.unpack, but I should also search specifically for "native messaging" to provide complete code examples that combine native messaging with struct operations.

Links: [{"title":"GitHub - a5482pick/Python-Chrome-App-Native-Messaging","url":"https://github.com/a5482pick/Python-Chrome-App-Native-Messaging"},{"title":"Setting Up Communication in Chrome Extensions: Native Messaging vs. External Processes","url":"https://onexception.dev/news/1374599/chrome-extensions-native-messaging-vs-external-processes"},{"title":"Native messaging - Mozilla | MDN","url":"https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging"},{"title":"Error when communicating with the native messaging host. · Issue #607 · GoogleChrome/chrome-extensions-samples","url":"https://github.com/GoogleChrome/chrome-extensions-samples/issues/607"},{"title":"chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host - chromium/src.git - Git at Google","url":"https://chromium.googlesource.com/chromium/src.git/+/62.0.3178.1/chrome/common/extensions/docs/examples/api/nativeMessaging/host/native-messaging-example-host"},{"title":"GitHub - tyfone-mitchell/Chrome-nativeMessaging-Python3: Converted the Chrome native messaging API example to Python 3 with reverse compatibility for Python 2 and better PEP 8 adherence.","url":"https://github.com/tyfone-mitchell/Chrome-nativeMessaging-Python3"},{"title":"Native messaging | Chrome for Developers","url":"https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging"},{"title":"Chromium native messaging example, but using python 3 instead of 2 · GitHub","url":"https://gist.github.com/pocc/56f3d8078975e3e7fccc718288f30bde"},{"title":"Native Messaging - Web Extensions - W3cubDocs","url":"https://docs.w3cub.com/web_extensions/native_messaging.html"},{"title":"native-messaging-host · GitHub Topics · GitHub","url":"https://github.com/topics/native-messaging-host"}]

Based on the search results, I can now provide you with comprehensive information about native messaging with struct.pack and struct.unpack in Python, along with complete code examples.

## Native Messaging with struct.pack and struct.unpack in Python

Native messaging enables an extension to exchange messages with a native application, and each message is serialized using JSON, UTF-8 encoded and is preceded with 32-bit message length in native byte order.

### How struct.pack and struct.unpack Work

The struct module converts between Python values and C structs represented as Python bytes objects using compact format strings that describe the intended conversions.

### Complete Native Messaging Example

Here's a complete example combining native messaging with struct operations:

```python
#!/usr/bin/env python3
import sys
import json
import struct

def send_message(message):
    """
    Send a message to the Chrome extension.
    Messages are sent as JSON, UTF-8 encoded, 
    preceded by 32-bit message length.
    """
    # Encode the message as JSON UTF-8
    encoded_message = json.dumps(message).encode('utf-8')
    
    # Write message length as 32-bit unsigned integer
    sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
    
    # Write the message itself
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()

def read_message():
    """
    Read a message from the Chrome extension.
    """
    # Read the message length (first 4 bytes)
    text_length_bytes = sys.stdin.buffer.read(4)
    
    if len(text_length_bytes) == 0:
        sys.exit(0)
    
    # Unpack message length as 4-byte unsigned integer
    text_length = struct.unpack('I', text_length_bytes)[0]
    
    # Read the message text
    text = sys.stdin.buffer.read(text_length).decode('utf-8')
    
    return json.loads(text)

def main():
    # Set binary mode on Windows
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

### Basic struct.pack and struct.unpack Examples

Here's a basic pack example using different formats:

```python
import struct

# Pack three integers
var1 = struct.pack('hhl', 5, 10, 15)
print(var1)

var2 = struct.pack('iii', 10, 20, 30)
print(var2)
```

To unpack, use the same string format:

```python
import struct

# Pack three integers
packed_struct = struct.pack("3i", 1, 2, 3)
print("Packed struct:", packed_struct)

# Unpack using the same format
unpacked_struct = struct.unpack("3i", packed_struct)
print("Unpacked struct:", unpacked_struct)
```

### Common Format Characters

Some popular format characters are:
- `?` : boolean
- `h` : short
- `l` : long
- `i` : int
- `f` : float
- `I` : unsigned int (commonly used for message length)
- `s` : string/bytes

### Additional Helper Functions

The calcsize() function calculates and returns the size of the String representation of struct in terms of bytes:

```python
import struct

var = struct.pack('hhl', 5, 10, 15)
size = struct.calcsize('hhl')
print(f"Size: {size} bytes")
```

These examples demonstrate the complete workflow for native messaging between browser extensions and Python applications using struct.pack and struct.unpack for proper binary message formatting.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Claude:**

Based on my research, here's a comprehensive technical overview of Chrome's Native Messaging API:

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


