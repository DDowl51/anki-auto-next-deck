# Auto Next Deck

**After finishing a deck, press Space to jump to the next deck — no mouse needed.**

Tired of finishing a deck and having to manually navigate back to the deck list, scroll, click the next deck, and click "Study"? This addon makes the flow seamless:

## How it works

```
复习完 Deck A → 停在 A 的 "Congratulations" 页面
     ↓ 按空格 (Space)
跳到 Deck B 的概览页面（显示待复习数量 + "Study" 按钮）
     ↓ 再按空格 (Space)
开始复习 Deck B
```

- **First Space** — switches to the alphabetically next deck that has cards due
- **Second Space** — starts reviewing that deck (normal behavior)
- Stays on the finished deck until you explicitly press Space — no auto-switch surprises

## Installation

### Via .ankiaddon (recommended)
1. Download `Auto_Next_Deck.ankiaddon`
2. In Anki: **Tools → Add-ons → Install from file...**
3. Select the `.ankiaddon` file
4. Restart Anki

### Manual
1. Copy the `auto_next_deck` folder into your Anki `addons21` directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **macOS**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
2. Restart Anki

## Usage

1. Study a deck as normal
2. When you review the last card, Anki shows the "Congratulations" screen
3. Press **Space** (or **Enter**) to jump to the next deck's overview
4. Press **Space** again to start studying

That's it. No new UI, no settings to configure.

## Deck ordering

Decks are traversed in **case-insensitive alphabetical order** by name.
Subdecks (e.g. `Parent::Child`) are included and sorted by their full path name.

- Filtered (cram) decks are **skipped**
- Decks with **zero due cards** are **skipped**
- If no decks remain, Space works normally (shows "No cards are due yet")

## Technical details

- Hooks into `gui_hooks.state_will_change` to detect review→overview transitions
- Uses `gui_hooks.state_shortcuts_will_change` to inject a Qt-level Space shortcut that fires before the webview's "Study" handler
- No external dependencies — pure Python, standard Anki addon API

## License

AGPL-3.0-only
