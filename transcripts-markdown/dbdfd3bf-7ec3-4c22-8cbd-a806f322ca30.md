# Conversation: dbdfd3bf-7ec3-4c22-8cbd-a806f322ca30
**Date:** 
**Messages:** 45 prompts, 75 responses

---

---

**You:**

how do I configure the cosmic launcher? the popup they displays when I hit the super button

<details>
<summary>💭 Claude's Thinking</summary>

The user is asking about configuring the COSMIC launcher - this is the COSMIC desktop environment's application launcher that appears when pressing the Super key. They want to know how to configure it.

This is a straightforward question about desktop environment configuration. I should help them find where the COSMIC launcher settings are located. COSMIC is a desktop environment being developed by System76 for Pop!_OS and other distributions.

Let me check what COSMIC tools are available and help them find the configuration. I can see from the environment that they're on Linux and have cosmic-settings and cosmic-screenshot available based on the tool permissions.

I should:
1. Tell them how to access COSMIC launcher settings
2. Maybe check what configuration files exist for COSMIC

The COSMIC launcher is typically configured through:
- The COSMIC Settings application
- Configuration files in ~/.config/cosmic/

Let me help them find the settings.

</details>


**Claude:**

The COSMIC launcher can be configured through the COSMIC Settings application. Let me help you access it:


**Running Command:** Open COSMIC Settings application
```bash
cosmic-settings
```

**Tool Result:**
```
Command running in background with ID: b5f6a7d. Output is being written to: /tmp/claude/-home-mischa/tasks/b5f6a7d.output
```

<details>
<summary>💭 Claude's Thinking</summary>

I've launched the COSMIC Settings application. Now let me also check what configuration files exist for the COSMIC launcher so I can give them complete information about where settings are stored.

</details>


**Claude:**

I've opened the COSMIC Settings application for you. Once it opens, look for:
- **Desktop** section - this typically contains launcher configuration
- **Keyboard shortcuts** - to modify the Super key behavior if needed

The launcher settings are also stored in configuration files. Let me check what's available:


**Running Command:** List COSMIC config directory contents
```bash
ls -la ~/.config/cosmic/ 2>/dev/null | head -20
```

**Tool:** Glob
```json
{
  "pattern": "~/.config/cosmic/*launcher*"
}
```

**Tool Result:**
```
total 0
drwxr-xr-x 1 mischa root   1858 Dec 25 23:53 .
drwxr-xr-x 1 mischa mischa 2198 Dec 29 22:54 ..
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppletAudio
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicAppletTime
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppLibrary
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppList
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAudio
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicBackground
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicComp
drwxr-xr-x 1 mischa mischa    4 Dec 18 21:04 com.system76.CosmicEdit
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicFiles
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicIdle
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicNotifications
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanelButton
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel.Dock
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel.Panel
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPortal
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:55 com.system76.CosmicSettings
```

**Tool Result:**
```
No files found
```

<details>
<summary>💭 Claude's Thinking</summary>

The launcher configuration doesn't appear to be in a separate file with "launcher" in the name. Looking at the directory listing, I see `com.system76.CosmicAppLibrary` and `com.system76.CosmicAppList` which are likely related to the launcher. Let me check those directories and also check what the cosmic-settings output shows.

</details>


**Running Command:** Check CosmicAppLibrary config directory
```bash
ls -la ~/.config/cosmic/com.system76.CosmicAppLibrary/
```

**Running Command:** Check CosmicAppList config directory
```bash
ls -la ~/.config/cosmic/com.system76.CosmicAppList/
```

**Tool Result:**
```
total 0
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 .
drwxr-xr-x 1 mischa root   1858 Dec 25 23:53 ..
drwxr-xr-x 1 mischa mischa   88 Dec 25 22:03 v1
```

**Tool Result:**
```
total 0
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 .
drwxr-xr-x 1 mischa root   1858 Dec 25 23:53 ..
drwxr-xr-x 1 mischa mischa    0 Dec 18 20:54 v1
```

<details>
<summary>💭 Claude's Thinking</summary>

Let me check the v1 subdirectories to see what configuration files are there.

</details>


**Running Command:** Find config files in CosmicAppList
```bash
find ~/.config/cosmic/com.system76.CosmicAppList/v1 -type f -exec ls -lh {} \;
```

**Tool Result:**
```
-rw-r--r-- 1 mischa mischa 4 Dec 25 22:03 /home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/filter_top_levels
-rw-r--r-- 1 mischa mischa 2 Dec 25 22:03 /home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/favorites
-rw-r--r-- 1 mischa mischa 4 Dec 25 22:03 /home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/enable_drag_source
```

<details>
<summary>💭 Claude's Thinking</summary>

Good! I found some configuration files. Let me read these to understand what they contain, especially the favorites and filter_top_levels files which seem relevant to launcher configuration.

</details>


**Read File:** `/home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/favorites`


**Read File:** `/home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/filter_top_levels`


**Tool Result:**
```
     1→[]

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>

```

**Tool Result:**
```
     1→None

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>

```

<details>
<summary>💭 Claude's Thinking</summary>

The configuration files show:
- `favorites` is an empty list `[]`
- `filter_top_levels` is set to `None`

These are RON (Rusty Object Notation) files used by COSMIC. Now let me provide the user with complete information about how to configure the launcher.

</details>


**Claude:**

Based on what I found, here's how to configure the COSMIC launcher:

## Through COSMIC Settings (GUI)
The COSMIC Settings application I just opened should have:
- Navigate to **Desktop** or **Launcher** section
- You can configure appearance, behavior, and favorites there

## Configuration Files
The launcher settings are stored in `~/.config/cosmic/com.system76.CosmicAppList/v1/`:

- **favorites** - List of pinned/favorite applications (currently empty: `[]`)
- **filter_top_levels** - Controls top-level category filtering (currently: `None`)
- **enable_drag_source** - Whether you can drag apps from the launcher

These are RON (Rusty Object Notation) format files that you can edit directly if needed.

## What Can You Configure?
Common launcher customizations include:
- Favorite/pinned applications
- Search behavior
- Category filtering
- Visual appearance
- Grid vs list layout

Try exploring the COSMIC Settings app I opened - it should have the most user-friendly interface for these options. If you need help editing specific configuration files directly, let me know what you'd like to change!


---

**You:**

not the app list but the launcher, like action bar, cosmic action bar?

