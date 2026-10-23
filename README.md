# Auto Next Deck

English | [简体中文](README.zh-CN.md)

An Anki add-on that lets you move on to the next deck from the "Congratulations" screen with a single key, instead of going back to the deck list.

## Features

- Press <kbd>Space</kbd> or <kbd>Enter</kbd> on the "Congratulations" screen to open the next deck that has cards due.
- Nothing happens automatically: the add-on only switches decks when you press the key.
- Works with game controllers via [Contanki](https://ankiweb.net/shared/info/1898790263).
- No settings, no extra UI.

## Installation

### AnkiWeb (recommended)

1. In Anki, open **Tools → Add-ons → Get Add-ons...**
2. Enter the code `1855134110`.
3. Restart Anki.

Add-on page: <https://ankiweb.net/shared/info/1855134110>

### From a file

1. Download `Auto_Next_Deck-<version>.ankiaddon` from the [latest release](https://github.com/DDowl51/anki-auto-next-deck/releases/latest).
2. In Anki, open **Tools → Add-ons → Install from file...** and select the downloaded file.
3. Restart Anki.

### From source

Clone this repository into your Anki add-ons folder and restart Anki:

| OS      | Add-ons folder                                |
| ------- | --------------------------------------------- |
| Windows | `%APPDATA%\Anki2\addons21\`                   |
| macOS   | `~/Library/Application Support/Anki2/addons21/` |
| Linux   | `~/.local/share/Anki2/addons21/`              |

```sh
cd ~/.local/share/Anki2/addons21
git clone https://github.com/DDowl51/anki-auto-next-deck.git
```

When installing from a file or from source, if you have the AnkiWeb version installed, disable it first so the two copies don't run at the same time.

## Usage

1. Study a deck until Anki shows the "Congratulations" screen.
2. Press <kbd>Space</kbd>. Anki opens the overview of the next deck.
3. Press <kbd>Space</kbd> again to start studying it.

If no later deck has cards due, <kbd>Space</kbd> behaves as it normally does.

### Which deck is "next"

- Decks are ordered by full name (for example `Parent::Child`), case-insensitive.
- The search starts after the deck you just finished and does not wrap around.
- Filtered decks and decks with no cards due are skipped.

### Game controllers

With Contanki, use the **Select** or **Enter** action (the A button in the default profile) on the "Congratulations" screen. It does the same as <kbd>Space</kbd>.

Contanki's **Forward** action is not supported yet.

## Compatibility

- Anki 2.1.45 or later. Tested on Anki 26.09.
- Because <kbd>Space</kbd> and <kbd>Enter</kbd> are handled at the Qt level on the deck overview screen, they start studying even when the page doesn't have keyboard focus. Other add-ons that bind these keys on the overview screen may conflict.

## How it works

- Listens to `gui_hooks.state_will_change` to detect the move from review to the overview screen, and remembers which deck was finished.
- Registers <kbd>Space</kbd> and <kbd>Enter</kbd> through `gui_hooks.state_shortcuts_will_change`. When a key is pressed, the add-on switches decks only if the current deck is still the one just finished; otherwise it starts studying.
- Contanki sends clicks to the page instead of key presses. On the "Congratulations" page the add-on installs a listener that catches synthetic clicks on `<body>` (`isTrusted === false`) and passes them to the same handler through `pycmd`. Real mouse clicks are not affected.

## Changelog

### 1.1.0

- Added game controller support for Contanki's Select / Enter actions.
- Fixed: after switching decks from the "Congratulations" screen in some other way (for example Contanki's "Next Due Deck"), <kbd>Space</kbd> skipped that deck instead of starting it.

### 1.0.0

- Initial release.

## License

[AGPL-3.0-only](LICENSE)
