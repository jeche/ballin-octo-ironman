
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

class UpdateNowPlaying:
	def __init__(self):
		try:
		 	print("WhatWhat")
		 	self.connection = psycopg2.connect(host="localhost", database="OnlyMovies",
	 					user="jaleo", password="jaleo")
		 	print("What")

		except StandardError, e:
	 		print str(e)
	 		exit
		self.curr = self.connection.cursor()

		self.status_code = 200

	def clearTable(self):
		self.curr.execute("DELETE FROM NOW_PLAYING;")
		self.connection.commit()

	
	def insertMovies(self, mov_id,media_id, imdb_id, reldate, imdb_rating, rated):
		if(imdb_rating != 'N/A' and imdb_rating is not None):
			imdb_rating = float(imdb_rating)
			# print(imdb_rating, int(imdb_rating*10))
			if(rated is not None):
				self.curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, %d, \'%s\');" % (mov_id, media_id, imdb_id, reldate, imdb_rating*10,rated ))
			else:
				self.curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, %d, NULL);" % (mov_id, media_id, imdb_id, reldate, imdb_rating*10))

		elif(rated is not None):
			self.curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, \'%s\');" % (mov_id, media_id, imdb_id, reldate, rated))
		else:
			self.curr.execute("INSERT INTO MOVIES VALUES (%d, %d, \'%s\', \'%s\', NULL, NULL, NULL, NULL);" % (mov_id, media_id, imdb_id, reldate))
		
		self.connection.commit()
	

	def insertMedia(self,mov_id, title , poster):
		self.curr.execute("INSERT INTO MEDIA(Entry_ID, Title, Type, Poster) VALUES (%d, \'%s\', TRUE, \'%s\');" %(mov_id, title.replace("'"," "), poster))
		self.connection.commit()


	def insertNowPly(self, mov_id, reldate, runtime, descr):
		if(runtime != None and descr !=None):
			if(len(descr)>600):
				descr = descr[:599]
			self.curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, %d, \'%s\');" %(mov_id, int(runtime), descr.replace("'","")))
		elif(descr!=None):
			if(len(descr)>600):
				descr = descr[:599]
			self.curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, NULL, \'%s\');" %(mov_id, descr.replace("'","")))
		elif(runtime != None):
			self.curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, %d, NULL);" %(mov_id, int(runtime)))

		else:
			self.curr.execute("INSERT INTO NOW_PLAYING VALUES (%d, NULL, NULL);" %(mov_id))

		self.connection.commit()


	def fetchMovie(self, url):
		request = urllib2.Request(url, None, {'user-agent':'whatever'})
		opener = urllib2.build_opener()
		stream = opener.open(request)
		return json.load(stream)

	def yess(self,req):
		return bool(req['Response'])

	def get(self, url):
		request = urllib2.urlopen(url)

		self.status_code = request.getcode()
		if(self.status_code==200):
			return json.load(request)
		else:
			return None

	def run(self):
		while(True):
			pageNum  = 1
			reqCount = 1
			self.clearTable()
			movPage  = self.get(movieDB+inTheater)
			if(movPage is not None):
				totPgs = int(movPage["total_pages"])
				totRes = int(movPage["total_results"])
				print(totPgs, totRes)
				while(pageNum <= totPgs):
					currRes = movPage["results"]
					for movie in currRes:
						mov_id  = movie['id']
						title   = movie['original_title']
						reldate = movie['release_date']
						currMov   = self.get(movieDB+getMovie+str(movie["id"])+movieKey)
						reqCount +=1

						if(reqCount %30==0):
							time.sleep(10)

						if(currMov is not None and len(reldate) != 0):	
							descr   = currMov['overview']
							runtime = currMov['runtime']

							self.curr.execute("SELECT COUNT(*) FROM MOVIES WHERE MOVIE_ID=%d;" % mov_id)
							for i in self.curr:
								count = i[0]
							if(count==0):
								title   = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
								poster  = currMov['poster_path']
								imdb_id = str(currMov["imdb_id"])[2:]



								if(len(imdb_id)!=0):
									self.insertMedia(mov_id, title.replace("'",''), poster)
									self.connection.commit()
									cmd = "SELECT ID FROM MEDIA WHERE Entry_ID = %d;" % (mov_id)
									self.curr.execute(cmd)
									for i in self.curr:
										media_id = i[0]

									page     = self.fetchMovie(IMDB_CRAP+"tt"+imdb_id);
									rated = None
									imdb_rating = None
									if(self.yess(page)):

										if('imdbRating' in page):
											imdb_rating = page['imdbRating']
							
										
										if('Rated' in page):
											rated = page['Rated']
									

									self.insertMovies(mov_id, media_id, imdb_id, reldate, imdb_rating, rated)

									self.insertNowPly(mov_id, reldate, runtime, descr)
							else:
								self.insertNowPly(mov_id, reldate, runtime, descr)										
								
							print(mov_id, title, reqCount, pageNum)
						else:
							print("SHIT ",mov_id, " ",  self.status_code)

				   	pageNum  +=1
				   	if(pageNum <= totPgs):
						movPage  = self.get(movieDB+inTheater+"&page="+str(pageNum))
				   		if(self.status_code != 200):
				   			print("SUPER BAD CRAP OH MAN ", self.status_code,movieDB+inTheater+"&page="+str(pageNum) )
				   			exit
				   		reqCount+=1
						if(reqCount %30==0):
							time.sleep(10)
			time.sleep(60*60*24)


main = UpdateNowPlaying()
main.run()