<details>
<summary>💭 Claude's Thinking</summary>

Ah, I see! The user is asking about the COSMIC launcher that appears when you press the Super key - this is likely the cosmic-launcher component, which is different from the app list. This is the command/action launcher, similar to what you might see in other desktop environments. Let me search for cosmic launcher configuration.

</details>


**Claude:**

Ah, you mean the cosmic-launcher - the command/action bar! Let me find those configuration files:


**Running Command:** Find launcher config directories
```bash
ls -la ~/.config/cosmic/ | grep -i launch
```

**Tool:** Glob
```json
{
  "pattern": "~/.config/cosmic/*aunch*"
}
```

**Tool Result:**
```

```

**Tool Result:**
```
No files found
```

<details>
<summary>💭 Claude's Thinking</summary>

Hmm, no specific launcher config found. Let me check the compositor config since the launcher is often integrated there, or check if there's a different naming convention.

</details>


**Running Command:** Check compositor config directory
```bash
ls -la ~/.config/cosmic/com.system76.CosmicComp/
```

**Running Command:** List all COSMIC config files
```bash
find ~/.config/cosmic -type f -name "*" 2>/dev/null | head -30
```

**Tool Result:**
```
total 4
drwxr-xr-x 1 mischa root    4 Dec 18 20:54 .
drwxr-xr-x 1 mischa root 1858 Dec 25 23:53 ..
drwxr-xr-x 1 mischa root  378 Dec 29 19:50 v1
```

**Tool Result:**
```
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Mode/v1/auto_switch
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Mode/v1/is_dark
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/name
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/success_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/palette
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/spacing
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/corner_radii
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/is_dark
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/is_high_contrast
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/window_hint
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/is_frosted
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/shade
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/accent_text
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/control_tint
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/text_tint
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/accent
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/accent_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/background
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/destructive
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/destructive_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/link_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/icon_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/primary
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/secondary
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/success
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/text_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/warning
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/warning_button
/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/gaps
```

<details>
<summary>💭 Claude's Thinking</summary>

Let me check the compositor config more thoroughly since the launcher keybinding is likely there.

</details>


**Running Command:** Find all compositor config files
```bash
find ~/.config/cosmic/com.system76.CosmicComp/v1 -type f -exec ls -lh {} \;
```

**Tool Result:**
```
-rw-r--r-- 1 mischa mischa 12 Dec 18 20:54 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/autotile_behavior
-rw-r--r-- 1 mischa mischa 30 Dec 18 21:02 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/keyboard_config
-rw-r--r-- 1 mischa mischa 4 Dec 18 21:06 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/autotile
-rw-r--r-- 1 mischa mischa 2 Dec 18 21:07 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/edge_snap_threshold
-rw-r--r-- 1 mischa mischa 4 Dec 18 21:07 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/focus_follows_cursor
-rw-r--r-- 1 mischa mischa 4 Dec 18 21:07 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/cursor_follows_focus
-rw-r--r-- 1 mischa mischa 275 Dec 23 21:04 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/input_default
-rw-r--r-- 1 mischa mischa 485 Dec 23 21:59 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/input_touchpad
-rw-r--r-- 1 mischa mischa 1 Dec 24 13:58 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/focus_follows_cursor_delay
-rw-r--r-- 1 mischa mischa 2 Dec 25 22:57 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/pinned_workspaces
-rw-r--r-- 1 mischa mischa 70 Dec 29 16:54 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/workspaces
-rw-r--r-- 1 mischa mischa 131 Dec 29 19:50 /home/mischa/.config/cosmic/com.system76.CosmicComp/v1/xkb_config
```

<details>
<summary>💭 Claude's Thinking</summary>

Let me check the settings directory for launcher-related settings, or look for keybindings that might relate to the launcher.

</details>


**Running Command:** Check settings config files
```bash
find ~/.config/cosmic/com.system76.CosmicSettings/v1 -type f 2>/dev/null | head -20
```

**Running Command:** Search for launcher-related directories
```bash
ls -la ~/.config/cosmic/ | grep -E "(Launcher|Action|Command)"
```

**Tool Result:**
```

```

**Tool Result:**
```

```

<details>
<summary>💭 Claude's Thinking</summary>

Let me try to see if there's any documentation or check what the cosmic-launcher process might be. Let me also check if there are keybindings configured.

</details>


**Running Command:** List all COSMIC config directories
```bash
ls -la ~/.config/cosmic/
```

**Running Command:** Check if cosmic-launcher exists
```bash
which cosmic-launcher
```

**Tool Result:**
```
/usr/bin/cosmic-launcher
```

**Tool Result:**
```
total 0
drwxr-xr-x 1 mischa root   1858 Dec 25 23:53 .
drwxr-xr-x 1 mischa mischa 2198 Dec 29 22:54 ..
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppletAudio
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicAppletTime
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppLibrary
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAppList
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicAudio
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicBackground
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicComp
drwxr-xr-x 1 mischa mischa    4 Dec 18 21:04 com.system76.CosmicEdit
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicFiles
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicIdle
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicNotifications
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanelButton
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel.Dock
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPanel.Panel
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicPortal
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:55 com.system76.CosmicSettings
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicSettingsDaemon
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicSettings.Shortcuts
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:55 com.system76.CosmicSettings.Wallpaper
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicSettings.WindowRules
drwxr-xr-x 1 mischa mischa    4 Dec 25 22:25 com.system76.CosmicStore
drwxr-xr-x 1 mischa mischa    4 Dec 18 21:04 com.system76.CosmicTerm
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicTheme.Dark
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicTheme.Dark.Builder
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicTheme.Light
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:55 com.system76.CosmicTheme.Light.Builder
drwxr-xr-x 1 mischa root      4 Dec 18 20:54 com.system76.CosmicTheme.Mode
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicTk
drwxr-xr-x 1 mischa mischa    4 Dec 18 20:54 com.system76.CosmicWorkspaces
drwxr-xr-x 1 mischa mischa    4 Dec 25 23:53 dev.edfloreshz.CosmicTweaks
drwxr-xr-x 1 mischa mischa    4 Dec 25 23:53 dev.edfloreshz.CosmicTweaks.ColorScheme
```

<details>
<summary>💭 Claude's Thinking</summary>

Great! cosmic-launcher exists. Now let me check if there's a config for it. The launcher configuration might be stored in a different location or it might be part of the compositor config. Let me also check the shortcuts config since the Super key binding would be there.

