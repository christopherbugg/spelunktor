# Overview
spleunkTor is an [Onion Services](https://community.torproject.org/onion-services/) spider designed to find base onion links for another tool, unhidden (a tool for discovering the true IP of onion services). The point of have a custom-built spider instead of using an off-the-shelf variant (scapy, etc) is to have the freedom not offered by those other solutions and build one tailored to our specific use.

One of the biggest freedoms we have is to avoid limiting our search to well-constructed HTML and finding ANY (v3) .onion links anywhere.

# Requirements
- Python 3

# Usage
`python3 spelunktor.py [-h] [-v {0,1,2,3}] [-p PROCESSES]`

- This will create `database.db` and `links.txt` in your current directory
- `database.db` is used internally and can be ignored
- `links.txt` is the output file that's overwritten every 2 minutes and contains the list of base links found  

# Structure
## main controller (`spelunktor.py`)
- main loop
- spawns spiders as child processes
- outputs a links file for unhidden

## spider (`spitor.py`)
- child loops
- gets the oldest link in the database and crawls it
- once a site is crawled saves all found links in the database
- if link is dead, saves that info in the database

## database handler (`dbmanager.py`)
- handles all interaction to/from the db
- database keeps track of all found links, time checked, and accessibility

# Contributing
Contributions are welcome! Please open an issue to discuss!

# License
See [license](./license.md)