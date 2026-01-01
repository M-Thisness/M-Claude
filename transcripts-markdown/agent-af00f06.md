# ea6b9704-440b-478b-bcc7-3705480cec17

*December 31, 2025 at 05:06:52 AM • 8 prompts, 10 responses*

---

**You:** Research and gather information about Helium browser:
1. What is Helium browser and its relationship to Chromium?
2. Does it support browser extensions? If so, what extension API does it use (Chrome extension API, WebExtensions)?
3. Does it support native messaging or similar APIs for communicating with external applications?
4. What's the architecture and how does it differ from standard Chrome?
5. Are there any known limitations or differences in extension support compared to Chrome?

Use web search to find official documentation, GitHub repos, or technical details about Helium browser.

**Claude:** I'll research Helium browser for you using web search to gather information about its architecture, Chromium relationship, and extension support.

*🔍 Helium browser Chromium architecture 2025*

*🔍 Helium browser extensions API support*

*🔍 Helium browser native messaging API*

*🔍 Helium browser GitHub repository documentation*

**Claude:** Let me search for more specific technical details about Helium's architecture and any known limitations.

*🔍 "Helium browser" "ungoogled-chromium" differences Chrome*

*🔍 Helium browser extension limitations compatibility issues*

*🔍 Helium browser Chrome Web Store extensions manifest v3*

**Claude:** Based on my research, here's a comprehensive overview of Helium browser:

## 1. What is Helium Browser and its Relationship to Chromium?

Helium is a privacy-focused, open-source web browser built on **ungoogled-chromium**, which is a Chromium variant with Google's tracking mechanisms and bloat removed. Helium extends ungoogled-chromium's philosophy with additional privacy features, design refinements, and user experience improvements.

**Technical Foundation:**
- Currently tracks Chromium version 141.0.7390.65
- Uses the Blink rendering engine + V8 JavaScript engine from Chromium
- Maintains compatibility with Chromium's web standards and DevTools
- Licensed under GPL-3.0 for Helium-specific code

**Key Privacy Modifications:**
- Domain substitution: replaces Google domain references with a non-existent domain (qjz9zk)
- Blocks all requests to domains containing qjz9zk and URLs with the trk: scheme
- Removes Google's telemetry and data collection mechanisms
- No built-in password manager or cloud sync (intentional for privacy)

## 2. Browser Extension Support

**Yes, Helium fully supports browser extensions** using the **Chrome Extension API** (Chromium WebExtensions).

Key features:
- **All Chromium extensions are supported** and work right away by default
- **Full Manifest V2 support** - Helium commits to keeping MV2 support "as long as possible" even as Chrome phases it out
- **Manifest V3 support** - Also supports the newer standard
- **Privacy-protected downloads** - All Chrome Web Store requests are anonymized through Helium services so Google can't track extension downloads
- **uBlock Origin** is integrated as a built-in component extension (compiled into ublock_resources.pak and loaded via ComponentLoader)

**Android version** also supports full desktop-style extensions, which is unique among mobile browsers.

## 3. Native Messaging and External Application APIs

Since Helium is based on Chromium and **doesn't break any web APIs or standards**, it should support the **Native Messaging API** that's available in standard Chromium browsers. This API allows extensions to communicate with native applications running outside the browser sandbox.

The Native Messaging API requires:
- The "nativeMessaging" permission in the extension's manifest.json
- Messages serialized as UTF8-encoded JSON with 32-bit unsigned length prefix
- Message size limits: up to 4GB to the host, 1MB from the host

There's no indication in the documentation of any Helium-specific customizations or limitations to this API.

## 4. Architecture and Differences from Standard Chrome

**Build Architecture:**
- Separate repositories for different platforms (helium-windows, helium-linux)
- Docker-based build system for Linux (`scripts/docker-build.sh`)
- Python build scripts for Windows (`python3 build.py`, `python3 package.py`)

**Key Architectural Differences:**