</details>


**Running Command:** Find keyboard shortcuts config
```bash
find ~/.config/cosmic/com.system76.CosmicSettings.Shortcuts -type f
```

**Running Command:** Check cosmic-launcher help info
```bash
cosmic-launcher --help 2>&1 | head -30
```

**Tool Result:**
```
/home/mischa/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/system_actions
/home/mischa/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/custom
```

**Tool Result:**
```
Usage: cosmic-launcher [COMMAND]

Commands:
  alt-tab        Toggle the launcher and switch to the alt-tab view
  shift-alt-tab  Toggle the launcher and switch to the alt-tab view
  help           Print this message or the help of the given subcommand(s)

Options:
  -h, --help     Print help
  -V, --version  Print version
```

<details>
<summary>💭 Claude's Thinking</summary>

Good! Now let me check the system_actions file which should contain the Super key binding for the launcher.

</details>


**Read File:** `/home/mischa/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/system_actions`


**Tool Result:**
```
     1→{
     2→    Terminal: "cosmic-term",
     3→}

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>

```

<details>
<summary>💭 Claude's Thinking</summary>

Interesting, the system_actions file only has Terminal configured. The launcher activation might be hardcoded or in a different location. Let me check if there are any other config files related to the launcher, or check what processes are running.

</details>


**Running Command:** Check if cosmic-launcher is running
```bash
ps aux | grep cosmic-launcher
```

**Running Command:** Check for launcher data files
```bash
find ~/.local/share/cosmic -name "*launch*" 2>/dev/null
```

**Tool Result:**
```

```

**Tool Result:**
```
mischa     32712  0.0  0.0 2136144 33140 tty1    S<l+ 19:54   0:07 cosmic-launcher
root      131704  0.0  0.0   8908  6092 ?        S<s  23:03   0:00 /usr/bin/zsh -c -l source /home/mischa/.claude/shell-snapshots/snapshot-zsh-1767077793685-8t1mvs.sh && { shopt -u extglob || setopt NO_EXTENDED_GLOB; } 2>/dev/null || true && eval 'ps aux < /dev/null | grep cosmic-launcher' && pwd -P >| /tmp/claude-7c53-cwd
root      131719  0.0  0.0   7084  4144 ?        S<   23:03   0:00 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox --exclude-dir=.venv --exclude-dir=venv cosmic-launcher
```

<details>
<summary>💭 Claude's Thinking</summary>

Good, cosmic-launcher is running. Now let me check the COSMIC settings in the GUI or look for configuration elsewhere. The launcher might store its config in a different location. Let me check if there's a cosmic-launcher specific config directory.

</details>


**Running Command:** Check system COSMIC launcher files
```bash
find /usr/share/cosmic -name "*launch*" 2>/dev/null | head -10
```

**Running Command:** Check for other cosmic config dirs
```bash
ls -la ~/.config/ | grep -i cosmic
```

**Tool Result:**
```
drwxr-xr-x 1 mischa root    1858 Dec 25 23:53 cosmic
```

**Tool Result:**
```

```

<details>
<summary>💭 Claude's Thinking</summary>

Let me try a different approach. Let me check what the actual launcher looks like by examining its desktop file or checking if there are configuration options available through COSMIC Settings. The launcher configuration might be minimal or might be accessed through the GUI settings.

</details>


**Running Command:** Check cosmic-launcher manual
```bash
man cosmic-launcher 2>&1 | head -40
```

**Tool Result:**
```
No manual entry for cosmic-launcher
```

<details>
<summary>💭 Claude's Thinking</summary>

The launcher seems to have minimal configuration exposed. Let me check the COSMIC documentation or search online for information about configuring the cosmic launcher. Let me also check if there are any RON files specifically for the launcher that I might have missed.

</details>


**Running Command:** Find RON config files
```bash
find ~/.config/cosmic -type f -name "*.ron" 2>/dev/null | head -20
```

**Running Command:** Search for launcher references in configs
```bash
grep -r "launcher" ~/.config/cosmic/ 2>/dev/null | head -10
```

**Tool Result:**
```

```

**Tool Result:**
```

```

<details>
<summary>💭 Claude's Thinking</summary>

The launcher doesn't seem to have extensive user-facing configuration files. Let me search online for information about configuring the COSMIC launcher, as this might be documented in the COSMIC desktop documentation.

</details>


**Web Search:** `cosmic launcher configure settings super key 2025`


