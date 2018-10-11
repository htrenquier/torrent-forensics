

#aria2c --max-concurrent-downloads=10 -d torrents/ --input-file=links.txt --follow-torrent=false
from __future__ import print_function
import argparse
import os

# arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scrape", type=str, default="no",
        help="Show the video stream on the local machine")
ap.add_argument("-t", "--timer", type=int, required=False, default=9999,
        help="Set the time the script runs")
args = vars(ap.parse_args())

# cleanup routine
def cleanup():
    if os.path.isfile('items.csv'):
        os.system('rm items.csv')

print('Starting...')

# scrape routine
cleanup()
if args["scrape"] == 'yes':
    os.system("scrapy crawl limetorrent -o items.csv --nolog")
    with open('items.csv') as f:
        for i, line in enumerate(f):
            if i is not 0:
                Raw = line
                Raw2 = Raw.split('"')[1]
                Raw3 = Raw2.split(',')

                for i in Raw3:
                    if 'http' in i:
                        with open("links.txt", "a") as myfile:
                            myfile.write(i + '\n')

    print('Scraping done!')
    os.system('aria2c --max-concurrent-downloads=10 -d torrents/ --input-file=links.txt --follow-torrent=false')
cleanup()