| Feature | Chrome | Helium |
|---------|--------|--------|
| Base | Chromium + Google services | ungoogled-chromium |
| Telemetry | Google tracking enabled | Completely removed |
| Extension Store Access | Direct to Google | Anonymized via Helium services |
| MV2 Extensions | Being phased out | Supported indefinitely |
| Default Ad Blocking | None | uBlock Origin built-in |
| Password Manager | Google account sync | None (privacy choice) |
| Translation | Google Translate built-in | Requires extension |
| Bloat | Google services included | Removed |

**Additional Features:**
- **Split view** - Open multiple web pages side-by-side in a single window
- **Native !bangs** - Quick searching across different websites from the address bar
- **Open source services** - Even the online services are open source and self-hostable

## 5. Known Limitations and Differences in Extension Support

**Limitations:**

1. **Missing Built-in Features:**
   - No built-in translation function (Google Translate removed)
   - No password manager or cloud sync
   - Some Chrome-specific features may be absent

2. **Extension Compatibility:**
   - Extensions tightly bound to Google APIs may require manual installation or fail
   - Extension conflicts can occur with multiple extensions (common to all browsers)

3. **Android-Specific Challenges:**
   - Service worker lifecycle management complexity with MV3
   - Background page limitations on mobile devices
   - Resource constraints affecting traditional extension architectures
   - Maintaining Chromium patch compatibility over time

4. **Update Dependencies:**
   - Some extensions may have issues if Chrome or external services (like Amazon) update suddenly
   - Maintaining compatibility with rapidly evolving Chromium codebase

**Advantages Over Chrome:**

- Indefinite Manifest V2 support (critical for privacy extensions like uBlock Origin)
- Privacy-protected extension downloads
- No Google tracking or data collection
- Lighter resource footprint
- Full extension support on Android

Overall, Helium appears to be a robust privacy-focused alternative to Chrome with near-complete extension compatibility, while prioritizing user privacy and removing Google's ecosystem dependencies.

---

## Sources:

- [GitHub - imputnet/helium: Private, fast, and honest web browser](https://github.com/imputnet/helium)
- [Helium Browser](https://helium.computer/)
- [Helium Browser for Android: Chromium Reborn with Extensions and Privacy at Core - LavX News](https://news.lavx.hu/article/helium-browser-for-android-chromium-reborn-with-extensions-and-privacy-at-core)
- [Is Helium the Browser Brave Was Meant to Be?](https://itsfoss.com/helium-browser/)
- [🥷 Helium Browser Review: Anonymous Browsing In 2025](https://whoerip.com/blog/helium-browser/)
- [Helium Browser: privacy-centred Chromium, without the extras | Edward Kiledjian](https://kiledjian.com/2025/10/16/helium-browser-privacycentred-chromium-without.html)
- [imputnet/helium-chromium | DeepWiki](https://deepwiki.com/imputnet/helium-chromium/1-overview)
- [Helium Services | imputnet/helium-chromium | DeepWiki](https://deepwiki.com/imputnet/helium-chromium/5-helium-customizations)
- [GitHub - jqssun/android-helium-browser: Private and secure Android browser with support for browser extensions](https://github.com/jqssun/android-helium-browser)
- [Helium Browser Brings Desktop-Style Extensions to Android, Sparking Developer Debate - BigGo News](https://biggo.com/news/202510270722_Helium_Browser_Android_Extensions_Support)
- [The best Chromium browser isn't Chrome, it's Helium](https://coywolf.com/news/productivity/the-best-chrome-browser-for-mac-windows-linux-isnt-chrome-its-helium/)
- [I tried out the Chromium-based browser 'Helium,' which comes with an ad blocker as standard - GIGAZINE](https://gigazine.net/gsc_news/en/20250927-helium-ad-blocking/)
- [GitHub - imputnet/helium-windows: Helium Browser for Windows](https://github.com/imputnet/helium-windows)
- [GitHub - imputnet/helium-linux: Helium Browser for Linux](https://github.com/imputnet/helium-linux)

