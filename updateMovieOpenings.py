
import threading

import urllib2
import psycopg2
import getpass
import sys 
import json
import time
import unicodedata



movieDB     = "https://api.themoviedb.org/3/"
movieKey    = "?api_key=709ba15ae33dc7539d0223508bdc6f0d"
inTheater   = "movie/now_playing"+movieKey
getMovie    = "movie/" 

IMDB_CRAP = "http://omdbapi.com/?i="
status_code = 200 

def get(url):
	request = urllib2.urlopen(url)

	status_code = request.getcode()
	if(status_code==200):
		return json.load(request)
	else:
		return None
def yes(req):
	return int(req.status_code)==200
def yess(req):
	return bool(req['Response'])
def fetchMovie(url):
	request = urllib2.Request(url, None, {'user-agent':'whatever'})
	opener = urllib2.build_opener()
	stream = opener.open(request)
	return json.load(stream)


# def nowPlaying():
# 	while(True):
# 		curr.execute("DELETE FROM NOW_PLAYING;")
# 		connection.commit()
# 		# curr.execute("CREATE TABLE OPENINGS_WEEK( \
# 		# M_ID int NOT NULL REFERENCES Movies(Movie_ID), \
# 		# Premiere_Date date, \
# 		# Running_Time int, \
# 		# Description VARCHAR(255), \
# 		# primary key(M_ID));")
# 		# connection.commit()
# 		# inTheaterLock.release()
# 		pageNum  = 1
# 		reqCount = 1
# 		movPage  = get(movieDB+inTheater)
# 		if(status_code == 200):
# 			totPgs = int(movPage["total_pages"])
# 			totRes = int(movPage["total_results"])
# 			print(totPgs, totRes)
# 			while(pageNum <= totPgs):
# 				currRes = movPage["results"]

# 		    	for movie in currRes:
# 		    		mov_id  = movie['id']
# 		    		title   = movie['original_title']
# 		    		reldate = movie['release_date']

# 		    		currMov   = get(movieDB+getMovie+str(movie["id"])+movieKey)
# 		    		reqCount +=1

# 		    		if(reqCount %30==0):
# 		    			time.sleep(10)

# 					if(status_code == 200):	
# 						descr   = currMov['overview']
# 						runtime = int(currMov['runtime'])

# 						curr.execute("SELECT COUNT(*) FROM MOVIES WHERE MOVIE_ID=%d;")
# 			    		for i in curr:
# 			    			count = i[0]
# 			    		if(count==0):
# 							title   = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
# 							poster  = currMov['poster_path']
# 							imdb_id = str(currMov["imdb_id"])[2:]

# 							curr.execute("INSERT INTO MEDIA(Entry_ID, Title, Type, Poster) VALUES (%d, \'%s\', TRUE, \'%s\');" %(mov_id, tit.replace("'"," "), poster))
# 							connection.commit()
# 							curr.execute("SELECT ID FROM MEDIA WHERE Entry_ID = %d;" % mov_id)
# 							for i in curr:
# 								media_id = i[0]

# 							if(len(imdb_id)!=0):
# 								curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, NULL);" % (mov_id, media_id, imdb_id, reldate))
# 								connection.commit()

# 			    		curr.execute("INSERT INTO OPENINGS_WEEK VALUES (%d, \'%s\', %d, \'%s\');" %(mov_id, reldate, runtime, descr))
# 			    	else:
# 			    		print("SHIT ",mov_id, " ", status_code)


# 			   	currNum  +=1
# 			   	if(currNum <= totPgs):
# 					movPage  = get(movieDB+inTheater+"&page="+str(currNum))
# 			   		if(status_code != 200):
# 			   			print("SUPER BAD CRAP OH MAN ", status_code,movieDB+inTheater+"&page="+str(currNum) )
# 			   			exit
# 			   		currRes  = movPage['results']
# 			   		reqCount+=1
# 					if(reqCount %30==0):
# 						time.sleep(10)

def main():

	try:
	 	print("WhatWhat")
	 	connection = psycopg2.connect(host="localhost", database="OnlyMovies",
 					user="jaleo", password="jaleo")
	 	print("What")

	except StandardError, e:
	 	print str(e)
	 	exit