**Tool Result:**
```
Web search results for query: "cosmic launcher configure settings super key 2025"

Links: [{"title":"Pop!_OS 24.04 LTS COSMIC Keyboard Shortcuts - System76 Support","url":"https://support.system76.com/articles/pop-cosmic-keyboard-shortcuts/"},{"title":"Change Super shortcut to open the launcher instead of workspaces · Issue #10 · pop-os/cosmic","url":"https://github.com/pop-os/cosmic/issues/10"},{"title":"2025: The Year of COSMIC — Alpha 5 Released! - System76 Blog","url":"https://blog.system76.com/post/cosmic-alpha-5-released/?s=09"},{"title":"COSMIC Updates (feat. Community) - System76 Blog","url":"https://blog.system76.com/post/cosmic-july-2024/"},{"title":"Keyboard shortcuts for both workspaces and launcher at the same time · Issue #1050 · pop-os/cosmic-epoch","url":"https://github.com/pop-os/cosmic-epoch/issues/1050"},{"title":"Exploring Cosmic Desktop: A Detailed First Look","url":"https://www.debugpoint.com/cosmic-desktop-first-look/"},{"title":"COSMIC","url":"https://system76.com/cosmic"},{"title":"Super key does not open launcher · Issue #110 · pop-os/cosmic-dock","url":"https://github.com/pop-os/cosmic-dock/issues/110"},{"title":"Option to have the super key do nothing · Issue #169 · pop-os/cosmic","url":"https://github.com/pop-os/cosmic/issues/169"},{"title":"Super key no longer opens cosmic-launcher · Issue #1511 · pop-os/cosmic-epoch","url":"https://github.com/pop-os/cosmic-epoch/issues/1511"}]

I found information about configuring the Super key for the COSMIC launcher. Here are the key findings:

## Configuring the Super Key in COSMIC

All key bindings can be modified in COSMIC Settings (Input devices > Keyboard > Keyboard shortcuts). In Pop!_OS, the Super key handles the majority of OS and window actions.

## Super Key Options

The Super key can be configured to open different views in COSMIC. You can change the window management option to make the "Super" key open workspaces instead of the launcher, though this means you no longer have any convenient way to open the launcher and start new applications using the keyboard when that option is selected.

## Suggested Alternatives

Users have proposed solutions for accessing both features, including Super opens workspaces, Super+Space opens launcher as one option.

## Recent Issues (2025)

Note that there's a recent report from January 23, 2025 that after an update, the super key no longer opens cosmic-launcher, with some users experiencing issues where all default System shortcuts no longer work despite being set.

To configure these settings, navigate to COSMIC Settings → Input devices → Keyboard → Keyboard shortcuts to customize your Super key behavior.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

<details>
<summary>💭 Claude's Thinking</summary>

Great! I found the information. The configuration is done through COSMIC Settings in the keyboard shortcuts section. Let me provide the user with a clear answer about how to configure the launcher.

</details>


**Claude:**

Perfect! The COSMIC launcher (the action bar that appears when you press Super) is configured through **COSMIC Settings**:

## How to Configure It

1. Open **COSMIC Settings** (already open from earlier)
2. Navigate to: **Input devices → Keyboard → Keyboard shortcuts**
3. Look for the Super key configuration

## Super Key Behavior Options

The Super key can be configured to:
- **Open the launcher** (cosmic-launcher) - the action/command bar
- **Open workspaces** - workspace overview

There's a trade-off: if you configure Super to open workspaces, you lose the convenient launcher access. Some users work around this by setting:
- `Super` → Opens workspaces
- `Super+Space` → Opens launcher

## Configuration Location

The keyboard shortcuts are stored in:
- `~/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/system_actions`

Currently your file only has the Terminal shortcut configured. The Super key binding would appear there once you configure it through the GUI.

## Note

There have been some recent reports (January 2025) of Super key bindings getting reset after updates, so if your shortcuts stop working, check that section in Settings to verify they're still configured.

**Sources:**
- [Pop!_OS 24.04 LTS COSMIC Keyboard Shortcuts - System76 Support](https://support.system76.com/articles/pop-cosmic-keyboard-shortcuts/)
- [Change Super shortcut to open the launcher instead of workspaces · Issue #10](https://github.com/pop-os/cosmic/issues/10)
- [Keyboard shortcuts for both workspaces and launcher at the same time · Issue #1050](https://github.com/pop-os/cosmic-epoch/issues/1050)


---

**You:**

How do I customize the look and function of cosmic launcher?

<details>
<summary>💭 Claude's Thinking</summary>

The user is asking about customizing the look and function of the cosmic-launcher (the action bar that pops up when you press Super). Let me search for more specific information about customizing the launcher itself - its appearance, behavior, search functionality, etc.

I should look for:
1. Configuration files specific to cosmic-launcher
2. Documentation on launcher customization options
3. What aspects can be customized (appearance, search behavior, plugins, etc.)

Let me search for this information.

</details>


**Web Search:** `cosmic-launcher customize appearance function configuration 2025`


**Running Command:** Search for launcher config files
```bash
find ~/.config -name "*launcher*" -o -name "*Launcher*" 2>/dev/null
```

**Tool Result:**
```
/home/mischa/.config/net.imput.helium/Default/Extensions/gejiddohjgogedgjnonbofjigllpkmbf/8.11.26.22_0/launcher
/home/mischa/.config/Antigravity/logs/20251224T134516/window1/exthost/google.antigravity-browser-launcher
/home/mischa/.config/Antigravity/logs/20251224T134516/window1/exthost/google.antigravity-browser-launcher/Browser Launcher.log
```

**Tool Result:**
```
Web search results for query: "cosmic-launcher customize appearance function configuration 2025"

Links: [{"title":"COSMIC","url":"https://system76.com/cosmic"},{"title":"Customizing COSMIC: Theming and Applications - System76 Blog","url":"https://blog.system76.com/post/customizing-cosmic-theming-and-applications/"},{"title":"GitHub - pop-os/cosmic-launcher: WIP","url":"https://github.com/pop-os/cosmic-launcher"},{"title":"Cosmic Launcher: 3D Wallpaper - Customize Your Home Screen","url":"https://cosmicwallpaper.com/"},{"title":"Releases · Cosmic-Launcher/Cosmic-Launcher","url":"https://github.com/Cosmic-Launcher/Cosmic-Launcher/releases"},{"title":"A first look at Pop!_OS Cosmic DE | Lorenzo Bettini","url":"https://www.lorenzobettini.it/2025/03/a-first-look-at-pop_os-cosmic-de/"},{"title":"COSMIC - ArchWiki","url":"https://wiki.archlinux.org/title/COSMIC"},{"title":"Cosmic Launcher · GitHub","url":"https://github.com/cosmic-launcher"},{"title":"Alpha 3: Tales from the COSMIC Desktop Environment - System76 Blog","url":"https://blog.system76.com/post/cosmic-alpha-3/"},{"title":"How to Install COSMIC Desktop on Ubuntu 24.04 [PPA] - OMG! Ubuntu","url":"https://www.omgubuntu.co.uk/2025/12/install-cosmic-desktop-ubuntu-24-04-ppa"}]

Based on the search results, here's information about customizing the cosmic-launcher appearance and configuration:

## Configuration Location

Configuration files for COSMIC applications and components can be found in subdirectories of "~/.config/cosmic". This makes it very easy to manage your dotfiles in Cosmic.

## Appearance Customization

You can customize how your system looks directly in COSMIC Settings, including changing from Dark to Light mode, choosing an accent color, and modifying the application background, interface text palette tint and neutral palette tint.

The Experimental Settings on the Appearance Settings page include custom system fonts, monospace fonts, icons, and toolkit theming.

## Launcher Configuration

The cosmic-launcher is part of the COSMIC desktop environment components. The Launcher has been updated to a major new version of libcosmic, and you can switch workspaces while the Launcher is open, which closes the Launcher.

## Development/Building

For developers, Cosmic Launcher can be built using just, and for a typical install from source, use just followed with sudo just install.

The cosmic-launcher is part of the broader COSMIC desktop environment that includes panels, applets, theming, tiling, launcher, app library, keyboard shortcuts and dynamic or pinned workspaces that are all made flexible.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

<details>
<summary>💭 Claude's Thinking</summary>

