import re
import time
import logging
import tempfile
import dbmanager
import subprocess


def spitor():

    # Create a new db handler
    spitor_db = dbmanager.DBManager()

    # Wait a bit before going round and round
    time.sleep(5)

    while True:

        # Grab a fresh new link
        onion_link = get_link(spitor_db)

        logging.info("Starting: %s", onion_link)

        # Update the onion link's most recent access time and indicate it was not accessible
        #  We do this first thing so if we reach our timeout and our sub-process is killed, it's still recorded.
        update_link(spitor_db, onion_link, False)

        # Make a new tmp file and delete when done
        with tempfile.NamedTemporaryFile() as file:

            try:
                # Spider the site and throw it all in the temp file
                if logging.root.level <= logging.INFO:
                    process = subprocess.Popen(['torsocks', 'wget', '--force-html', '--random-wait', '--wait=1',
                                                '--recursive', '--level=2', '--timeout=120',
                                                '-R', '*.jpg, *.zip, *.css, *.png, *.jpeg, *.svg',
                                                '--output-document=' + file.name, onion_link + '.onion'])
                elif logging.root.level <= logging.ERROR:
                    process = subprocess.Popen(['torsocks', 'wget', '--force-html', '--random-wait', '--wait=1',
                                                '--recursive', '--level=2', '--quiet', '--timeout=120',
                                                '-R', '*.jpg, *.zip, *.css, *.png, *.jpeg, *.svg',
                                                '--output-document=' + file.name, onion_link + '.onion'])
                else:
                    process = subprocess.Popen(['torsocks', '--quiet', 'wget', '--force-html', '--random-wait',
                                                '--wait=1',
                                                '--recursive', '--level=2', '--quiet', '--timeout=120',
                                                '-R', '*.jpg, *.zip, *.css, *.png, *.jpeg, *.svg',
                                                '--output-document='+file.name, onion_link+'.onion'])

                # Run the command for at most <timeout> seconds
                try:
                    logging.info('Running in process %s %s', process.pid, onion_link)
                    process.wait(timeout=240)
                except subprocess.TimeoutExpired:
                    logging.warning('Timed out - killing %s %s', process.pid, onion_link)
                    process.kill()

            except Exception as e:
                logging.error("the below exception was encountered when attempting the following link")
                logging.error(onion_link)
                logging.error(e)

            # Parse the temp file
            file_lines_list = file.readlines()

        # If we got something back
        if file_lines_list:

            process_file_lines(spitor_db, onion_link, file_lines_list)

        # Save items to db without closing connection
        spitor_db.save()
        time.sleep(1)

        logging.info("Ending: " + onion_link)


# Take the returned file, extract links, save in db, and update our link's access info
def process_file_lines(spitor_db, onion_link, file_lines_list):

    # The list of links we get back
    links_list = []

    # Add together all the links into a single list
    for line in file_lines_list:
        links_list = links_list + extract_links(line)

    # Save the links to the db
    save_links(spitor_db, links_list)

    # Update the onion link's most recent access time and indicate it was accessible
    update_link(spitor_db, onion_link, True)


def extract_links(page):
    # Bytes Regex to match onion links (v3)
    regex = rb'[a-zA-Z0-9]{56}\.onion'

    trunkated_list = []

    try:

        # List of all onion links in the page
        matches_list = re.findall(regex, page)

        # Remove .onion (we don't need to store it)
        for match in matches_list:
            trunkated_list.append(match[:-6])

    except Exception as e:
        logging.warning("the below exception was encountered when parsing the following line (trunkated)")
        logging.warning(page[:100])
        logging.warning(e)

    return trunkated_list


# Save the links in the database
def save_links(spitor_db, links_list):

    spitor_db.insert_multiple_links(links_list)


# Update the last accessed time and accessibility of a link
def update_link(spitor_db, onion_link, accessible):

    spitor_db.update_link(onion_link, accessible)


# Return a new link to spider
def get_link(spitor_db):

    link = spitor_db.get_links(1)[0]

    return link
