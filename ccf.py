

#aria2c --max-concurrent-downloads=10 -d torrents/ --input-file=links.txt --follow-torrent=false
from __future__ import print_function
from prettytable import PrettyTable
import argparse
import libtorrent as lt
import time
import binascii
import os
import sys
import MySQLdb
import hashlib
import datetime


# arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scrape", type=str, default="no",
        help="Scrape torrent files from the internet")
ap.add_argument("-m", "--meta", type=str, default="no",
        help="Extract meta information from torrent files")
ap.add_argument("-d", "--database", type=str, default="no",
        help="Populate database with meta information")
ap.add_argument("-S", "--scan", type=str, default="no",
        help="Populate database with meta information")
ap.add_argument("-Z", "--scanpath", type=str, default="no",
        help="Set the scanning path")
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

if args["meta"] == 'yes':
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
        outfilename = 'torrents.results/' + name + '.txt'

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Name: " + name)
        e = lt.bdecode(open(TorrentDir + name, 'rb').read())
        info = lt.torrent_info(e)

        #PRINT INFOS
        info_hash = info.info_hash()
        print ("info_hash: " + str(info_hash))

        info_hash_hex = str(info_hash)
        #print ("Hex of info_hash: " + str(info_hash_hex))

        #integer = int(hexadecimal, 16)
        #print "Int of info_hash: " + str(integer)

        nf = info.num_files()
        print ("File amount: " + str(nf))

        #FILE NAMES
        files = info.files()
        #print files

        print("File piece length: " + str(files.piece_length()))
        #print("File hash: " + str(files.hash(0)))
        #print("File path: " + str(files.file_path(0)))
        #print (files[0])
        #print (files[0].path)
        print(str(files.total_size()))

        with open(outfilename, 'a') as log:
            log.write(str("Name: " + name) + '\n')
            log.write(str("info_hash: " + str(info_hash)) + '\n')
            #log.write(str("Hex of info_hash: " + str(info_hash_hex)) + '\n')
            log.write("File amount: " + str(str(nf)) + '\n')
            log.write("File piece length: " + str(files.piece_length()) + '\n')
            log.write("Total size: " + str(files.total_size()) + '\n')
            #log.write("File hash: " + str(files.hash(0)) + '\n')
            #log.write(str("File path: " + str(files.file_path(0))) + '\n')

        #METAINFOS
        np = info.num_pieces()
        print ("Pieces in torrent file: " + str(info.num_pieces()))
        #print ("Piece length (bytes): " + str(info.piece_length()))
        with open(outfilename, 'a') as log:
            log.write("Pieces in torrent file: " + str(info.num_pieces()) + '\n')
            #log.write("Piece length (bytes): " + str(info.piece_length()) + '\n')

        print ("===============================")
        for k in range(0,nf):
	    print("File path: " + files.file_path(k))
            print(files.hash(k))
            print(files.file_offset(k))
            print(files.file_size(k))

            first_block_offset =(files.piece_length() - (files.file_offset(k) % files.piece_length()))%files.piece_length()
            print("fbo= " + str(first_block_offset))

            if ((first_block_offset + files.piece_length()) <= files.file_size(k)):
                FirstBlockOffsetReliable = 'yes'
            else:
                FirstBlockOffsetReliable = 'no'

            first_block_to_hash = (files.file_offset(k) + first_block_offset) // files.piece_length()
            readable_block_num = (files.file_size(k) - first_block_offset) // files.piece_length()
            unhashed_byte_num = (files.file_size(k) - first_block_offset) % files.piece_length()
            print(first_block_to_hash)
            print(readable_block_num)
            print(unhashed_byte_num)

            with open(outfilename, 'a') as log:
                log.write(str("File path: " + files.file_path(k)) + '|||' + \
                    str(files.hash(k)) + '|||' + \
                    str(files.file_offset(k)) + '|||' + \
                    str(files.file_size(k)) + '|||' + \
                    str(first_block_offset) + '|||' + \
                    str(FirstBlockOffsetReliable) + '|||' + \
                    str(first_block_to_hash) + '|||' + \
                    str(readable_block_num) + '|||' + \
                    str(files.piece_length()) + '|||' + \
                    str(unhashed_byte_num)  + "\n")

        block_hash_hex = []

        for i in range(0,np):
            block_hash_hex.append(info.hash_for_piece(i))
            #uncomment below to see the hashes
            #print (binascii.hexlify(block_hash_hex[i]))
            with open(outfilename, 'a') as log:
                log.write("SHA-1 hash: " + str(binascii.hexlify(block_hash_hex[i])) + '\n')