The web search didn't give me specific details about cosmic-launcher configuration files. Let me search more specifically for cosmic-launcher config files and also check the GitHub repository for documentation.

</details>


**Fetching:** https://github.com/pop-os/cosmic-launcher


**Running Command:** Check system COSMIC share directory
```bash
ls -la /usr/share/cosmic/ 2>/dev/null
```

**Tool Result:**
```
total 0
drwxr-xr-x 1 root root  800 Dec 18 20:43 .
drwxr-xr-x 1 root root 4612 Dec 29 16:16 ..
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicAppList
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicBackground
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicComp
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicPanel
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicPanel.Dock
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicPanel.Panel
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicSettings.Shortcuts
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicSettings.WindowRules
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicTheme.Dark
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicTheme.Dark.Builder
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicTheme.Light
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicTheme.Light.Builder
drwxr-xr-x 1 root root    4 Dec 18 20:43 com.system76.CosmicTheme.Mode
```

**Tool Result:**
```
# Cosmic Launcher Configuration

Based on the provided GitHub repository content, **no specific configuration options or customization features are documented**. 

The README focuses on:
- Building instructions using `just` commands
- Translation/localization via the i18n directory
- Debugging with tokio-console for async tasks

The repository describes cosmic-launcher as "Layer Shell frontend" for a backend launcher service, but offers "no details about user-facing configuration files, settings panels, or customization mechanisms."

To find configuration documentation, you would need to:
1. Check the project's issues or discussions on GitHub
2. Examine the source code in the `/src` directory
3. Review any wiki or additional documentation not shown in this overview
```

<details>
<summary>💭 Claude's Thinking</summary>

It seems like cosmic-launcher doesn't have much documented configuration. Let me search for any config files that might exist for it, and also check if there's information about what can be customized through COSMIC Settings or theme files.

</details>


**Running Command:** Check local state directories
```bash
ls -la ~/.local/state/cosmic* 2>/dev/null
```

**Web Search:** `"cosmic-launcher" plugins extensions customize search providers`


**Tool Result:**
```
/home/mischa/.local/state/cosmic:
total 0
drwxr-xr-x 1 mischa root   272 Dec 18 21:04 .
drwxr-xr-x 1 mischa root   762 Dec 29 19:54 ..
drwxr-xr-x 1 mischa root     8 Dec 18 21:01 com.system76.CosmicBackground
drwxr-xr-x 1 mischa mischa   4 Dec 18 21:04 com.system76.CosmicEdit
drwxr-xr-x 1 mischa mischa   4 Dec 18 20:54 com.system76.CosmicFiles
drwxr-xr-x 1 mischa mischa   4 Dec 18 20:55 com.system76.CosmicSettings
drwxr-xr-x 1 mischa mischa   4 Dec 18 20:54 com.system76.CosmicSettingsDaemon

/home/mischa/.local/state/cosmic-comp:
total 12
drwxr-xr-x 1 mischa mischa  88 Dec 29 16:25 .
drwxr-xr-x 1 mischa root   762 Dec 29 19:54 ..
-rw-r--r-- 1 mischa mischa  24 Dec 29 16:25 a11y_screen_filter.ron
-rw-r--r-- 1 mischa mischa  26 Dec 18 21:02 numlock.ron
-rw-r--r-- 1 mischa mischa 991 Dec 29 19:48 outputs.ron
```

**Tool Result:**
```
Web search results for query: ""cosmic-launcher" plugins extensions customize search providers"

Links: [{"title":"Launcher should be able to use gnome search providers · Issue #111 · pop-os/cosmic","url":"https://github.com/pop-os/cosmic/issues/111"},{"title":"GitHub - pop-os/cosmic-launcher: WIP","url":"https://github.com/pop-os/cosmic-launcher"},{"title":"Releases · Cosmic-Launcher/Cosmic-Launcher","url":"https://github.com/Cosmic-Launcher/Cosmic-Launcher/releases"},{"title":"Cosmic Desktop: The Basics","url":"https://content.nexus.support.com/how-to/cosmic-desktop-basics"},{"title":"Cosmic Chrome Extension - Chrome Web Store","url":"https://chromewebstore.google.com/detail/cosmic-chrome-extension/ooihoppnbephpmmpiadjmpeicihmjong"},{"title":"[Request] Customize result order · Issue #204 · pop-os/cosmic-launcher","url":"https://github.com/pop-os/cosmic-launcher/issues/204"},{"title":"COSMIC desktop - Wikipedia","url":"https://en.m.wikipedia.org/wiki/COSMIC_(desktop_environment)"},{"title":"Will a COSMIC applet happen? · GSConnect/gnome-shell-extension-gsconnect · Discussion #1703","url":"https://github.com/GSConnect/gnome-shell-extension-gsconnect/discussions/1703"},{"title":"GitHub - pop-os/gnome-shell-extension-pop-cosmic: GNOME Shell extension. See cosmic-epoch for COSMIC Epoch","url":"https://github.com/pop-os/cosmic"},{"title":"Exploring Cosmic Desktop: A Detailed First Look","url":"https://www.debugpoint.com/cosmic-desktop-first-look/"}]

I found information about the COSMIC launcher and its customization capabilities. Here's what the search revealed:

## COSMIC Launcher Overview

The COSMIC launcher is a Layer Shell frontend for the COSMIC desktop environment, which is a free and open-source desktop environment for Linux and other Unix-like operating systems developed by System76.

## Search Capabilities

The launcher/global search activates when you press the SUPER key and allows you to search by keywords to reach applications. However, the launcher currently does not search for browsing history or file contents.

There's an open feature request for the launcher to use GNOME search providers, suggesting that integration with external search providers may be a future enhancement.

## Extensions and Plugins

Regarding customization through plugins or extensions:

- COSMIC supports various extensions and plugins that can add new features or enhance existing ones
- All applets for the new COSMIC appear to be written in Rust, and extensions would need to be written in Rust rather than be a port of existing code
- You probably do not need any add-on or extensions at all because the desktop includes extensive built-in customization options

## Result Order Customization

Users have requested the ability to customize result order, such as putting open apps last or removing them from results, though this feature may still be under development.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

<details>
<summary>💭 Claude's Thinking</summary>

Let me check if there are any launcher-specific configuration directories or files in the cosmic config that I might have missed, and also look at the theme configurations since the launcher's appearance would inherit from the system theme.

</details>


**Running Command:** Find app/launcher related directories
```bash
find ~/.config/cosmic -type d | grep -i "app\|launch"
```

**Read File:** `/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/corner_radii`


**Read File:** `/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/spacing`


**Tool Result:**
```
     1→(
     2→    radius_0: (0.0, 0.0, 0.0, 0.0),
     3→    radius_xs: (2.0, 2.0, 2.0, 2.0),
     4→    radius_s: (2.0, 2.0, 2.0, 2.0),
     5→    radius_m: (2.0, 2.0, 2.0, 2.0),
     6→    radius_l: (2.0, 2.0, 2.0, 2.0),
     7→    radius_xl: (2.0, 2.0, 2.0, 2.0),
     8→)

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>

