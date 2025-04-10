#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2025 cbolzoni@proton.me

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Pythonprogrammering för AI-utveckling mars VT25 - Inlämningsuppgift 1 - Blackjack med Flask

A Flask-based implementation of the Blackjack card game.
This web application allows users to play the classic casino card game
against a dealer following standard blackjack rules.
"""

import os
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for the session

# Card-related collections
CARD_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,
}
SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Unicode card symbols
SPADES = ["🂡", "🂢", "🂣", "🂤", "🂥", "🂦", "🂧", "🂨", "🂩", "🂪", "🂫", "🂭", "🂮"]
HEARTS = ["🂱", "🂲", "🂳", "🂴", "🂵", "🂶", "🂷", "🂸", "🂹", "🂺", "🂻", "🂽", "🂾"]
DIAMONDS = ["🃁", "🃂", "🃃", "🃄", "🃅", "🃆", "🃇", "🃈", "🃉", "🃊", "🃋", "🃍", "🃎"]
CLUBS = ["🃑", "🃒", "🃓", "🃔", "🃕", "🃖", "🃗", "🃘", "🃙", "🃚", "🃛", "🃝", "🃞"]
CARD_BACK = "🂠"
CARD_SYMBOLS = {
    "spades": {value: suit for value, suit in zip(VALUES, SPADES)},
    "hearts": {value: suit for value, suit in zip(VALUES, HEARTS)},
    "diamonds": {value: suit for value, suit in zip(VALUES, DIAMONDS)},
    "clubs": {value: suit for value, suit in zip(VALUES, CLUBS)},
}


def get_card_symbol(card):
    """Get the Unicode symbol for a card."""
    return CARD_SYMBOLS[card["suit"]][card["rank"]]


def create_deck():
    """Create a standard deck of 52 cards."""
    return [{"rank": rank, "suit": suit} for suit in SUITS for rank in RANKS]


def shuffle_deck(deck):
    """Shuffle the deck of cards."""
    random.shuffle(deck)
    return deck


def calculate_hand_value(hand):
    """Calculate the value of a hand, considering Aces as 1 or 11."""
    value = 0
    aces = 0

    for card in hand:
        rank = card["rank"]
        if rank == "A":
            aces += 1
            value += 11
        else:
            value += CARD_VALUES[rank]

    # Adjust for Aces if needed
    while value > 21 and aces:
        value -= 10
        aces -= 1

    return value


def deal_initial_cards():
    """Deal initial cards to player and dealer."""
    deck = shuffle_deck(create_deck())
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    return {
        "deck": deck,
        "player_hand": player_hand,
        "dealer_hand": dealer_hand,
        "player_value": calculate_hand_value(player_hand),
        "dealer_value": calculate_hand_value(dealer_hand),
        "game_over": False,
        "message": "",
    }


@app.route("/")
def index():
    """Render the main game page."""
    return render_template("index.html")


@app.route("/new_game")
def new_game():
    """Start a new game."""
    session["game_state"] = deal_initial_cards()
    return redirect(url_for("game"))


@app.route("/game")
def game():
    """Show the current game state."""
    if "game_state" not in session:
        return redirect(url_for("new_game"))

    game_state = session["game_state"]

    # Only show the first card of the dealer if the game is not over
    visible_dealer_hand = (
        [game_state["dealer_hand"][0]]
        if not game_state["game_over"]
        else game_state["dealer_hand"]
    )
    visible_dealer_value = (
        calculate_hand_value([game_state["dealer_hand"][0]])
        if not game_state["game_over"]
        else game_state["dealer_value"]
    )

    return render_template(
        "game.html",
        player_hand=game_state["player_hand"],
        dealer_hand=visible_dealer_hand,
        player_value=game_state["player_value"],
        dealer_value=visible_dealer_value,
        game_over=game_state["game_over"],
        message=game_state["message"],
        card_back=CARD_BACK,
    )


@app.route("/hit")
def hit():
    """Player decides to hit (take another card)."""
    if "game_state" not in session:
        return redirect(url_for("new_game"))

    game_state = session["game_state"]

    if game_state["game_over"]:
        return redirect(url_for("game"))

    # Deal a card to the player
    game_state["player_hand"].append(game_state["deck"].pop())
    game_state["player_value"] = calculate_hand_value(game_state["player_hand"])

    # Check if player busts
    if game_state["player_value"] > 21:
        game_state["game_over"] = True
        game_state["message"] = "You busted! Dealer wins."

    session["game_state"] = game_state
    return redirect(url_for("game"))


@app.route("/stand")
def stand():
    """Player decides to stand (no more cards)."""
    if "game_state" not in session:
        return redirect(url_for("new_game"))

    game_state = session["game_state"]

    if game_state["game_over"]:
        return redirect(url_for("game"))

    # Dealer's turn
    while game_state["dealer_value"] < 17:
        game_state["dealer_hand"].append(game_state["deck"].pop())
        game_state["dealer_value"] = calculate_hand_value(game_state["dealer_hand"])

    game_state["game_over"] = True

    # Determine the winner
    if game_state["dealer_value"] > 21:
        game_state["message"] = "Dealer busted! You win!"
    elif game_state["dealer_value"] > game_state["player_value"]:
        game_state["message"] = "Dealer wins!"
    elif game_state["dealer_value"] < game_state["player_value"]:
        game_state["message"] = "You win!"
    else:
        game_state["message"] = "It's a tie!"

    session["game_state"] = game_state
    return redirect(url_for("game"))


@app.context_processor
def utility_processor():
    """Make the `get_card_symbol` function available in all templates."""
    return dict(get_card_symbol=get_card_symbol)


if __name__ == "__main__":
    app.run(debug=True)
