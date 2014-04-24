

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



class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
    	if(tag=="div" and len(attrs)==2):
    		if('left padding_bottom_10' in attrs[0] and 'vertical-align: top;'in attrs[1]):
	    		print attrs
	    		print "Encountered a start tag:", tag


RagePage   = urllib2.urlopen('http://www.tvrage.com/The_Bold_and_the_Beautiful/episodes/1065539857').read()
# print(RagePage)
print()
print("------------------------------------------------------------------------------------------------")

# lines = RagePage.split("<div class=\"left padding_bottom_10\" style=\"vertical-align: top;\">")
# print(len(lines))
# print('<div class=\"left padding_bottom_10\" style=\"vertical-align: top;\">')
parser = DescripFind()
parser.feed(RagePage)
print(parser.data[0])
