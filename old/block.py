import libtorrent as lt
import time
import binascii
import os
import sys

print (sys.version)
#READ TORRENT FILE
#torrent = open('test.torrent','rb').read()
#info = lt.torrent_info(torrent, len(torrent))
##info = lt.bdecode(open("test.torrent", 'rb').read())

#https://stackoverflow.com/questions/12058802/how-use-libtorrent-for-python-to-get-info-hash
#prev link doesn't work
#torrent_file = open('test.torrent','rb').read()

#READ TORRENT FILE INFO
#info = lt.torrent_info('test.torrent')
TorrentDir = 'torrents/'

os.system('rm ' + TorrentDir + '*.html')
TorrentFiles = os.listdir(TorrentDir)

for name in TorrentFiles:
    print(name)
    e = lt.bdecode(open(TorrentDir + name, 'rb').read())
    info = lt.torrent_info(e)

    #PRINT INFOS
    info_hash = info.info_hash()
    print ("info_hash: " + str(info_hash))

    info_hash_hex = str(info_hash)
    print ("Hex of info_hash: " + str(info_hash_hex))

    #integer = int(hexadecimal, 16)
    #print "Int of info_hash: " + str(integer)

    nf = info.num_files()
    print (str(nf) + "files")

    #FILE NAMES
    files = info.files()
    #print files

    print(files.piece_length())
    print(files.hash(0))
    print(files.file_path(0))
    #print (files[0])
    #print (files[0].path)
    print ("===============================")
    for k in range(0,nf):
	print(files.file_path(k))
        #
        print(files.hash(k))
        #print(files.file_name(k))
        print(files.file_offset(k))
        print(files.file_size(k))
        print(files.file_path(k))

        #####################

    #METAINFOS
    np = info.num_pieces()
    print (str(info.num_pieces()) + " pieces in the torrent file.")
    print ("Piece length = " + str(info.piece_length()) + " bytes.")

    block_hash_hex = []

    for i in range(0,np):
        block_hash_hex.append(info.hash_for_piece(i))
        #uncomment below to see the hashes
        #print binascii.hexlify(block_hash_hex[i])

print(binascii.hexlify(block_hash_hex[i]))
