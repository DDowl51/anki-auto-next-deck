"""
Auto Next Deck - After finishing a deck, press Space to jump to the next deck

Behavior:
  1. Review all cards in Deck A -> land on Deck A's overview (Congratulations!)
  2. Press Space -> switch to Deck B's overview (shows due cards)
  3. Press Space again -> start reviewing Deck B

This avoids auto-switching without your intent -- you always have to
confirm with Space before moving on.
"""

from __future__ import annotations

from aqt import mw, gui_hooks
from aqt.utils import tooltip

# ---- state tracking ----
_just_finished: bool = False          # True when we just completed a deck's review
_finished_deck_id: int | None = None  # the deck that was just finished
_current_deck_id: int | None = None   # the deck currently being reviewed
_next_deck_id: int | None = None      # cached next deck found while _just_finished


# ---- card tracking ----
def on_reviewer_did_show_question(card) -> None:
    """Remember which deck we're currently reviewing."""
    global _current_deck_id
    _current_deck_id = card.current_deck_id()


# ---- state change detection ----
def on_state_will_change(new_state: str, old_state: str) -> None:
    """
    Detect when a deck's review finishes (review -> overview).
    Also clear the 'just finished' flag if the user navigates away manually.
    """
    global _just_finished, _finished_deck_id, _current_deck_id, _next_deck_id

    if new_state == "overview" and old_state == "review":
        _just_finished = True
        _finished_deck_id = _current_deck_id
        _current_deck_id = None
        _next_deck_id = _find_next_deck_with_cards(_finished_deck_id)

    elif new_state == "deckBrowser":
        _clear_finished_state()


# ---- shortcut handling ----
def on_state_shortcuts_will_change(state: str, shortcuts: list) -> None:
    """
    On overview: always handle Space/Enter at Qt level.

    The decision is made at key-press time (see on_overview_key), because
    the deck can change while the overview stays open.
    """
    if state != "overview":
        return

    # Qt-level shortcuts fire before webview handlers, so Space works
    # regardless of webview focus state.
    shortcuts.insert(0, (" ", on_overview_key))
    shortcuts.insert(0, ("return", on_overview_key))


def on_overview_key() -> None:
    """
    - Still on the deck we just finished, and a next deck exists
      -> switch to the next deck's overview
    - Otherwise -> start review (mw.onStudyKey)
    """
    if _is_on_finished_deck() and _next_deck_id is not None:
        _switch_to_next_deck()
    else:
        _clear_finished_state()
        mw.onStudyKey()


def _is_on_finished_deck() -> bool:
    """True if we just finished a deck and are still on that deck.

    If the user switched decks some other way (e.g. a controller add-on
    selecting another deck from the congrats screen), the finished state
    is stale and must not hijack Space.
    """
    return (
        _just_finished
        and _finished_deck_id is not None
        and mw.col.decks.get_current_id() == _finished_deck_id
    )


def _clear_finished_state() -> None:
    global _just_finished, _finished_deck_id, _next_deck_id
    _just_finished = False
    _finished_deck_id = None
    _next_deck_id = None


def _switch_to_next_deck() -> None:
    deck_id_to_switch = _next_deck_id
    _clear_finished_state()

    mw.col.decks.select(deck_id_to_switch)

    next_deck = mw.col.decks.get(deck_id_to_switch)
    if next_deck:
        tooltip(
            f"Next deck: {next_deck['name']}\nPress Space again to start",
            period=2500,
        )

    mw.moveToState("overview")


# ---- controller support (e.g. Contanki) ----
# Controller add-ons don't send real key presses, so the Qt shortcuts above
# never fire. Contanki's "Select"/"Enter" actions run
# `document.activeElement.click()` in the main webview; on the congrats page
# the active element is <body>. Catch that synthetic click (isTrusted=false;
# real mouse clicks are trusted) and route it to the same Space logic.
_BRIDGE_CMD = "auto_next_deck:next"

_CLICK_LISTENER_JS = f"""
(() => {{
  if (window.__autoNextDeckInstalled) return;
  window.__autoNextDeckInstalled = true;
  document.addEventListener("click", (e) => {{
    if (e.isTrusted) return;
    if (e.target !== document.body && e.target !== document.documentElement) return;
    pycmd("{_BRIDGE_CMD}");
  }}, true);
}})();
"""


def on_webview_did_inject_style_into_page(webview) -> None:
    """Install the click listener on the main webview's overview pages.

    Uses page().runJavaScript() directly: webview.eval() queues until the
    page reports domDone, which the SvelteKit congrats page never does.
    """
    if webview is not mw.web or mw.state != "overview":
        return
    webview.page().runJavaScript(_CLICK_LISTENER_JS)


def on_webview_did_receive_js_message(handled: tuple, message: str, context):
    if message != _BRIDGE_CMD:
        return handled
    if mw.state == "overview":
        on_overview_key()
    return (True, None)


# ---- deck navigation helpers ----
def _find_next_deck_with_cards(current_deck_id: int) -> int | None:
    """Find the alphabetically-next deck with cards to study.

    Skips filtered (cram) decks and decks with zero due cards.
    Returns None if no suitable deck remains.
    """
    decks = mw.col.decks.all_names_and_ids()
    if not decks:
        return None

    sorted_decks = sorted(decks, key=lambda d: d.name.lower())

    found_current = False
    for deck in sorted_decks:
        if found_current:
            if _is_filtered_deck(deck.id):
                continue
            if _deck_has_due_cards(deck.id):
                return deck.id
            continue
        if deck.id == current_deck_id:
            found_current = True

    return None


def _is_filtered_deck(deck_id: int) -> bool:
    """Check if a deck is a filtered (cram) deck."""
    try:
        cfg = mw.col.decks.config_dict_for_deck_id(deck_id)
        return bool(cfg.get("dyn", 0))
    except Exception:
        return False


def _deck_has_due_cards(deck_id: int) -> bool:
    """Check if a deck has any new/learn/review cards due.

    Temporarily selects the deck to query the scheduler,
    then restores the original selection.
    """
    saved = mw.col.decks.get_current_id()
    try:
        mw.col.decks.select(deck_id)
        new_lrn_rev = mw.col.sched.counts()
        return sum(new_lrn_rev) > 0
    except Exception:
        return True  # safe default
    finally:
        mw.col.decks.select(saved)


# ---- wire everything up ----
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)
gui_hooks.state_will_change.append(on_state_will_change)
gui_hooks.state_shortcuts_will_change.append(on_state_shortcuts_will_change)
gui_hooks.webview_did_inject_style_into_page.append(on_webview_did_inject_style_into_page)
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)
