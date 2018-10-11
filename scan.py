from __future__ import print_function
import argparse
import time
import binascii
import os
import sys
import MySQLdb
import hashlib

#sf stands for "stands for"
#pl sf "piece length"

piece_len=[32768,65536,131072,262144,524288,1048576,2097152,4194304,8388608]
db = MySQLdb.connect(host="145.100.110.114",
        user="maria",
        passwd="/ccf18",
        db="torrent",
        charset='utf8')

cur = db.cursor()

def check_first_block_hash(file,pl):
    with open(file, "rb") as f:
        chunk = f.read(pl)
        hash_sha1 = hashlib.sha1()
        hash_sha1.update(chunk)
        query = "SELECT info_hash, piece_hash_num FROM hashes WHERE piece_hash LIKE '" + str(hash_sha1.hexdigest()) + "';"
        #print(query)
        cur.execute(query)
        row = cur.fetchone()
        f.close()
        return row

def check_file_blocks(file,pl,info_hash,offset,expected_hashes):
    valid = 1
    with open(file, "rb") as f:
        nb_pieces = os.path.getsize(file) // pl
        print(str(nb_pieces) + " pieces in the file")
        #print(str(len(expected_hashes)) + " expected hashes.")
        for block in xrange(0,nb_pieces):
            f.seek(block*pl + offset)
            chunk = f.read(pl)
            hash_sha1 = hashlib.sha1()
            hash_sha1.update(chunk)

            if hash_sha1.hexdigest() == expected_hashes[block]:
                print("hash #" + str(block) + " @ offset " + str(block*pl) +" matches")
            else:
                valid = 0
                return valid, block*pl
    f.close()
    return valid,(os.path.getsize(file) - (nb_pieces*pl+offset))

def get_next_blocks_hashes_refs(info_hash): #for single files torrents
    query = "SELECT first_hash_block, hash_block_amount, unscanned_bytes FROM file WHERE info_hash LIKE '" + str(info_hash) + "';"
#    print(query)
    hash_list = []
    cur.execute(query)
    while True:
        row = cur.fetchone()
#        print(row)
        if row is None:
            print("IMPOSSIBLE")
        else:
            fhb,hba,ub = row[0],row[1],row[2]
            break
    return get_expected_hashes(info_hash,fhb,hba)

def get_expected_hashes(info_hash,fhb,hba):
    hash_list = []
    query = "SELECT piece_hash FROM hashes WHERE info_hash LIKE '" + info_hash + "' AND piece_hash_num >= " + str(fhb) +" AND piece_hash_num <= " + str(fhb+hba) + " ;"
#    print(query)
    cur.execute(query)
    while True:
        row = cur.fetchone()
        if row is None:
            break
        else:
            hash_list.append(str(row[0]))
    return hash_list

def get_file_by_name(filename):
    name = str(filename).replace("'","\\'")
#    print(name)
    query = "SELECT info_hash, first_block_offset, piece_length, first_hash_block, hash_block_amount, unscanned_bytes FROM file WHERE file_path LIKE '%" + name + "' AND first_block_offset_reliable ='yes';"
#    print(query)
    file_list = []
    cur.execute(query)
    while True:
        row = cur.fetchone()
        if row is None:
            return file_list
        else:
            file_list.append(row)

def get_file_by_size(file_size):
    query = "SELECT info_hash, first_block_offset, piece_length, first_hash_block, hash_block_amount, unscanned_bytes FROM file WHERE file_len =" + str(file_size) + " AND first_block_offset_reliable = 'yes';"
#    print(query)
    file_list = []
    cur.execute(query)
    while True:
        row = cur.fetchone()
        if row is None:
            return file_list
        else:
            file_list.append(row)

def check_file(file,row_list):
    valid = 0
    ub = 0
    for r in row_list:
        info_hash,fbo,pl,fhb,hba,ub = r[:]
        expected_hashes = get_expected_hashes(info_hash,fhb,hba)
        valid,ub =  check_file_blocks(file,pl,info_hash,fbo,expected_hashes)
        if valid == 1:
            break
    return valid, ub

# directory to scan
ScanDir = 'scan/'
# safe file list
safe_list = []
# unknown file list
unknown_file_list = []

for root, directories, filenames in os.walk(ScanDir):
    for filename in filenames:
        file_path = os.path.join(root, filename)
        file_size = os.path.getsize(file_path)
        file_can_be_excluded = 0
        print("##############################################################################")
        print(file_path)
        for pl in piece_len:
            if file_size >= pl:
                res = check_first_block_hash(file_path,pl)
                if res is None:
                    break
                else:
                    print(res[0])
                    info_hash = res[0] #info_hash
                    piece_hash_num = res[1]
                    if (piece_hash_num == 0):
                        expected_hashes = get_next_blocks_hashes_refs(info_hash)
                        file_can_be_excluded, uncomplete_block_offset = check_file_blocks(file_path,pl,info_hash,0,expected_hashes)
                        break
                    else:
                        print("UNLIKELY")
        #NAME LOOKUP
        if(file_can_be_excluded == 0):
            print("Lookup by name...")
            row_list = get_file_by_name(filename)
#            print(row_list)
            file_can_be_excluded, uncomplete_block_offset = check_file(file_path,row_list)

        #SIZE LOOKUP
        if(file_can_be_excluded == 0):
            print("Lookup by size...")
            row_list = get_file_by_size(file_size)
            print(row_list)
            file_can_be_excluded, uncomplete_block_offset = check_file(file_path,row_list)

        # REPORT
        if(file_can_be_excluded == 1):
            file_report = []
            file_report.append(file_path)
            file_report.append(uncomplete_block_offset)
            safe_list.append(file_report)
        else:
            file_report = []
            file_report.append(file_path)
            file_report.append(uncomplete_block_offset)
            unknown_file_list.append(file_report)

print()
print()
print("################ OS3 SNE CCF PROJECT ##############")
print()
print("Safe files:")
for fr in safe_list:
    print(fr)
print("Unknown files:")
for uf in unknown_file_list:
    print(uf)
