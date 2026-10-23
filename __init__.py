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
        _just_finished = False
        _finished_deck_id = None
        _next_deck_id = None


# ---- shortcut handling ----
def on_state_shortcuts_will_change(state: str, shortcuts: list) -> None:
    """
    On overview: always handle Space/Enter at Qt level.

    - Just finished a deck (has _next_deck_id) -> switch to next deck
    - Normal overview -> start review (mw.onStudyKey)
    """
    global _just_finished, _finished_deck_id, _next_deck_id

    if state != "overview":
        return

    if _just_finished and _next_deck_id is not None:
        # ---- Mode 1: Deck just finished, Space = jump to next deck ----
        deck_id_to_switch = _next_deck_id

        def switch_to_next_deck() -> None:
            global _just_finished, _finished_deck_id, _next_deck_id
            _just_finished = False
            _finished_deck_id = None
            _next_deck_id = None

            mw.col.decks.select(deck_id_to_switch)

            next_deck = mw.col.decks.get(deck_id_to_switch)
            if next_deck:
                tooltip(
                    f"Next deck: {next_deck['name']}\nPress Space again to start",
                    period=2500,
                )

            mw.moveToState("overview")

        shortcuts.insert(0, (" ", switch_to_next_deck))
        shortcuts.insert(0, ("return", switch_to_next_deck))

    else:
        # ---- Mode 2: Normal overview, Space = start review ----
        # This ensures Space always works on the overview, regardless of
        # webview focus state. Qt-level shortcuts fire before webview handlers.
        shortcuts.insert(0, (" ", mw.onStudyKey))
        shortcuts.insert(0, ("return", mw.onStudyKey))

        # If the just finished flag was stale (no next deck found), clean it up
        if _just_finished:
            _just_finished = False
            _finished_deck_id = None


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
