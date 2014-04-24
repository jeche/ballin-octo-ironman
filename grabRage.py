# INSERT INTO TV VALUES(1767,62649,'1990-09-08','1998-02-23', 80, 7);
# INSERT INTO TV VALUES(1920,62650,'1990-04-08','1991-06-10', 32, 2);
# INSERT INTO TV VALUES(549,62651,'1990-09-13','2010-05-24', 456, 20);



import urllib2
import psycopg2
import getpass
import sys 
import json
import time
import unicodedata
def yes(req):
	return int(req.status_code)==200

def fetchMovie(url):
	request = urllib2.Request(url, None, {'user-agent':'whatever'})
	opener = urllib2.build_opener()
	stream = opener.open(request)
	return json.load(stream)
def yess(req):
	return bool(req['Response'])

def main():



	try:
	 	print("WhatWhat")
	 	connection = psycopg2.connect(host="localhost",database="OnlyMovies",
 					user="jaleo", password="jaleo", port=63333)
	 	print("What")

	except StandardError, e:
	 	print str(e)
	 	exit


	curr = connection.cursor()
	search = 'http://services.tvrage.com/tools/quickinfo.php?show='

	try:


		curr.execute("SELECT TITLE, MEDIA_ID FROM MEDIA, TV WHERE MEDIA_ID = ID AND RAGE_ID IS NULL ORDER BY MEDIA_ID ASC;")
		retVals = curr.fetchall()
		for value in retVals:
			title = value[0]
			media_id = value[1]
			request = urllib2.urlopen(search+title.replace(" ", "%20")).read().split("\n")
			splits  = request[0].split("@")
			if(len(splits)==2):
				if (not isinstance(splits[1], int)):
					print(splits[1], media_id, title)
					curr.execute("SELECT COUNT(*) FROM TV WHERE RAGE_ID=%d;" % int(splits[1]))
					for i in curr:
						count = i[0]
					if(count==0):
						curr.execute("UPDATE TV SET RAGE_ID=%d WHERE MEDIA_ID=%d;"%(int(splits[1]), media_id))
						connection.commit()
	except StandardError, e:
		print "ERROR"
		print str(e)
	connection.commit()
main()