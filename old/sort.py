#!/usr/bin/python
import os
import libtorrent as lt

walk_dir = '.'

#Creates sort dirs
if not os.path.exists("multifile"):
    os.makedirs("multifile")
if not os.path.exists("monofile"):
    os.makedirs("monofile")

#Sorts
for file in os.listdir(walk_dir):
    if str(file).endswith(".torrent"):
        print(file)
	info = lt.torrent_info(file)
	nf = info.num_files()
        if int(nf) > 1:
            os.rename(file,"multifile/" + file)
        else:
            os.rename(file,"monofile/" + file)

