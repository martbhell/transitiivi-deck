""" Script to generate an .apkg ankiweb deck with verbs from a wiktionary category """

import sqlite3
from sqlite3 import Error

import genanki

import mediawikiapi

# scrape wiktionary with beautifulsoup4:
#  - visit https://en.wiktionary.org/wiki/Category:Finnish_transitive_verbs
#  - follow links til we get to the end
#  - https://en.wiktionary.org/wiki/Category:Finnish_intransitive_verbs
#  - add words and explanation and if transitive or intransitive


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    #    finally:
    #        if conn:
    #            conn.close()

    return conn


def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_verb(conn, verb):
    """
    Create a new project into the projects table
    :param conn:
    :param verb (verb, explanation, transitiivi)
    :return: project id
    """
    sql = """ INSERT INTO verbs(verb,explanation,transitiivi)
              VALUES(?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, verb)
    conn.commit()
    return cur.lastrowid


def select_verb(conn, verb):
    """
    Query verbs by verb
    :param conn: the Connection object
    :param verb:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM verbs WHERE verb=?", (verb,))

    rows = cur.fetchall()

    return rows


def get_words():
    """parse wiktionary"""

    mediawiki = mediawikiapi.MediaWikiAPI(
        config=mediawikiapi.Config(
            mediawiki_url="https://{}.wiktionary.org/w/api.php", rate_limit=10
        )
    )

    trans = mediawiki.category_members(title="Finnish_transitive_verbs", cmlimit=6550)
    intrans = mediawiki.category_members(
        title="Finnish_intransitive_verbs", cmlimit=6550
    )

    common = parse_csc()
    conn = create_connection(r"pythonsqlite.db")
    create_table(conn, sql_create_verbs_table)

    trans_dict = {}
    intrans_dict = {}
    for t in trans:
        if t not in common:
            print(f"skipping {t}")
            continue
        print(f"found: {t}")

        # check if in db
        # if not add one to these columns:
        #  - verb (yep)
        #  - explanation (yep)
        #  - transitiivi (true/false)

        db_query = select_verb(conn, t)
        if len(db_query) > 0:
            print("It's in the DB already!")
            trans_dict[t] = db_query[0][2]
            continue

        t_page = mediawiki.page(t)
        explanation = t_page.section("Verb")
        if explanation.strip() == "":
            continue
        trans_dict[t] = explanation

        insert = (t, explanation, 1)
        create_verb(conn, insert)

    for it in intrans:
        if it not in common:
            print(f"skipping {it}")
            continue
        print(f"found: {it}")

        it_db_query = select_verb(conn, it)
        if len(it_db_query) > 0:
            print("It's in the DB already!")
            intrans_dict[it] = it_db_query[0][2]
            continue

        it_page = mediawiki.page(it)
        in_explanation = it_page.section("Verb")
        if in_explanation.strip() == "":
            continue
        intrans_dict[it] = in_explanation

        itinsert = (it, in_explanation, 0)
        create_verb(conn, itinsert)

    conn.close()

    return (trans_dict, intrans_dict)


def parse_csc():
    """parse the common words from finnish news papers"""
    common_verbs = []

    with open(
        "suomen-sanomalehtikielen-taajuussanasto-B9996.txt", encoding="utf-8"
    ) as f:
        lines = f.readlines()
    for line in lines:
        if "(verbi" in line:
            cleanup = line.strip()
            verbi = cleanup.split(" ")[7]
            common_verbs.append(verbi)

    return common_verbs


def main():
    """The Thing"""

    trans, intrans = get_words()

    words = []
    for k in trans:
        value = trans[k]
        words.append((k, value))

    for c in intrans:
        valuec = intrans[c]
        words.append((c, valuec))

    print(words)
    print(len(words))

    #    data structure
    #    words = [
    #        ("verb1", "trans|intrans + explanation"),
    #        ("verb2", "trans|intrans + explanation"),
    #    ]

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
                "afmt": "{{Description}}",
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
    # TODO: Any other sources of verbs?


#########

sql_create_verbs_table = """ CREATE TABLE IF NOT EXISTS verbs (
                                        id integer PRIMARY KEY,
                                        verb text NOT NULL,
                                        explanation text,
                                        transitiivi text
                         ); """

main()
