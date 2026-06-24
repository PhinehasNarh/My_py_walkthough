"""
14 - Spaced-Repetition Flashcards
Project: Study and retain material efficiently with a real spaced-repetition algorithm.

Uses the SM-2 algorithm (the one behind Anki and SuperMemo): cards you find hard come
back sooner, cards you know well come back later. Cards live in a JSON file so your
progress is saved between sessions.

Usage:
  python main.py add "What port does HTTPS use?" "443"
  python main.py review        # study everything due today
  python main.py list
  python main.py stats
"""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

DECK_FILE = Path(__file__).parent / "deck.json"


def load_deck():
    if DECK_FILE.exists():
        return json.loads(DECK_FILE.read_text(encoding="utf-8"))
    return []


def save_deck(deck) -> None:
    DECK_FILE.write_text(json.dumps(deck, indent=2), encoding="utf-8")


def new_card(question: str, answer: str) -> dict:
    return {
        "question": question,
        "answer": answer,
        "ease": 2.5,        # SM-2 ease factor, never drops below 1.3
        "interval": 0,      # days until next review
        "repetitions": 0,   # how many times answered correctly in a row
        "due": date.today().isoformat(),
    }


def sm2_update(card: dict, quality: int) -> dict:
    """Apply one SM-2 step. quality is 0-5 (0 = blank, 5 = perfect recall)."""
    if quality < 3:
        # Got it wrong: start the card over, but keep the ease factor adjustment below.
        card["repetitions"] = 0
        card["interval"] = 1
    else:
        if card["repetitions"] == 0:
            card["interval"] = 1
        elif card["repetitions"] == 1:
            card["interval"] = 6
        else:
            card["interval"] = round(card["interval"] * card["ease"])
        card["repetitions"] += 1

    # Adjust the ease factor based on how hard it felt.
    card["ease"] += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    card["ease"] = max(1.3, round(card["ease"], 2))
    card["due"] = (date.today() + timedelta(days=card["interval"])).isoformat()
    return card


def cmd_add(args) -> None:
    deck = load_deck()
    deck.append(new_card(args.question, args.answer))
    save_deck(deck)
    print(f"Added card. Deck now has {len(deck)} card(s).")


def cmd_review(args) -> None:
    deck = load_deck()
    today = date.today().isoformat()
    due = [c for c in deck if c["due"] <= today]
    if not due:
        print("Nothing due today. Nice work.")
        return

    print(f"{len(due)} card(s) due. Grade each 0-5 (0 = no idea, 5 = perfect).\n")
    for card in due:
        print(f"Q: {card['question']}")
        input("   (press Enter to see the answer) ")
        print(f"A: {card['answer']}")
        grade = ask_grade()
        sm2_update(card, grade)
        print(f"   Next review in {card['interval']} day(s).\n")
    save_deck(deck)
    print("Session saved.")


def ask_grade() -> int:
    while True:
        raw = input("   Your grade (0-5): ").strip()
        if raw.isdigit() and 0 <= int(raw) <= 5:
            return int(raw)
        print("   Please enter a whole number from 0 to 5.")


def cmd_list(args) -> None:
    deck = load_deck()
    if not deck:
        print("Deck is empty. Add cards with the 'add' command.")
        return
    for i, c in enumerate(deck, 1):
        print(f"{i:3}. [due {c['due']}] {c['question']}")


def cmd_stats(args) -> None:
    deck = load_deck()
    today = date.today().isoformat()
    due = sum(1 for c in deck if c["due"] <= today)
    learned = sum(1 for c in deck if c["repetitions"] >= 2)
    print(f"Total cards: {len(deck)}")
    print(f"Due today:   {due}")
    print(f"Well-known:  {learned}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Spaced-repetition flashcards (SM-2).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a card.")
    p_add.add_argument("question")
    p_add.add_argument("answer")
    p_add.set_defaults(func=cmd_add)

    sub.add_parser("review", help="Review cards due today.").set_defaults(func=cmd_review)
    sub.add_parser("list", help="List all cards.").set_defaults(func=cmd_list)
    sub.add_parser("stats", help="Show deck statistics.").set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
