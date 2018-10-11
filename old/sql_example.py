#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb

db = MySQLdb.connect(host="192.168.0.23",
                     user="jonas",
                     passwd="jonas",
                     db="TestDB-004",
		     charset='utf8')

cur = db.cursor()

query = "CREATE TABLE IF NOT EXISTS `Games` ( "\
		"`ID` int(11) unsigned zerofill NOT NULL AUTO_INCREMENT, "\
		"`Name` longtext, "\
		"`FTP link` longtext, "\
		"PRIMARY KEY (`ID`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
cur.execute(query)
db.commit()

with open("games.data") as f: # The with keyword automatically closes the file when you are done
	for line in f:
		d = "ftp://data/Media/"+line.replace(" ","%20") # replace whitespaces with %20		        	
		FinalLink = d.replace("'", "\\'") # account for ' in weblinks
		
		system1, name2 = line.rsplit('/', 1) # split at last /
		FinalName = name2.replace("'", "\\'") # account for ` in names

		query = "INSERT INTO `TestDB-004`.`Games` "\
				"(`Name`, "\
				"`FTP link`) "\
				"VALUES "\
				"(\'"+FinalName+"\', "\
				"\'"+FinalLink+"\')" # tha query
		print query
		print FinalName
		print FinalLink
		cur.execute(query) # execute query
		db.commit() # Commit changes

#for row in cur.fetchall():
    #print row

db.close() # close db connection