```

**Tool Result:**
```
     1→(
     2→    space_none: 0,
     3→    space_xxxs: 4,
     4→    space_xxs: 8,
     5→    space_xs: 12,
     6→    space_s: 16,
     7→    space_m: 24,
     8→    space_l: 32,
     9→    space_xl: 48,
    10→    space_xxl: 64,
    11→    space_xxxl: 128,
    12→)

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>

```

**Tool Result:**
```
/home/mischa/.config/cosmic/com.system76.CosmicAppletTime
/home/mischa/.config/cosmic/com.system76.CosmicAppletTime/v1
/home/mischa/.config/cosmic/com.system76.CosmicAppLibrary
/home/mischa/.config/cosmic/com.system76.CosmicAppLibrary/v1
/home/mischa/.config/cosmic/com.system76.CosmicAppList
/home/mischa/.config/cosmic/com.system76.CosmicAppList/v1
/home/mischa/.config/cosmic/com.system76.CosmicAppletAudio
/home/mischa/.config/cosmic/com.system76.CosmicAppletAudio/v1
```

<details>
<summary>💭 Claude's Thinking</summary>

Good, I can see the theme files use RON format. The launcher itself doesn't seem to have dedicated configuration files - it likely inherits appearance from the system theme. Let me provide a comprehensive answer about what can be customized.

</details>


**Claude:**

Based on my research, here's what you can customize with the cosmic-launcher:

## Current Customization Options

### 1. **Appearance (via System Theme)**
The launcher inherits its appearance from your COSMIC theme settings:

**Through COSMIC Settings → Appearance:**
- **Dark/Light mode** - Controls overall launcher appearance
- **Accent color** - Affects launcher highlights and selections
- **Corner radii** - Roundness of launcher window corners (stored in `~/.config/cosmic/com.system76.CosmicTheme.Dark/v1/corner_radii`)
- **Spacing** - Spacing between launcher elements (`~/.config/cosmic/com.system76.CosmicTheme.Dark/v1/spacing`)
- **Experimental settings:**
  - Custom system fonts
  - Monospace fonts
  - Icons
  - Toolkit theming

### 2. **Functionality**
Currently **limited configuration** available:
- The launcher searches applications by keywords
- Does **not** currently search browsing history or file contents
- There's a feature request for GNOME search provider integration (not yet implemented)
- Custom result ordering is requested but not yet available

### 3. **Configuration Files**
Unlike other COSMIC components, **cosmic-launcher doesn't have its own config directory** in `~/.config/cosmic/`. It appears to be controlled by:
- System theme settings (mentioned above)
- No documented plugin/extension system yet

## Current Limitations

- **No plugin system** - Extensions would need to be written in Rust and compiled into COSMIC
- **No search provider plugins** - Cannot add custom search sources
- **No result ordering customization** - Can't control how results are ranked
- **No dedicated config files** - Appearance is theme-based only

## Future Enhancements

Based on GitHub issues, the community has requested:
- GNOME search provider support
- Customizable result ordering
- More search capabilities

The cosmic-launcher is still marked as "WIP" (Work In Progress) on GitHub, so more customization options may be added in future releases.

**Sources:**
- [Customizing COSMIC: Theming and Applications - System76 Blog](https://blog.system76.com/post/customizing-cosmic-theming-and-applications/)
- [GitHub - pop-os/cosmic-launcher: WIP](https://github.com/pop-os/cosmic-launcher)
- [Launcher should be able to use gnome search providers · Issue #111](https://github.com/pop-os/cosmic/issues/111)
- [[Request] Customize result order · Issue #204](https://github.com/pop-os/cosmic-launcher/issues/204)


---

**You:**

what is the best launcher that I can still use with cosmic desktop?  something that will obey theme changes, and keep track of application installs

<details>
<summary>💭 Claude's Thinking</summary>

The user is asking about alternative launchers that work well with COSMIC desktop. They want:
1. Something that obeys theme changes (integrates with COSMIC theming)
2. Keeps track of application installs (auto-discovers new apps)

This is a good question for web search to find what launchers are compatible with COSMIC and what the community recommends. I should search for information about:
- Alternative launchers that work with COSMIC
- Launchers that support Wayland (since COSMIC uses Wayland)
- How well they integrate with theming

Let me search for this information.

</details>


**Web Search:** `best application launcher COSMIC desktop wayland 2025`


**Web Search:** `rofi ulauncher wofi wayland launcher COSMIC theme integration`


**Tool Result:**
```
Web search results for query: "rofi ulauncher wofi wayland launcher COSMIC theme integration"

Links: [{"title":"App launchers – Hyprland Wiki","url":"https://wiki.hypr.land/Useful-Utilities/App-Launchers/"},{"title":"Ubuntu Manpage: wofi - A rofi inspired launcher for wlroots compositors","url":"https://manpages.ubuntu.com/manpages/jammy/man1/wofi.1.html"},{"title":"App Launchers in KDE || Timothy Miller","url":"https://timothymiller.dev/posts/2024/app-launchers-in-kde/"},{"title":"chmouel/mounch - a simple WOFI/ROFI launcher","url":"https://github.com/chmouel/mounch"},{"title":"Wayland Application Launchers: Stick with Rofi — The Negation --- @vst's Personal Website","url":"https://www.thenegation.com/posts/wayland-app-launchers-rofi/"},{"title":"GitHub - onagre-launcher/onagre: A general purpose application launcher for X and wayland inspired by rofi/wofi and alfred","url":"https://github.com/onagre-launcher/onagre"},{"title":"Share alternative app launchers for Hyprland/Wayland - All WMs - EndeavourOS","url":"https://forum.endeavouros.com/t/share-alternative-app-launchers-for-hyprland-wayland/71208"},{"title":"wofi: A rofi inspired launcher for wlroots compositors | Man Page | Commands | wofi | ManKier","url":"https://www.mankier.com/1/wofi"},{"title":"We are Wayland now!","url":"https://wearewaylandnow.com/"},{"title":"App Launchers | Hyprland Wiki","url":"https://wiki.hypr.land/hyprland-wiki/pages/Useful-Utilities/App-Launchers/"}]

