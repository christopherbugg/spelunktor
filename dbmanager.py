import sqlite3
import os
import time
import logging


class DBManager:
    # Boolean check if table exists
    database_exists = os.path.exists('database.db')
    # Create Connection object (database)
    conn = sqlite3.connect('database.db', timeout=60)

    # Create Cursor object to navigate database
    curs = conn.cursor()

    # Constructor
    def __init__(self):
        # If there is no database, create one (with a table)
        if not self.database_exists:
            logging.info("Database not found, creating new database")
            self.create_tables()

    def create_tables(self):
        # Create tables
        self.curs.execute('''CREATE TABLE IF NOT EXISTS links 
                            (linkID integer PRIMARY KEY, link text, lastchecked integer, accessible bool)''')

        # Save (commit) the changes
        self.conn.commit()

        # Seed the new db with a solid start
        self.insert_link('darkfailenbsdla5mal2mxn2uz66od5vtzd5qozslagrfzachha3f3id')

        # Save (commit) the changes
        self.conn.commit()

    def insert_multiple_links(self, links):
        for link in links:
            self.insert_link(link)

    def insert_link(self, link):

        # Setup an escape condition
        query_failed = True

        # Keep trying till the query runs
        while query_failed:

            try:

                # Insert a row of data
                self.curs.execute("INSERT INTO links(link) VALUES (?) EXCEPT "
                                  "SELECT link from links where cast(link as text) = cast(? as text)", [link, link])

                # We did it!
                query_failed = False

            # Print exception and chill for a bit
            except Exception as e:

                logging.error(e)
                logging.error("Exception occurred, trying again!")

                time.sleep(5)

        # Save (commit) the changes
        self.conn.commit()

    def update_link(self, link, accessibility):

        # Setup an escape condition
        query_failed = True

        # Keep trying till the query runs
        while query_failed:

            try:

                link_tuple = (time.time(), accessibility, link)

                self.curs.execute(
                    "UPDATE links SET lastchecked = ?, accessible = ? WHERE cast(link as text) = cast(? as text)",
                    link_tuple)

                # We did it!
                query_failed = False

            # Print exception and chill for a bit
            except Exception as e:

                logging.error(e)
                logging.error("Exception occurred, trying again!")

                time.sleep(5)

        # Save (commit) the changes
        self.conn.commit()

    def get_links(self, numlinks):

        links_list = []

        # Setup an escape condition
        query_failed = True

        # Keep trying till the query runs
        while query_failed:

            try:

                # Execute the search
                self.curs.execute("SELECT link FROM links ORDER BY lastchecked LIMIT ?", [numlinks])

                for useless_tuple in self.curs.fetchall():

                    # Some values are already strings for some reason so we're side-stepping an error here
                    if type(useless_tuple[0]).__name__ == 'str':
                        links_list.append(useless_tuple[0])
                    else:
                        links_list.append(str(useless_tuple[0], 'utf-8'))

                # We did it!
                query_failed = False

            # Print exception and chill for a bit
            except Exception as e:

                logging.error(e)
                logging.error("Exception occurred, trying again!")

                time.sleep(5)

        return links_list

    def get_base_urls(self):

        duplicated_links_list = []
        links_list = []

        # Setup an escape condition
        query_failed = True

        # Keep trying till the query runs
        while query_failed:

            try:

                # Execute the search
                self.curs.execute("SELECT cast(link as text) as link FROM links WHERE accessible = 1")

                # Scrape out the link from the db cursor and parse out just the base url
                for useless_tuple in self.curs.fetchall():
                    duplicated_links_list.append(useless_tuple[0] + '\n')

                # De-Duplicate the list
                links_list = list(dict.fromkeys(duplicated_links_list))

                # We did it!
                query_failed = False

            # Print exception and chill for a bit
            except Exception as e:

                logging.error(e)
                logging.error("Exception occurred, trying again!")

                time.sleep(5)

        return links_list

    # Commits the changes but does not close the connection
    def save(self):

        self.conn.commit()

    # Closes connection when done
    def close(self):

        # Save (commit) the changes
        self.conn.commit()

        # Close connection
        self.conn.close()