if args["database"] == 'yes':
    db = MySQLdb.connect(host="145.100.110.114",
        user="maria",
        passwd="/ccf18",
        db="torrent",
        charset='utf8')

    cur = db.cursor()

    query = "CREATE TABLE IF NOT EXISTS `hashes` ( "\
        "`id` INT(11) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT, "\
        "`info_hash` CHAR(41) NULL DEFAULT NULL, "\
        "`piece_hash_num` INT(21) NULL DEFAULT NULL, "\
        "`piece_hash` TEXT NULL, "\
        "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(query)
    query = "CREATE TABLE IF NOT EXISTS `torrent_files` ( "\
        "`info_hash` CHAR(41) NOT NULL, "\
        "`multifile` TINYINT(1) NULL DEFAULT NULL, "\
        "`torrent_name` TEXT NULL, "\
        "`piece_len` INT(41) NULL DEFAULT NULL, "\
        "`file_num` TEXT NULL, "\
        "`piece_num` TEXT NULL, "\
        "`total_size` TEXT NULL, "\
        "PRIMARY KEY (`info_hash`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(query)
    query = "CREATE TABLE IF NOT EXISTS `file` ( "\
        "`id` INT(11) NOT NULL AUTO_INCREMENT, "\
        "`file_num` INT(21) NULL DEFAULT NULL, "\
        "`info_hash` CHAR(41) NOT NULL, "\
        "`file_len` INT(21) NULL DEFAULT NULL, "\
        "`file_offset` DECIMAL(41) NULL DEFAULT NULL, "\
        "`first_block_offset` INT(21) NULL DEFAULT NULL, "\
        "`first_block_offset_reliable` CHAR(3) NULL DEFAULT NULL, "\
        "`first_hash_block` INT(11) NULL DEFAULT NULL, "\
        "`hash_block_amount` INT(11) NULL DEFAULT NULL, "\
        "`piece_length` INT(11) NULL DEFAULT NULL, "\
        "`unscanned_bytes` INT(11) NULL DEFAULT NULL, "\
        "`file_path` TEXT NULL, "\
        "`file_hash` TEXT NULL, "\
        "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    cur.execute(query)
    db.commit()

    ResultsDir = 'torrents.results/'
    ResultFiles = os.listdir(ResultsDir)

    for name in ResultFiles:
        print('Proccessing file: ' + name)
        outfilename = 'torrents.results/' + name
        with open(outfilename) as f:
            ArrayResults = []
            ArrayHashResults = []
            ArrayFileResults = []
            for i, line in enumerate(f):
                if i < 6:
                    ArrayResults.append(line.strip("\n"))
                if 'SHA-1 hash: ' in line:
                    ArrayHashResults.append(line.strip("\n"))
                if 'File path: ' in line:
                    ArrayFileResults.append(line.strip("\n"))

            TorrentName = ArrayResults[0].split('Name: ')[1]
            InfoHash = ArrayResults[1].split('info_hash: ')[1]
            FileAmount = ArrayResults[2].split('File amount: ')[1]
            FilePieceLength = ArrayResults[3].split('File piece length: ')[1]
            TotalSize = ArrayResults[4].split('Total size: ')[1]
            PiecesInTorrentFile = ArrayResults[5].split('Pieces in torrent file: ')[1]

            query = "INSERT INTO `torrent`.`torrent_files` "\
                                "(`info_hash`, "\
                                "`torrent_name`, "\
                                "`piece_len`, "\
                                "`file_num`, "\
                                "`piece_num`, "\
                                "`total_size`) "\
                                "VALUES "\
                                "(\'"+InfoHash+"\', "\
                                "\'"+TorrentName+"\', "\
                                "\'"+FilePieceLength+"\', "\
                                "\'"+FileAmount+"\', "\
                                "\'"+PiecesInTorrentFile+"\', "\
                                "\'"+TotalSize+"\')"
            cur.execute(query) # execute query

            for i, line in enumerate(ArrayFileResults):
                FileAllInfo = line.split('File path: ')[1]
                FileInfoSplit = FileAllInfo.split('|||')
                FilePath = FileInfoSplit[0].replace("'", "\\'")
                FileHash = FileInfoSplit[1]
                FileOffset = FileInfoSplit[2]
                FileSize = FileInfoSplit[3]
                FirstBlockOffset = FileInfoSplit[4]
                FirstBlockOffsetReliable = FileInfoSplit[5]
                FirstHashBlock = FileInfoSplit[6]
                HashBlockAmount = FileInfoSplit[7]
                FilePieceLength = FileInfoSplit[8]
                UnscannedBytes = FileInfoSplit[9]

                query = "INSERT INTO `torrent`.`file` "\
                                "(`info_hash`, "\
                                "`file_num`, "\
                                "`file_len`, "\
                                "`file_offset`, "\
                                "`file_path`, "\
                                "`file_hash`, "\
                                "`first_block_offset`, "\
                                "`first_block_offset_reliable`, "\
                                "`first_hash_block`, "\
                                "`hash_block_amount`, "\
                                "`piece_length`, "\
                                "`unscanned_bytes`) "\
                                "VALUES "\
                                "(\'"+InfoHash+"\', "\
                                "\'"+str(i)+"\', "\
                                "\'"+FileSize+"\', "\
                                "\'"+FileOffset+"\', "\
                                "\'"+FilePath+"\', "\
                                "\'"+FileHash+"\', "\
                                "\'"+FirstBlockOffset+"\', "\
                                "\'"+FirstBlockOffsetReliable+"\', "\
                                "\'"+FirstHashBlock+"\', "\
                                "\'"+HashBlockAmount+"\', "\
                                "\'"+FilePieceLength+"\', "\
                                "\'"+UnscannedBytes+"\')"
                cur.execute(query) # execute query

            for i, line in enumerate(ArrayHashResults):
                Hash = line.split('SHA-1 hash: ')[1]
                query = "INSERT INTO `torrent`.`hashes` "\
                                "(`info_hash`, "\
                                "`piece_hash_num`, "\
                                "`piece_hash`) "\
                                "VALUES "\
                                "(\'"+InfoHash+"\', "\
                                "\'"+str(i)+"\', "\
                                "\'"+Hash+"\')"
                cur.execute(query) # execute query
            db.commit() # Commit changes