I've completed the search for application launchers on Wayland with COSMIC theme integration. Here's what I found:

## Application Launchers for Wayland

**Wofi** is a GTK-based customizable launcher for Wayland, while **Rofi** is a window switcher and application launcher that now supports Wayland since 2025. Wofi is described as "a rofi inspired menu program for wlroots compositors" that is highly customizable through CSS styling.

**Ulauncher** experienced stability issues on KDE with Wayland, and being built with GTK (a Gnome project), it works better on Gnome systems.

## Wayland Support Status

Rofi's main issue was lack of native Wayland support, leading users to Wofi (a Wayland fork), though Wofi is apparently no longer actively maintained. Wayland support for Rofi is currently provided through a fork called rofi-wayland.

## Theme Customization

Onagre, another launcher inspired by rofi/wofi, offers a "fully customizable theme". Wofi supports CSS styling with a default CSS file at $XDG_CONFIG_HOME/wofi/style.css.

## COSMIC Desktop

COSMIC Desktop is listed among desktop environments as being in Alpha stage, with Rofi, Ulauncher, and Wofi all mentioned as available application launchers on Wayland.

**Note:** The search results didn't reveal specific information about COSMIC theme integration with these launchers. COSMIC Desktop being in Alpha suggests theme integration may still be under development.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

**Tool Result:**
```
Web search results for query: "best application launcher COSMIC desktop wayland 2025"

Links: [{"title":"COSMIC - ArchWiki","url":"https://wiki.archlinux.org/title/COSMIC"},{"title":"COSMIC","url":"https://system76.com/cosmic"},{"title":"COSMIC desktop now available for testing on SparkyLinux | AlternativeTo","url":"https://alternativeto.net/news/2025/12/cosmic-desktop-now-available-for-testing-on-sparkylinux/"},{"title":"COSMIC desktop - Wikipedia","url":"https://en.wikipedia.org/wiki/COSMIC_desktop"},{"title":"How to Install COSMIC Desktop on Ubuntu 24.04 [PPA] - OMG! Ubuntu","url":"https://www.omgubuntu.co.uk/2025/12/install-cosmic-desktop-ubuntu-24-04-ppa"},{"title":"App launchers – Hyprland Wiki","url":"https://wiki.hypr.land/Useful-Utilities/App-Launchers/"},{"title":"pop-os/cosmic-launcher | DeepWiki","url":"https://deepwiki.com/pop-os/cosmic-launcher"},{"title":"How to install COSMIC Desktop on Ubuntu step by step","url":"https://en.ubunlog.com/como-instalar-cosmic-desktop-en-ubuntu-paso-a-paso/"},{"title":"COSMIC 1.0 Released: System76's Rust desktop reaches its stable version","url":"https://en.ubunlog.com/cosmic-desktop-1-0-lanzamiento-rust-pop-os-wayland/"},{"title":"GitHub - pop-os/cosmic-epoch: Next generation Cosmic desktop environment","url":"https://github.com/pop-os/cosmic-epoch"}]

Based on the search results, here's what I found about application launchers for COSMIC desktop on Wayland in 2025:

## COSMIC's Native Launcher

COSMIC includes its own built-in application launcher called "cosmic-launcher". cosmic-launcher is the application launcher component for the COSMIC desktop environment, providing users with a search interface to find and launch applications, files, and system actions.

cosmic-launcher uses Wayland layer surfaces via SctkLayerSurfaceSettings to display over other applications, configured with exclusive keyboard interactivity and anchored to the top of the screen with a maximum width of 600 pixels.

The Launcher (activated with the Super/Windows key) acts as the command center, not only launching applications, but also allowing you to search for files, perform quick mathematical calculations, and execute terminal commands, all without taking your hands off the keyboard.

## Alternative Wayland Launchers

If you're looking for alternatives that work on Wayland (including COSMIC), several options are available:

- Rofi, a window switcher, application launcher and dmenu replacement, supports Wayland since 2025
- Fuzzel is an application launcher for wlroots-based Wayland compositors, similar to rofi's drun mode
- tofi is an extremely fast and simple yet highly customizable dmenu / rofi replacement for wlroots-based Wayland compositors that can get on screen within a single frame when configured correctly(no content)COSMIC is a Wayland-native desktop environment built in Rust that eliminates vulnerabilities like keylogging and input spoofing.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

<details>
<summary>💭 Claude's Thinking</summary>

Good, I have information about alternative launchers. Let me search for more specific information about which launchers automatically track application installs and work well on Wayland.

</details>


**Web Search:** `fuzzel tofi anyrun launcher wayland freedesktop applications`


**Running Command:** Check which launchers are installed
```bash
which rofi wofi fuzzel tofi ulauncher 2>/dev/null
```

**Tool Error:**
```
Exit code 1
rofi not found
wofi not found
fuzzel not found
tofi not found
ulauncher not found
```

**Tool Result:**
```
Web search results for query: "fuzzel tofi anyrun launcher wayland freedesktop applications"

Links: [{"title":"App launchers – Hyprland Wiki","url":"https://wiki.hypr.land/Useful-Utilities/App-Launchers/"},{"title":"dnkl/fuzzel: App launcher and fuzzy finder for Wayland, inspired by rofi(1) and dmenu(1). - Codeberg.org","url":"https://codeberg.org/dnkl/fuzzel"},{"title":"Rofi alternatives for Wayland: app launcher, window switcher and picker for Linux","url":"https://mark.stosberg.com/rofi-alternatives-for-wayland/"},{"title":"Fuzzel Launcher - Run Applications | Online Free DevTools by Hexmos - linux Commands - TLDR | Online Free DevTools by Hexmos","url":"https://hexmos.com/freedevtools/tldr/linux/fuzzel/"},{"title":"Fuzzel: A great dmenu and rofi alternative for Wayland","url":"https://mark.stosberg.com/fuzzel-a-great-dmenu-and-rofi-altenrative-for-wayland/"},{"title":"FreshPorts -- x11/fuzzel: Application launcher for wlroots-based Wayland compositors","url":"https://www.freshports.org/x11/fuzzel/?branch=2023Q3"},{"title":"Ubuntu Manpage: fuzzel - Wayland app launcher and picker","url":"https://manpages.ubuntu.com/manpages/plucky/man1/fuzzel.1.html"},{"title":"Ubuntu Manpage: fuzzel - display XDG applications in a searchable Wayland window","url":"https://manpages.ubuntu.com/manpages/noble/man1/fuzzel.1.html"},{"title":"Anyrun Alternatives: Top 9 Application Launchers & Similar Apps | AlternativeTo","url":"https://alternativeto.net/software/anyrun/"},{"title":"Application launcher - lnorg documentation","url":"https://docs.bijl.us/void-desktop-setup/graphical-session/application-launcher/"}]

