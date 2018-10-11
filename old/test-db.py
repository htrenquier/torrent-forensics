import mysql.connector as mdb

connection = mdb.connect(user='maria', password='/ccf18', database='torrent', host='145.100.110.114')
cursor = connection.cursor()

cursor.execute("DESCRIBE torrent.file")
for i in cursor.fetchall():
	print(i)
print ("=====")
cursor.execute("DESCRIBE torrent.torrent_files")
for i in cursor.fetchall():
        print(i)

#DONT FORGET (?)
#connection.commit()



