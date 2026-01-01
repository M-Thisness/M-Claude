# dbdfd3bf-7ec3-4c22-8cbd-a806f322ca30

* • 45 prompts, 75 responses*

---

---

**You:** how do I configure the cosmic launcher? the popup they displays when I hit the super button

<details><summary>💭 thinking</summary>
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

**Claude:** The COSMIC launcher can be configured through the COSMIC Settings application. Let me help you access it:

```bash
$ cosmic-settings
```

<details><summary>💭 thinking</summary>
I've launched the COSMIC Settings application. Now let me also check what configuration files exist for the COSMIC launcher so I can give them complete information about where settings are stored.
</details>

**Claude:** I've opened the COSMIC Settings application for you. Once it opens, look for:
- **Desktop** section - this typically contains launcher configuration
- **Keyboard shortcuts** - to modify the Super key behavior if needed

The launcher settings are also stored in configuration files. Let me check what's available:

```bash
$ ls -la ~/.config/cosmic/ 2>/dev/null | head -20
```

*Tool: Glob*

<details><summary>💭 thinking</summary>
The launcher configuration doesn't appear to be in a separate file with "launcher" in the name. Looking at the directory listing, I see `com.system76.CosmicAppLibrary` and `com.system76.CosmicAppList` which are likely related to the launcher. Let me check those directories and also check what the cosmic-settings output shows.
</details>

```bash
$ ls -la ~/.config/cosmic/com.system76.CosmicAppLibrary/
```

```bash
$ ls -la ~/.config/cosmic/com.system76.CosmicAppList/
```

<details><summary>💭 thinking</summary>
Let me check the v1 subdirectories to see what configuration files are there.
</details>

```bash
$ find ~/.config/cosmic/com.system76.CosmicAppList/v1 -type f -exec ls -lh {} \;
```

<details><summary>💭 thinking</summary>
Good! I found some configuration files. Let me read these to understand what they contain, especially the favorites and filter_top_levels files which seem relevant to launcher configuration.
</details>

*Read: `/home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/favorites`*

*Read: `/home/mischa/.config/cosmic/com.system76.CosmicAppList/v1/filter_top_levels`*

<details><summary>💭 thinking</summary>
The configuration files show:
- `favorites` is an empty list `[]`
- `filter_top_levels` is set to `None`

These are RON (Rusty Object Notation) files used by COSMIC. Now let me provide the user with complete information about how to configure the launcher.
</details>

**Claude:** Based on what I found, here's how to configure the COSMIC launcher:

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

**You:** not the app list but the launcher, like action bar, cosmic action bar?

<details><summary>💭 thinking</summary>
Ah, I see! The user is asking about the COSMIC launcher that appears when you press the Super key - this is likely the cosmic-launcher component, which is different from the app list. This is the command/action launcher, similar to what you might see in other desktop environments. Let me search for cosmic launcher configuration.
</details>

**Claude:** Ah, you mean the cosmic-launcher - the command/action bar! Let me find those configuration files:

```bash
$ ls -la ~/.config/cosmic/ | grep -i launch
```

*Tool: Glob*

<details><summary>💭 thinking</summary>
Hmm, no specific launcher config found. Let me check the compositor config since the launcher is often integrated there, or check if there's a different naming convention.
</details>

```bash
$ ls -la ~/.config/cosmic/com.system76.CosmicComp/
```

```bash
$ find ~/.config/cosmic -type f -name "*" 2>/dev/null | head -30
```

<details><summary>💭 thinking</summary>
Let me check the compositor config more thoroughly since the launcher keybinding is likely there.
</details>

```bash
$ find ~/.config/cosmic/com.system76.CosmicComp/v1 -type f -exec ls -lh {} \;
```

<details><summary>💭 thinking</summary>
Let me check the settings directory for launcher-related settings, or look for keybindings that might relate to the launcher.
</details>

```bash
$ find ~/.config/cosmic/com.system76.CosmicSettings/v1 -type f 2>/dev/null | head -20
```

```bash
$ ls -la ~/.config/cosmic/ | grep -E "(Launcher|Action|Command)"
```

<details><summary>💭 thinking</summary>
Let me try to see if there's any documentation or check what the cosmic-launcher process might be. Let me also check if there are keybindings configured.
</details>

```bash
$ ls -la ~/.config/cosmic/
```

```bash
$ which cosmic-launcher
```

<details><summary>💭 thinking</summary>
Great! cosmic-launcher exists. Now let me check if there's a config for it. The launcher configuration might be stored in a different location or it might be part of the compositor config. Let me also check the shortcuts config since the Super key binding would be there.
</details>

```bash
$ find ~/.config/cosmic/com.system76.CosmicSettings.Shortcuts -type f
```

```bash
$ cosmic-launcher --help 2>&1 | head -30
```

<details><summary>💭 thinking</summary>
Good! Now let me check the system_actions file which should contain the Super key binding for the launcher.
</details>

*Read: `/home/mischa/.config/cosmic/com.system76.CosmicSettings.Shortcuts/v1/system_actions`*

<details><summary>💭 thinking</summary>
Interesting, the system_actions file only has Terminal configured. The launcher activation might be hardcoded or in a different location. Let me check if there are any other config files related to the launcher, or check what processes are running.
</details>

```bash
$ ps aux | grep cosmic-launcher
```

```bash
$ find ~/.local/share/cosmic -name "*launch*" 2>/dev/null
```

