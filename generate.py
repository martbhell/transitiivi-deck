""" Script to generate an .apkg ankiweb deck with verbs from a wiktionary category """

import genanki

# scrape wiktionary with beautifulsoup4:
#  - visit https://en.wiktionary.org/wiki/Category:Finnish_transitive_verbs
#  - follow links til we get to the end
#  - https://en.wiktionary.org/wiki/Category:Finnish_intransitive_verbs
#  - add words and explanation and if transitive or intransitive

# Data structure


def main():
    """The Thing"""

    words = [
        ("verb1", "trans|intrans + explanation"),
        ("verb2", "trans|intrans + explanation"),
    ]

    # Define Anki note model
    model_id = 1699392319  ## TODO
    model = genanki.Model(
        model_id,
        "Simple Model",
        fields=[
            {"name": "Verb"},
            {"name": "Description"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Verb}}",
                "afmt": "{{Description}}",
            },
            {
                "name": "Card 2",
                "qfmt": "{{Verb}}",
                "afmt": "{{Directory}}",
            },
        ],
    )

    # Generate Anki cards and add them to a deck
    deck_id = 2159400110  ## TODO
    deck = genanki.Deck(deck_id, "In- and Transitive Verbs in Finnish")

    for verb, description in words:
        note = genanki.Note(model=model, fields=[verb, description])
        deck.add_note(note)

    # Save the deck to an Anki package (*.apkg) file
    genanki.Package(deck).write_to_file("transitiivi-deck.apkg")

    # TODO: Add to GitHub actions and make a release out of this
    # TODO: Perhaps prune esoteric / weird words.
    # TODO: Any other sources of verbs?


main()