if args["scan"] == 'yes':
    t = PrettyTable(['Scanned File', 'Hash Blocks', 'File in DB', 'unscanned bytes (first)', 'unscanned bytes (last)', 'File size (DB)', 'File size (disk)'])
    t.title = 'os3'

    StartDate = datetime.datetime.now()
    db = MySQLdb.connect(host="145.100.110.114",
        user="maria",
        passwd="/ccf18",
        db="torrent",
        charset='utf8')
    cur = db.cursor()

    # get all info hashes from db
    query = "SELECT info_hash, file_len, first_block_offset, first_hash_block, hash_block_amount, piece_length, unscanned_bytes, file_path FROM file WHERE first_block_offset_reliable='yes'"
    cur.execute(query)
    TorrentFiles = []
    while True:
        row = cur.fetchone()
        if row == None:
            break
        TorrentFiles.append(row)

    # for each info hash do
    for i in TorrentFiles:
        #print(i[7])

        # directory to scan
        ScanDir = args["scanpath"]
        for root, directories, filenames in os.walk(ScanDir):
            for filename in filenames:
                FilePath = os.path.join(root, filename)
                #print(FilePath)
                #print(i[0])

                HashBlocksMatch = 0
                with open(FilePath, "rb") as f:
                    HashIterate = 0
                    f.seek(i[2])
                    for chunk in iter(lambda: f.read(i[5]), b""):
                        query = "SELECT piece_hash FROM hashes WHERE info_hash=" + "'" + i[0] + "'" + " AND piece_hash_num=" + "'" + str(i[3] + HashIterate) + "'"
                        cur.execute(query)
                        CurrentHashPiece = cur.fetchone()
                        hash_sha1 = hashlib.sha1()
                        hash_sha1.update(chunk)

                        if CurrentHashPiece[0] == hash_sha1.hexdigest():
                            HashBlocksMatch = HashBlocksMatch + 1
                            print(FilePath + " -- " + str(HashIterate) + " hash block match! -- with -- " + i[7])
                        else:
                            break
                        HashIterate = HashIterate + 1
                        if HashIterate == i[4]:
                            break

                    if HashBlocksMatch > 0:
                        t.add_row([FilePath, (str(HashBlocksMatch) + '/' + str(i[4])), i[7], i[2], i[6], i[1], os.path.getsize(FilePath)])
                        #print(hash_sha1.hexdigest())

        #query = "SELECT file_path FROM file WHERE info_hash LIKE " + "'" + i + "'"
        #cur.execute(query)
        #while True:
        #    row = cur.fetchone()
        #    if row == None:
        #        break
        #    print(row[0])

        #query = "SELECT piece_hash_num, piece_hash FROM hashes WHERE info_hash LIKE " + "'" + i + "'"
        #cur.execute(query)
        #while True:
        #    row = cur.fetchone()
        #    if row == None:
        #        break
            #print(str(row[0]) + ": " + str(row[1]))

    db.close()
    StopDate = datetime.datetime.now()
    RunTime = StopDate - StartDate

    with open('scan.results.txt', 'w') as log:
        log.write('                    _____              __          _____    _   __    ______' + "\n")
        log.write('    ____    _____  |__  /            _/_/         / ___/   / | / /   / ____/' + "\n")
        log.write('   / __ \  / ___/   /_ <           _/_/           \__ \   /  |/ /   / __/   ' + "\n")
        log.write('  / /_/ / (__  )  ___/ /         _/_/            ___/ /  / /|  /   / /___   ' + "\n")
        log.write('  \____/ /____/  /____/         /_/             /____/  /_/ |_/   /_____/   ' + "\n")
        log.write('                                                                            ' + "\n")
        log.write(str(t))
    print("\n\n\n")
    print('                    _____              __          _____    _   __    ______')
    print('    ____    _____  |__  /            _/_/         / ___/   / | / /   / ____/')
    print('   / __ \  / ___/   /_ <           _/_/           \__ \   /  |/ /   / __/   ')
    print('  / /_/ / (__  )  ___/ /         _/_/            ___/ /  / /|  /   / /___   ')
    print('  \____/ /____/  /____/         /_/             /____/  /_/ |_/   /_____/   ')
    print('                                                                            ')
    print(str(t))
    print("runtime: " + str(RunTime))
