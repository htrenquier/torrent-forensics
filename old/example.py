#!/usr/bin/env python3
from __future__ import print_function
import sys
import pprint
import os
import bencode
import argparse
import os

# arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scrape", type=str, default="no",
        help="Scrape")
ap.add_argument("-e", "--extract", type=str, default="no",
        help="Get torrent info")
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


if args["extract"] == "yes":
    TorrentDir = 'torrents/'

    os.system('rm ' + TorrentDir + '*.html')
    TorrentFiles = os.listdir(TorrentDir)

    for name in TorrentFiles:
        print('Processing: ' + name)

        with open((TorrentDir + name), 'rb') as fh:
            torrent_bytes = fh.read()

        torrent = bencode.decode(torrent_bytes)
        outfilename = 'torrents.results/' + name + '.txt'

        print(torrent[0][b'info'][b'hash'])

        GetName = ("ccf2018_name: ", torrent[0][b'info'][b'name'])
        GetPieceLength = ("ccf2018_piece_length: ", torrent[0][b'info'][b'piece length'])
        with open(outfilename, 'a') as log:
            log.write(str(GetName) + '\n')
            log.write(str(GetPieceLength) + '\n')

        files = (torrent[0][b'info'][b'files'])
        for i, line in enumerate(files):
            with open(outfilename, 'a') as log:
                cast = str(line).split('{b\'length\': ')[-1]
                cast2 = cast.split(',')[0]
                cast3 = cast.split('b\'path\': [b\'')[1]
                cast4 = cast3.replace('\', b\'', ' ')
                cast5 = cast4.replace('\', b"', ' ')
                cast6 = cast5.replace('\']}', '')
                cast7 = cast6.replace('"]}', '')
                final = str(cast2) + ' ' + str(cast7)

                log.write(str('ccf2018_file ' + final) + '\n')

        string = ''
        piecehash = (torrent[0][b'info'][b'pieces'])
        for j, line2 in enumerate(piecehash):
            with open(outfilename, 'a') as log:
                convert = str(hex(line2)[2:].zfill(2))
                if len(convert) < 2:
                    convert = '0' + convert
                    if len(convert) < 2:
                        convert = '0' + convert
                if len(string) < 40:
                    string = string + convert

                if len(string) == 40:
                    log.write(str('SHA-1_piece_hash: ' + string) + '\n')
                    string = ''

cleanup()
