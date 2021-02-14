# Pathfinder-Insight
Simple search-engine tailored for www.d20pfsrd.com

###Usage
To start the engine from command line:

`python PathfinderInsight.py`

###Installation
####Requirements:
- Python 3.8 (I used Anaconda tu set up the environment)
- PySimpleGUI: `pip install PySimpleGUI`
- Whoosh: `pip install Whoosh`

Unzip the whole project in a directory of your choosing and start the
search engine.

###To use the crawler
####Requirements:
- Scrapy: `pip install scrapy`
- html2text: `pip install html2text`
- Sanitize_filename: `pip install sanitize-filename`

Run from this directory in the command line:
`scrapy crawl pfsrd`


###Notes
To watch the crawler log file in powershell:

`get-content .\crawler.log -wait -tail 1`