<details><summary>💭 thinking</summary>
Good, cosmic-launcher is running. Now let me check the COSMIC settings in the GUI or look for configuration elsewhere. The launcher might store its config in a different location. Let me check if there's a cosmic-launcher specific config directory.
</details>

```bash
$ find /usr/share/cosmic -name "*launch*" 2>/dev/null | head -10
```

```bash
$ ls -la ~/.config/ | grep -i cosmic
```

<details><summary>💭 thinking</summary>
Let me try a different approach. Let me check what the actual launcher looks like by examining its desktop file or checking if there are configuration options available through COSMIC Settings. The launcher configuration might be minimal or might be accessed through the GUI settings.
</details>

```bash
$ man cosmic-launcher 2>&1 | head -40
```

<details><summary>💭 thinking</summary>
The launcher seems to have minimal configuration exposed. Let me check the COSMIC documentation or search online for information about configuring the cosmic launcher. Let me also check if there are any RON files specifically for the launcher that I might have missed.
</details>

```bash
$ find ~/.config/cosmic -type f -name "*.ron" 2>/dev/null | head -20
```

```bash
$ grep -r "launcher" ~/.config/cosmic/ 2>/dev/null | head -10
```

<details><summary>💭 thinking</summary>
The launcher doesn't seem to have extensive user-facing configuration files. Let me search online for information about configuring the COSMIC launcher, as this might be documented in the COSMIC desktop documentation.
</details>

*🔍 cosmic launcher configure settings super key 2025*

<details><summary>💭 thinking</summary>
Great! I found the information. The configuration is done through COSMIC Settings in the keyboard shortcuts section. Let me provide the user with a clear answer about how to configure the launcher.
</details>

**Claude:** Perfect! The COSMIC launcher (the action bar that appears when you press Super) is configured through **COSMIC Settings**:

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

**You:** How do I customize the look and function of cosmic launcher?

<details><summary>💭 thinking</summary>
The user is asking about customizing the look and function of the cosmic-launcher (the action bar that pops up when you press Super). Let me search for more specific information about customizing the launcher itself - its appearance, behavior, search functionality, etc.

I should look for:
1. Configuration files specific to cosmic-launcher
2. Documentation on launcher customization options
3. What aspects can be customized (appearance, search behavior, plugins, etc.)

Let me search for this information.
</details>

*🔍 cosmic-launcher customize appearance function configuration 2025*

```bash
$ find ~/.config -name "*launcher*" -o -name "*Launcher*" 2>/dev/null
```

<details><summary>💭 thinking</summary>
The web search didn't give me specific details about cosmic-launcher configuration files. Let me search more specifically for cosmic-launcher config files and also check the GitHub repository for documentation.
</details>

*🌐 https://github.com/pop-os/cosmic-launcher*

```bash
$ ls -la /usr/share/cosmic/ 2>/dev/null
```

<details><summary>💭 thinking</summary>
It seems like cosmic-launcher doesn't have much documented configuration. Let me search for any config files that might exist for it, and also check if there's information about what can be customized through COSMIC Settings or theme files.
</details>

```bash
$ ls -la ~/.local/state/cosmic* 2>/dev/null
```

*🔍 "cosmic-launcher" plugins extensions customize search providers*

<details><summary>💭 thinking</summary>
Let me check if there are any launcher-specific configuration directories or files in the cosmic config that I might have missed, and also look at the theme configurations since the launcher's appearance would inherit from the system theme.
</details>

```bash
$ find ~/.config/cosmic -type d | grep -i "app\|launch"
```

*Read: `/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/corner_radii`*

*Read: `/home/mischa/.config/cosmic/com.system76.CosmicTheme.Dark/v1/spacing`*

<details><summary>💭 thinking</summary>
Good, I can see the theme files use RON format. The launcher itself doesn't seem to have dedicated configuration files - it likely inherits appearance from the system theme. Let me provide a comprehensive answer about what can be customized.
</details>

**Claude:** Based on my research, here's what you can customize with the cosmic-launcher:

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

**You:** what is the best launcher that I can still use with cosmic desktop?  something that will obey theme changes, and keep track of application installs

<details><summary>💭 thinking</summary>
The user is asking about alternative launchers that work well with COSMIC desktop. They want:
1. Something that obeys theme changes (integrates with COSMIC theming)
2. Keeps track of application installs (auto-discovers new apps)

This is a good question for web search to find what launchers are compatible with COSMIC and what the community recommends. I should search for information about:
- Alternative launchers that work with COSMIC
- Launchers that support Wayland (since COSMIC uses Wayland)
- How well they integrate with theming

Let me search for this information.
</details>

*🔍 best application launcher COSMIC desktop wayland 2025*

*🔍 rofi ulauncher wofi wayland launcher COSMIC theme integration*

<details><summary>💭 thinking</summary>
Good, I have information about alternative launchers. Let me search for more specific information about which launchers automatically track application installs and work well on Wayland.
</details>

*🔍 fuzzel tofi anyrun launcher wayland freedesktop applications*

```bash
$ which rofi wofi fuzzel tofi ulauncher 2>/dev/null
```

❌ Error:
```
Exit code 1
rofi not found
wofi not found
fuzzel not found
tofi not found
ulauncher not found
```

<details><summary>💭 thinking</summary>
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

**Claude:** Based on my research, here are the best launcher options for COSMIC desktop:

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

