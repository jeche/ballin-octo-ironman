import io
import psycopg2
import getpass
import sys
import Tkinter
import urllib2
import base64
from PIL import Image, ImageTk
from collections import deque

base_url = "http://image.tmdb.org/t/p/w185"

# TODO: Fix any sort of case sensitivity for the database queries

# returns a list of worker tuples in a given movie or TV show
def queryWorkerFromMedia(media_name, media_type):
	"""media_name is a case sensitive title for the media, media_type is a boolean
	denoting if it is a movie or not, True is for if it is a movie, False if it is a TV show"""
	cur = connection.cursor()
	list_of_workers = []
	try:
		cur.execute("SELECT * from media, jobs, workers WHERE title=%s AND media.type=%s AND jobs.media_id=media.ID AND workers.W_ID=jobs.W_ID", [media_name, media_type])

		# count = 0
		for tuple in cur.fetchall():
			# count += 1
			print tuple
			list_of_workers.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
	# result_listbox.pack()
	cur.close()
	return list_of_workers

# returns a list of movie tuples for a given actor or worker
def queryMediaFromWorker(worker_name):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, jobs, workers WHERE workers.Name=%s AND jobs.media_id=media.ID AND workers.W_ID=jobs.W_ID", [worker_name])

		# count = 0
		for tuples in cur.fetchall():
			# count += 1
			print tuple
			list_of_movies.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
	# result_listbox.pack()
	cur.close()
	return list_of_movies

def findMovieBasedOnCRating(rating):
	cur = connection.cursor()
	try:
		cur.execute("SELECT * from media, movie, workers WHERE movie.media_id=media.ID AND movie.CRATING=%s", [str(rating)])

		for tuples in cur.fetchall():
			# count += 1
			print tuple
			list_of_movies.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
		# result_listbox.pack()
	cur.close()
def findPathTo100Percent(movie_name):
	q = deque(queryFromMediaTitle)

	while len(q) != 0:
		pass


def queryForAllMovieInfo(movie_name):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		print "executing select upper " + str(entry_field.get()) + str(isMovie)
		cur.execute("SELECT * from media, movies WHERE title=%s AND type=True AND media.ID=movies.media_id;", [media_title])
		
		for tuple in cur.fetchall():
			title_list.append(tuple)
			print tuple

	except StandardError, e:
		print str(e)
	cur.close()
	return title_list

# returns a list of media tuples with the appropriate title
def queryFromMediaTitle(media_title, isMovie):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		print "executing select upper " + str(entry_field.get()) + str(isMovie)
		cur.execute("SELECT * from media WHERE title=%s AND type=%s;", [media_title, str(isMovie)])
		
		for tuple in cur.fetchall():
			title_list.append(tuple)
			print tuple

	except StandardError, e:
		print str(e)
	cur.close()
	return title_list

def queryFromGenreTitle(genre_title):
	cur = connection.cursor()
	media_list = []
	try:
		print "executing select upper " + str(genre_title) + str(isMovie)
		sql = "SELECT * from genre WHERE title ILIKE \'%"+genre_title+"%\';"
		cur.execute(sql)
		print sql

		genre = cur.fetchone()
		print genre[0]

		sql2 = "SELECT * FROM media where id in (SELECT media_id from genre_mtv WHERE g_id="+str(genre[0])+");"
		print sql2
		cur.execute(sql2)
		for tuple in cur.fetchall():
			media_list.append(tuple)
			print tuple
	except StandardError, e:
		print str(e)
	cur.close()
	return media_list

# Does the query based on what you picked
def queryDatabase():
	result_listbox.delete(0, Tkinter.END)
	# cur = connection.cursor() # constructs the cursor, try this before evey query
	if query_type == 3:
		result = findPathTo100Percent("Primeval")
	elif query_type != 2: # for the first two options
		if query_type == 1:
			isMovie = False
		else:
			isMovie = True

		result = queryFromMediaTitle(entry_field.get(), isMovie)
		# count = 0
		# for tuple in cur.fetchall():
		# 	count += 1
		# 	print tuple
		# 	result_listbox.insert(count, str(tuple))

	else:
		result = queryFromGenreTitle(entry_field.get())
		# try:
		# 	print "executing select lower for genre " + str(entry_field.get()) 
		# 	sql = "SELECT * from genre WHERE title LIKE \'%"+entry_field.get()+"%\';"
		# 	print sql
		# 	cur.execute(sql)

		# 	genre = cur.fetchone()
		# 	print genre[0]

		# 	sql2 = "SELECT * FROM media where id in (SELECT media_id from genre_mtv WHERE g_id="+str(genre[0])+");"
		# 	print sql2
		# 	cur.execute(sql2)
			
		# 	count = 0
		# 	for tuple in cur.fetchall():
		# 		count += 1
		# 		print tuple
		# 		result_listbox.insert(count, str(tuple))

		# except StandardError, e:
		# 	print str(e)

	# u = urllib2.urlopen(URL)
	# raw_data = u.read()
	# u.close()
	for item in result:
		image_byt = urllib2.urlopen(base_url+item[4]).read()
		image_b64 = base64.encodestring(image_byt)
		photo = Tkinter.PhotoImage(image_b64)
		cv = Tkinter.Canvas(bg='white')
		cv.pack(side='top', fill='both', expand='yes')
		# put the image on the canvas with
		# create_image(xpos, ypos, image, anchor)
		cv.create_image(10, 10, image=photo, anchor='nw')
		result_listbox.insert(Tkinter.END, str(item))

	result_listbox.pack(fill=Tkinter.BOTH, expand=1)
	# cur.close()
	
