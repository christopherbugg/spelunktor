import spitor
import dbmanager
import time
import argparse
import logging
from multiprocessing import Process


class SpelunkTor:

    # Specify the name of the links file
    links_filename = 'links.txt'

    # Number of child processes
    #  Good values are <50
    #  Above 50 seems to result in too many concurrency problems (tor and db)
    child_processes = 1

    # Establish a db manager
    db = dbmanager.DBManager()

    def __init__(self):

        # Parse and deal with the args
        parser = argparse.ArgumentParser(description='Program Description')
        parser.add_argument('-v', '--verbosity', type=int, default=0, choices=[0, 1, 2, 3],
                            help='Verbosity of log messages. Default is 0.')
        parser.add_argument('-p', '--processes', type=self.positive_integer, default=10,
                            help='Number of child processes. Default is 10.')
        args = parser.parse_args()

        self.child_processes = args.processes

        # Set logging output verbosity based on argument
        log_lvl = logging.CRITICAL
        if args.verbosity == 1:
            log_lvl = logging.ERROR
        elif args.verbosity == 2:
            log_lvl = logging.WARNING
        elif args.verbosity == 3:
            log_lvl = logging.INFO
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log_lvl)

        # Let the db get setup before the children play with it
        time.sleep(1)

        # Initialize the main program loop
        self.main_loop()

    # Function for checking for a positive integer in an argument
    @staticmethod
    def positive_integer(string_value):
        integer_value = int(string_value)
        if integer_value <= 0:
            raise argparse.ArgumentTypeError("found %s, looking for a positive integer" % string_value)
        return integer_value

    # The main program loop
    def main_loop(self):

        # Start the sub processes
        for x in range(self.child_processes):
            p = Process(target=spitor.spitor, args=())
            time.sleep(5)
            p.start()

        # Every x seconds, write links to a file
        while True:

            # Time to sleep between cycles
            time.sleep(120)

            # Write out the currently accessible links to a file
            logging.info("Updating links.txt file...")
            self.links_to_file()

    # Create our links file with all the base urls in the db
    def links_to_file(self):

        urls = self.db.get_base_urls()

        with open(self.links_filename, 'w') as file:
            file.writelines(urls)

        print("links.txt updated with " + str(len(urls)) + " urls")
        # Included to make log redirection easier
        logging.info("links.txt updated with %s urls", str(len(urls)))


SpelunkTor()