# handler = urllib2.urlopen('https://api.themoviedb.org/3/movie/now_playing?api_key=709ba15ae33dc7539d0223508bdc6f0d')
	curr = connection.cursor()
	inTheaterLock  = threading.Lock()
	tvScheduleLock = threading.Lock()

	# inTheaterLock.acquire()
	curr.execute("DELETE FROM NOW_PLAYING;")
	connection.commit()
	# curr.execute("CREATE TABLE OPENINGS_WEEK( \
	# M_ID int NOT NULL REFERENCES Movies(Movie_ID), \
	# Premiere_Date date, \
	# Running_Time int, \
	# Description VARCHAR(255), \
	# primary key(M_ID));")
	# connection.commit()
	# inTheaterLock.release()
	pageNum  = 1
	reqCount = 1
	movPage  = get(movieDB+inTheater)
	if(status_code == 200):
		totPgs = int(movPage["total_pages"])
		totRes = int(movPage["total_results"])
		print(totPgs, totRes)
		while(pageNum <= totPgs):
			currRes = movPage["results"]
			for movie in currRes:
				mov_id  = movie['id']
				title   = movie['original_title']
				reldate = movie['release_date']
				currMov   = get(movieDB+getMovie+str(movie["id"])+movieKey)
				reqCount +=1

				if(reqCount %30==0):
					time.sleep(10)

				if(status_code == 200):	
					descr   = currMov['overview']
					runtime = currMov['runtime']

					curr.execute("SELECT COUNT(*) FROM MOVIES WHERE MOVIE_ID=%d;" % mov_id)
					for i in curr:
						count = i[0]
					if(count==0):
						title   = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
						poster  = currMov['poster_path']
						imdb_id = str(currMov["imdb_id"])[2:]



						if(len(imdb_id)!=0):
							curr.execute("INSERT INTO MEDIA(Entry_ID, Title, Type, Poster) VALUES (%d, \'%s\', TRUE, \'%s\');" %(mov_id, title.replace("'"," "), poster))
							connection.commit()
							cmd = "SELECT ID FROM MEDIA WHERE Entry_ID = %d;" % (mov_id)
							curr.execute(cmd)
							for i in curr:
								media_id = i[0]
							page     = fetchMovie(IMDB_CRAP+"tt"+imdb_id);
							if(yess(page)):
								rated = None
								imdb_rating = None
								if('imdbRating' in page):
									imdb_rating = page['imdbRating']
					
								
								if('Rated' in page):
									rated = page['Rated']
								if(imdb_rating != 'N/A' and imdb_rating is not None):
									imdb_rating = float(imdb_rating)
									# print(imdb_rating, int(imdb_rating*10))
									if(rated is not None):
										curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, %d, \'%s\');" % (mov_id, media_id, imdb_id, reldate, imdb_rating*10,rated ))
									else:
										print(page)
										curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, %d, NULL);" % (mov_id, media_id, imdb_id, reldate, imdb_rating*10))

								elif(rated is not None):
									curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, \'%s\');" % (mov_id, media_id, imdb_id, reldate, rated))
								else:
									print(page)
									curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, NULL);" % (mov_id, media_id, imdb_id, reldate))

							else:
								curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, NULL);" % (mov_id, media_id, imdb_id, reldate))

							connection.commit()
							if(runtime != None and descr !=None):
								if(len(descr)>600):
									descr = descr[:599]
								curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, \'%s\', %d, \'%s\');" %(mov_id, reldate, int(runtime), descr.replace("'","")))
							elif(descr!=None):
								if(len(descr)>600):
									descr = descr[:599]
								curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, \'%s\', NULL, \'%s\');" %(mov_id, reldate, descr.replace("'","")))
							elif(runtime != None):
								curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, \'%s\', %d, NULL);" %(mov_id, reldate, int(runtime)))

							else:
								curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, \'%s\', NULL, NULL);" %(mov_id, reldate))

					connection.commit()
					print(mov_id, title, reqCount, pageNum)
				else:
					print("SHIT ",mov_id, " ", status_code)


		   	pageNum  +=1
		   	if(pageNum <= totPgs):
				movPage  = get(movieDB+inTheater+"&page="+str(pageNum))
		   		if(status_code != 200):
		   			print("SUPER BAD CRAP OH MAN ", status_code,movieDB+inTheater+"&page="+str(pageNum) )
		   			exit
		   		reqCount+=1
				if(reqCount %30==0):
					time.sleep(10)

	# time.sleep(60*60*24)
main()