I found comprehensive information about these Wayland application launchers and their relationship to freedesktop applications:

## Overview

Fuzzel is an application launcher for wlroots-based Wayland compositors, similar to rofi's drun mode.(no content)tofi is an extremely fast and simple yet highly customizable dmenu / rofi replacement for wlroots-based Wayland compositors.(no content)Anyrun is described as 'A wayland native, highly customizable runner'.

## Key Features

**Fuzzel:**
- Fuzzel is a Wayland-native application launcher and fuzzy finder, inspired by rofi and dmenu.
- Features include Wayland native, Rofi drun-like mode of operation, dmenu mode where newline separated entries are read from stdin, Emacs key bindings, Icons, and remembers frequently launched applications

**Tofi:**
- tofi provides three binaries: tofi for a dmenu-like behavior tofi-run for listing binaries and tofi-drun for displaying desktop apps.
- It's written in C and does not support icons currently.

## Freedesktop Desktop Entry Support

These launchers integrate with the freedesktop.org Desktop Entry specification: fuzzel will pass the Desktop File ID of the chosen application (see the Desktop Entry specification) in the FUZZEL_DESKTOP_FILE_ID environment variables.

## Recommendations

For this category of tool, I recommend Fuzzel. It has a number of rofi and dmenu features, good documentation and ongoing maintenance. It's also widely packaged.


REMINDER: You MUST include the sources above in your response to the user using markdown hyperlinks.
```

<details>
<summary>💭 Claude's Thinking</summary>

Good, so none of these alternative launchers are installed. Let me provide a comprehensive recommendation to the user about the best launcher options for COSMIC desktop. Based on my research:

1. Fuzzel seems to be the best recommendation - it's Wayland-native, actively maintained, respects freedesktop standards, and automatically tracks applications
2. Rofi now has Wayland support via rofi-wayland fork
3. Tofi is very fast but lacks icons
4. Wofi is no longer actively maintained
5. Ulauncher has issues on Wayland

I should explain which one would work best with COSMIC and why, focusing on:
- Wayland compatibility (COSMIC is Wayland-only)
- Freedesktop.org desktop entry support (for auto-tracking apps)
- Theme integration possibilities
- Active maintenance

Fuzzel seems like the best choice because:
- Native Wayland support
- Actively maintained
- Supports freedesktop desktop entries (auto-tracks apps)
- Themeable via config file
- Widely packaged

However, I should note that none will perfectly integrate with COSMIC's theme system since COSMIC uses its own theming system, but they can be configured to match.

</details>


**Claude:**

Based on my research, here are the best launcher options for COSMIC desktop:

## **Top Recommendation: Fuzzel**

**Fuzzel** is the best alternative launcher for COSMIC desktop because:

✓ **Wayland-native** - COSMIC is Wayland-only, so this is essential
✓ **Auto-tracks applications** - Reads freedesktop.org Desktop Entry specifications, so it automatically discovers new installed apps
✓ **Actively maintained** - Unlike wofi which is abandoned
✓ **Remembers frequently used apps** - Learns your usage patterns
✓ **Icon support** - Shows application icons
✓ **Themeable** - Configurable colors, fonts, and appearance via config file
✓ **Widely packaged** - Easy to install on most distributions

### Install Fuzzel:
```bash
# Arch/CachyOS
sudo pacman -S fuzzel

# Ubuntu/Debian
sudo apt install fuzzel
```

### Basic theming:
Create `~/.config/fuzzel/fuzzel.ini`:
```ini
[main]
font=monospace:size=12
dpi-aware=yes
icon-theme=Your-Icon-Theme
layer=overlay

[colors]
background=1e1e2edd
text=cdd6f4ff
match=f38ba8ff
selection=45475aff
selection-text=cdd6f4ff
```

## **Alternative: Rofi (Wayland fork)**

**Rofi-wayland** is also good if you prefer more features:
- More modes (window switcher, file browser, etc.)
- Extensive theming options
- Large plugin ecosystem
- Requires the **rofi-wayland** fork for Wayland support

## **Other Options:**

- **tofi** - Extremely fast, minimal, but **no icon support**
- **wofi** - Works but **no longer maintained**
- **ulauncher** - GTK-based, has **stability issues on Wayland**

## **Theme Integration Note:**

None of these will automatically follow COSMIC's theme changes since COSMIC uses its own Rust-based theming system. However, you can:
1. Manually configure launchers to match COSMIC's colors
2. Extract COSMIC theme colors from `~/.config/cosmic/com.system76.CosmicTheme.Dark/v1/` and apply to launcher configs
3. Create scripts to sync theme changes

## **Quick Start with Fuzzel:**

After installing, bind it to a key in COSMIC Settings → Keyboard → Shortcuts:
- Command: `fuzzel`
- Key: Something like `Super+D` or `Super+Space`

**Sources:**
- [dnkl/fuzzel: App launcher for Wayland](https://codeberg.org/dnkl/fuzzel)
- [Fuzzel: A great dmenu and rofi alternative for Wayland](https://mark.stosberg.com/fuzzel-a-great-dmenu-and-rofi-altenrative-for-wayland/)
- [App launchers – Hyprland Wiki](https://wiki.hypr.land/Useful-Utilities/App-Launchers/)
- [Rofi alternatives for Wayland](https://mark.stosberg.com/rofi-alternatives-for-wayland/)
- [Wayland Application Launchers: Stick with Rofi](https://www.thenegation.com/posts/wayland-app-launchers-rofi/)


