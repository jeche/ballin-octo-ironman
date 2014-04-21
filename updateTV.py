
import threading

import urllib2
import psycopg2
import getpass
import sys 
import json
import time
import unicodedata
from xml.dom.minidom import parseString
from xml.dom import minidom
import xml.etree.ElementTree as ET

from HTMLParser import HTMLParser

movieDB     = "https://api.themoviedb.org/3/"
movieKey    = "?api_key=709ba15ae33dc7539d0223508bdc6f0d"
inTheater   = "movie/now_playing"+movieKey
getMovie    = "movie/" 
otherTvSchd = 'http://services.tvrage.com/tools/quickschedule.php'
tvschedule  = 'http://services.tvrage.com/feeds/fullschedule.php?country=US&24_format=1'
status_code = 200
temp_file   = open('tv_sched2.txt', 'w')
class DescripFind(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.recording = 0
    self.data = []

  def handle_starttag(self, tag, attrs):
    if tag != 'div' or len(attrs)!=2:
      return
    if self.recording:
      self.recording += 1
      return
    if('left padding_bottom_10' in attrs[0] and 'vertical-align: top;'in attrs[1]):
    	self.recording = 1
    else:
      return


  def handle_endtag(self, tag):
    if tag == 'div' and self.recording:
      self.recording -= 1

  def handle_data(self, data):
    if self.recording:
      self.data.append(data)



def get(url):
	request = urllib2.urlopen(url)

	status_code = request.getcode()
	if(status_code==200):
		return json.load(request.read())
	else:
		return None


def otherGet(url):
	request = urllib2.urlopen(url)
	status_code = request.getcode()
	bitch = request.read()
	return bitch
def main():
	try:
	 	print("WhatWhat")
	 	connection = psycopg2.connect(host="localhost", database="OnlyMovies",
 					user="jaleo", password="jaleo")
	 	print("What")

	except StandardError, e:
	 	print str(e)
	 	exit
	curr = connection.cursor()
	page =  otherGet(tvschedule)
	print(status_code)
	dom    = parseString(page)
	xmlTag = dom.getElementsByTagName('DAY')
	curr.execute("DELETE FROM CURRENT_TV_SCHEDULE;")

	connection.commit()
	for i in range(7):
		day = xmlTag[i].attributes
		# print(day['attr'].value)
		
		date = day['attr'].value
		modDate = date.split("-")
		year  = modDate[0]
		month = modDate[1]
		day   = modDate[2]
		if(len(day)==1):
			day = "0"+day
		if(len(month)==1):
			month ="0"+month
		date = year+"-"+month+"-"+day
		times = xmlTag[i].getElementsByTagName('time')
		for value in times:
			time = value.attributes['attr'].value
			time = time+":00"
			shows = value.getElementsByTagName('show')
			for show in shows:
				

				rage_id = int(show.getElementsByTagName('sid')[0].childNodes[0].nodeValue)
				curr.execute("SELECT tv_id from tv where rage_id=%d;" % rage_id)
				tv_id = None
				for i in curr:
					tv_id = i[0]
				if(tv_id is not None):
					title   = show.getElementsByTagName('title')[0].childNodes[0].nodeValue
					title   = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore') 
					epiSea  = show.getElementsByTagName('ep')[0].childNodes[0].nodeValue
					epiSea  = unicodedata.normalize('NFKD', epiSea).encode('ascii', 'ignore')
					network = show.getElementsByTagName('network')[0].childNodes[0].nodeValue
					network = unicodedata.normalize('NFKD', network).encode('ascii', 'ignore')

					if(len(epiSea.split("x"))!=2):
						episode = None
						season  = epiSea
					else:
						episode = epiSea.split("x")[0]
						season  = epiSea.split("x")[1]
					link   = show.getElementsByTagName('link')[0].childNodes[0].nodeValue
					RagePage   = urllib2.urlopen(link).read()
					parser = DescripFind()
					parser.feed(RagePage)
					# print(rage_id, title, episode, season, link)
					# print(show.attributes['name'].value, date, time)
					
					insert  = ""
					full_date = date+" "+time
					if(len(parser.data) > 0):
						if('Episode number: ' not in parser.data[0]):
							if (not isinstance(parser.data[0], str)):
								print("other")
								descrp = unicodedata.normalize('NFKD', parser.data[0]).encode('ascii', 'ignore')
							else:
								# print("here")
								unicode_str = parser.data[0].decode('ascii', 'replace')
	   							utf8_str = unicodedata.normalize('NFKD', unicode_str).encode('ascii', 'ignore')
								descrp = utf8_str
								if(len(descrp)>600):
									descrp = descrp[:599]
							if(episode is not None):
								curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\');" %(tv_id, full_date, title.replace("'", ''), network, episode, season, descrp.replace("'",'')))
							else:
								curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', NULL,\'%s\',\'%s\');" %(tv_id, full_date, title.replace("'", ''), network, season, descrp.replace("'",'')))

					else:
						if(episode is not None):
							curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',NULL);" %(tv_id, full_date, title.replace("'", ''), network, episode, season))

							temp_file.write("%d , \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', NULL, \'%s\'" %(rage_id, title.replace("'",""), episode, season, date, time,network))
						else:
							curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', NULL,\'%s\',NULL);" %(tv_id, full_date, title.replace("'", ''), network, season))
					connection.commit()
					temp_file.write("\n")
# print(RagePage)	

# lines = RagePage.split("<div class=\"left padding_bottom_10\" style=\"vertical-align: top;\">")
# print(len(lines))
# print('<div class=\"left padding_bottom_10\" style=\"vertical-align: top;\">')


			#print(value.toxml())
				# print itemlist[0].attributes['name'].value
		# tree = ET.parse(day)
		# root = tree.getroot()
		# print(root.tag)











































































# 	try:
# 	 	print("WhatWhat")
# 	 	connection = psycopg2.connect(host="localhost", database="OnlyMovies",
#  					user="jaleo", password="jaleo")
# 	 	print("What")

# 	except StandardError, e:
# 	 	print str(e)
# 	 	exit
# # handler = urllib2.urlopen('https://api.themoviedb.org/3/movie/now_playing?api_key=709ba15ae33dc7539d0223508bdc6f0d')
# 	curr = connection.cursor()
# 	inTheaterLock  = threading.Lock()
# 	tvScheduleLock = threading.Lock()

# 	# inTheaterLock.acquire()
# 	curr.execute("DELETE FROM ;")
# 	connection.commit()
# 	# curr.execute("CREATE TABLE OPENINGS_WEEK( \
# 	# M_ID int NOT NULL REFERENCES Movies(Movie_ID), \
# 	# Premiere_Date date, \
# 	# Running_Time int, \
# 	# Description VARCHAR(255), \
# 	# primary key(M_ID));")
# 	# connection.commit()
# 	# inTheaterLock.release()
# 	pageNum  = 1
# 	reqCount = 1
# 	movPage  = get(movieDB+inTheater)
# 	if(status_code == 200):
# 		totPgs = int(dic["total_pages"])
# 		totRes = int(dic["total_results"])
# 		print(totPgs, totRes)
# 		while(pageNum <= totPgs):
# 			currRes = dic["results"]

# 	    	for movie in currRes:
# 	    		mov_id  = movie['id']
# 	    		title   = movie['original_title']
# 	    		reldate = movie['release_date']

# 	    		currMov   = get(movieDB+getMovie+str(movie["id"])+movieKey)
# 	    		reqCount +=1

# 	    		if(reqCount %30==0):
# 	    			time.sleep(10)

# 				if(status_code == 200):	
# 					descr   = currMov['overview']
# 					runtime = int(currMov['runtime'])

# 					curr.execute("SELECT COUNT(*) FROM MOVIES WHERE MOVIE_ID=%d;")
# 		    		for i in curr:
# 		    			count = i[0]
# 		    		if(count==0):
# 						title   = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
# 						poster  = currMov['poster_path']
# 						imdb_id = str(currMov["imdb_id"])[2:]

# 						curr.execute("INSERT INTO MEDIA(Entry_ID, Title, Type, Poster) VALUES (%d, \'%s\', TRUE, \'%s\');" %(mov_id, tit.replace("'"," "), poster))
# 						connection.commit()
# 						curr.execute("SELECT ID FROM MEDIA WHERE Entry_ID = %d;" % mov_id)
# 						for i in curr:
# 							media_id = i[0]

# 						if(len(imdb_id)!=0):
# 							curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, NULL);" % (mov_id, media_id, imdb_id, reldate))
# 							connection.commit()

# 		    		curr.execute("INSERT INTO OPENINGS_WEEK VALUES (%d, \'%s\', %d, \'%s\');" %(mov_id, reldate, runtime, descr))
# 		    	else:
# 		    		print("SHIT ",mov_id, " ", status_code)


# 		   	currNum  +=1
# 		   	if(currNum <= totPgs):
# 				movPage  = get(movieDB+inTheater+"&page="+str(currNum))
# 		   		if(status_code != 200):
# 		   			print("SUPER BAD CRAP OH MAN ", status_code,movieDB+inTheater+"&page="+str(currNum) )
# 		   			exit
# 		   		currRes  = dic['results']
# 		   		reqCount+=1
# 				if(reqCount %30==0):
# 					time.sleep(10)

	# time.sleep(60*60*24)
main()