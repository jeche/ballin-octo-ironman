
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

class UpdateTv:
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


	def get(self, url):
		request = urllib2.urlopen(url)

		self.status_code = request.getcode()
		if(self.status_code==200):
			return json.load(request.read())
		else:
			return None


	def otherGet(self, url):
		request = urllib2.urlopen(url)
		self.status_code = request.getcode()
		bitch = request.read()
		return bitch

	def clearTable(self):
		self.curr.execute("DELETE FROM CURRENT_TV_SCHEDULE;")
		self.connection.commit()


	def insertCurrTV(self, tv_id, full_date, title, network, episode, season, descrip):
		if(episode is not None and descrip is not None):
			self.curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\');" %(tv_id, full_date, title.replace("'", ''), network, episode, season, descrp.replace("'",'')))
		elif(episode is None and descrip is not None):
			self.curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', NULL,\'%s\',\'%s\');" %(tv_id, full_date, title.replace("'", ''), network, season, descrp.replace("'",'')))

		elif(episode is not None and descrip is None):
			self.curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', \'%s\',\'%s\',NULL);" %(tv_id, full_date, title.replace("'", ''), network, episode, season))

		else:
			self.curr.execute("INSERT INTO CURRENT_TV_SCHEDULE VALUES (%d, \'%s\', \'%s\', \'%s\', NULL,\'%s\',NULL);" %(tv_id, full_date, title.replace("'", ''), network, season))
		self.connection.commit()

	def run(self):
		while(True):
			page =  self.otherGet(tvschedule)
			dom    = parseString(page)
			xmlTag = dom.getElementsByTagName('DAY')
			self.clearTable()
			
			for i in range(7):
				day = xmlTag[i].attributes
				
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
							descrp = None
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
									

							self.insertCurrTV(tv_id, full_date, title, network, episode, season, descrip)
							connection.commit()

			time.sleep(60*60*24)