# Deals with the RadioButton based on the selection
def radioSelection():
	print "rb_choice: " + str(rb_choice.get())
	global query_type
	global isMovie
	if rb_choice.get() == 1:		
		query_type = 0 # if it is a Movie
		isMovie = True
	elif rb_choice.get() == 2:
		query_type = 1 # if it is a TV Show
		isMovie = False
	elif rb_choice.get() == 4:
		query_type = 3
	else:
		query_type = 2 # if it is a Genre

	print  "query_type: " + str(query_type)


try:
	# makes connection
	connection = psycopg2.connect( database = "OnlyMovies", user = "jaleo", password = "jaleo")
	print "SUCCESS: connection made"
except StandardError, e:
	print str(e)
	exit

def on_select(event):
	global image_byt
	global data_stream
	global pil_image
	global w
	global h
	rez_list = result_listbox.get(Tkinter.ACTIVE).split(",")
	image_byt = urllib2.urlopen(base_url+rez_list[4].strip().strip("'").strip(')').strip("'")).read()
	data_stream = io.BytesIO(image_byt)
	pil_image = Image.open(data_stream)
	w, h = pil_image.size
	photo = ImageTk.PhotoImage(pil_image)
	image_container.configure(image = photo)
	image_container.image = photo
	image_container.pack()
	


# Initialize main GUI elements
top = Tkinter.Tk() # root tkinter thingy

######Global Vars#######
query_type = 0
rb_choice = Tkinter.IntVar()
rb_choice.set(1)
########################

# code to display an image
image_byt = urllib2.urlopen(base_url+"/p6p4mYAGJMfvPYc3JSsS7RHFA81.jpg").read()
data_stream = io.BytesIO(image_byt)
pil_image = Image.open(data_stream)
w, h = pil_image.size

image_b64 = base64.encodestring(image_byt)
photo = Tkinter.PhotoImage(image_b64)
photo = ImageTk.PhotoImage(pil_image)


top.maxsize(700,700)
top.minsize(700,700)

entryFrame = Tkinter.Frame(top)
resultFrame = Tkinter.Frame(top)

result_listbox = Tkinter.Listbox(resultFrame, height =35, width = 80)
result_listbox.bind('<<ListboxSelect>>', on_select)

entry_field = Tkinter.Entry(entryFrame, bd =5)
entry_label = Tkinter.Label(entryFrame, text="Title")

query_button = Tkinter.Button(entryFrame, text ="Query!", command = queryDatabase)

# rb stands for RadioButton
rb_movie = Tkinter.Radiobutton(entryFrame, text="Movie Title", variable=rb_choice, value=1, command=radioSelection)
rb_tvshow = Tkinter.Radiobutton(entryFrame, text="TV Show Title", variable=rb_choice, value=2, command=radioSelection)
rb_movie_genre = Tkinter.Radiobutton(entryFrame, text="Genre for Movies", variable=rb_choice, value=3, command=radioSelection)
rb_path_to_hundred = Tkinter.Radiobutton(entryFrame, text="Path to 100", variable=rb_choice, value=4, command=radioSelection)
image_container = Tkinter.Label(top, image=photo)


# Making GUI items visible
entry_field.pack(side = Tkinter.RIGHT)
entry_label.pack( side = Tkinter.RIGHT)

rb_movie.pack(anchor = Tkinter.W)
rb_tvshow.pack(anchor = Tkinter.W)
rb_movie_genre.pack(anchor = Tkinter.W)

query_button.pack(anchor = Tkinter.S)

entryFrame.pack(anchor = Tkinter.CENTER)

image_container.pack(side='top', fill='both', expand='yes')
resultFrame.pack()
# main()
top.mainloop()
