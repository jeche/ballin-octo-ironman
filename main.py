import io
import psycopg2
import getpass
import sys
import Tkinter
import urllib2
import base64
import Image
from PIL import Image, ImageTk
from collections import deque

class item_container:
	def __init__(self, item, parent, isActor):
		self.parent = parent
		self.isActor = isActor
		self.id = item

	def __eq__(self, other):
		return self.id == other.id and self.isActor == other.isActor



base_url = "http://image.tmdb.org/t/p/w185"

# TODO: Fix any sort of case sensitivity for the database queries
# TODO: Fix any images with broken links crashing, catch and present a default movie poster

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

def queryWorkerFromMediaId(media_id, media_type):
	"""media_name is a case sensitive title for the media, media_type is a boolean
	denoting if it is a movie or not, True is for if it is a movie, False if it is a TV show"""
	cur = connection.cursor()
	list_of_workers = []
	try:
		cur.execute("SELECT * from media, jobs WHERE media.ID=%s AND media.type=%s AND jobs.media_id=media.ID AND jobs.type=True", [media_id, media_type])

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

def queryForWorkerInfoOnId(worker_id):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from workers WHERE W_ID=%s ", [worker_id])

		for tuple in cur.fetchone():
			print tuple
			list_of_movies.append(tuple)
	except StandardError, e:
		print str(e)
	cur.close()
	return list_of_movies

# returns a list of movie tuples for a given actor or worker
def queryMediaFromWorker(worker_name, isMovie):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, jobs, workers WHERE workers.Name=%s AND jobs.media_id=media.ID AND workers.W_ID=jobs.W_ID AND media.type=%s", [worker_name, isMovie])

		# count = 0
		for tuple in cur.fetchall():
			# count += 1
			print tuple
			list_of_movies.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
	# result_listbox.pack()
	cur.close()
	return list_of_movies

# returns a list of movie tuples for a given actor or worker
def queryMediaFromWorkerId(worker_name, isM):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, jobs WHERE jobs.media_id=media.ID AND jobs.W_ID=%s AND media.type=%s AND jobs.type=True", [worker_name, isM])

		# count = 0
		for tuple in cur.fetchall():
			# count += 1
			print tuple
			list_of_movies.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
	# result_listbox.pack()
	cur.close()
	return list_of_movies

# returns a list of movies with the specified rating
def findMovieBasedOnCRating(rating):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, movies WHERE movies.media_id=media.ID AND movies.CRATING=%s", [str(rating)])

		for tuple in cur.fetchall():
			# count += 1
			print tuple
			list_of_movies.append(tuple)
			# result_listbox.insert(count, str(tuple))
	except StandardError, e:
		print str(e)
		# result_listbox.pack()
	cur.close()
	return list_of_movies

# returns list of actors and movies to click on in order to reach the movie with a 100% rating
def findPathTo100Percent(movie_name):
	final = []
	temp_answer = findMovieBasedOnCRating(100)
	answer = []
	for item in temp_answer:
		answer.append(item_container(item[0], None, False))
	q = deque()
	found = []
	# appends media id, and isActor (either is a movie or an actor)
	isActor = False
	init_id = queryForAllInfo(movie_name,True)[0]
	cur_item = item_container(init_id, None, isActor)
	init_item = cur_item
	q.append(cur_item)
	while len(q) != 0:
		cur_item = q.popleft()
		found.append(cur_item)
		isActor = cur_item.isActor
		if cur_item in answer:
			while cur_item.parent != None:
				final.append(cur_item)
				print(cur_item.id)
				cur_item = cur_item.parent
				
			final.append(init_item)
			final.reverse()
			return final
		elif isActor:
			result = queryMediaFromWorkerId(cur_item.id, True)
		else:
			result = queryWorkerFromMediaId(cur_item.id, True)


		for item in result:
			print item
			if isActor:
				item = item[0]
			else:
				item = item[6]
			new_tup = item_container(item, cur_item, not isActor)
			if new_tup not in found:
				q.append(new_tup)
	return final

def queryForAllInfo(movie_name, isM):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		print "executing all"

		if isM:
			cur.execute("SELECT * from media, movies WHERE title=%s AND type=True AND media.ID=movies.media_id;", [movie_name])
		else:
			cur.execute("SELECT * from media, tv WHERE title=%s AND type=False AND media.ID=tv.media_id;", [movie_name])
		
		for item in cur.fetchone():
			title_list.append(item)
			print item

	except StandardError, e:
		print str(e)
	cur.close()

	print title_list
	return title_list

def queryForAllInfoOnId(media_id, isM):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		print "executing all"

		if isM:
			cur.execute("SELECT * from media, movies WHERE media.ID=%s AND type=True AND media.ID=movies.media_id;", [media_id])
		else:
			cur.execute("SELECT * from media, tv WHERE media.ID=%s=%s AND type=False AND media.ID=tv.media_id;", [media_id])
		
		for item in cur.fetchone():
			title_list.append(item)
			print item

	except StandardError, e:
		print str(e)
	cur.close()

	print title_list
	return title_list

# returns a list of media tuples with the appropriate title
def queryFromMediaTitle(media_title, isMovie):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		cur.execute("SELECT * from media WHERE title=%s AND type=%s;", [media_title, str(isMovie)])
		
		for tuple in cur.fetchall():
			title_list.append(tuple[2])
			print tuple

	except StandardError, e:
		print str(e)
	cur.close()
	return title_list

def queryFromGenreTitle(genre_title):
	cur = connection.cursor()
	media_list = []
	try:
		sql = "SELECT * from genre WHERE title ILIKE \'%"+genre_title+"%\';"
		cur.execute(sql)
		print sql

		genre = cur.fetchone()
		print genre[0]

		sql2 = "SELECT * FROM media where id in (SELECT media_id from genre_mtv WHERE g_id="+str(genre[0])+");"
		print sql2
		cur.execute(sql2)
		for tuple in cur.fetchall():
			media_list.append(tuple[2])
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
		# result = findPathTo100Percent("Primeval")
		result = findPathTo100Percent(entry_field.get())
		for item in result:
			if item.isActor:
				item = queryForWorkerInfoOnId(item.id)
			else:
				item = queryForAllInfoOnId(item.id, True)
			result_listbox.insert(Tkinter.END, str(item))

		result_listbox.pack(fill=Tkinter.BOTH, expand=1)
		return
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
		# image_byt = urllib2.urlopen(base_url+item[4]).read()
		# image_b64 = base64.encodestring(image_byt)
		# photo = Tkinter.PhotoImage(image_b64)
		# cv = Tkinter.Canvas(bg='white')
		# cv.pack(side='top', fill='both', expand='yes')
		# put the image on the canvas with
		# create_image(xpos, ypos, image, anchor)
		# cv.create_image(10, 10, image=photo, anchor='nw')
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
		query_type = 3 # if it is a rating for a movie
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

# on selection of item in listbox attempt to display a picture.  is still really buggy.
def on_select(event):
	global image_byt
	global data_stream
	global pil_image
	global w
	global h
	global isMovie
	
	movieTitle = result_listbox.get(Tkinter.ACTIVE)#[2].strip().strip("'").strip(')').strip("'")
	movieInfo = queryForAllInfo(movieTitle, isMovie)

	try:
		image_byt = urllib2.urlopen(base_url+movieInfo[4].strip().strip("'").strip(')').strip("'")).read()
	except StandardError, e:
		image_byt = urllib2.urlopen("http://i60.tinypic.com/15o6j61.png").read()

	data_stream = io.BytesIO(image_byt)
	pil_image = Image.open(data_stream)
	w, h = pil_image.size
	photo = ImageTk.PhotoImage(pil_image)
	image_container.configure(image = photo, justify = Tkinter.LEFT)
	image_container.image = photo
	image_container.pack(anchor = Tkinter.W)

	if isMovie:
		release_Date_text.set("Release_Date: "+ movieInfo[8].isoformat())
		MPAA_RATING_text.set("MPAA Rating:  "+ str(movieInfo[12]))
		IMDB_Rating_text.set("IMDB Rating:                            " + ("N/A" if  movieInfo[11] < 0 else str(movieInfo[11])))
		C_RATING_text.set("Rotten Tomatoes' Critic Rating: "+ ("N/A" if  movieInfo[9] < 0 else str(movieInfo[9])))
		U_RATING_text.set("Rotten Tomatoes' User Rating:  "+  ("N/A" if movieInfo[10] < 0 else str(movieInfo[10])))
	else:
		#fill this in... will do (brittany)
		pass
	

	release_Date.place(x = 200, y = 120)
	MPAA_RATING.place(x = 200, y = 140)
	C_RATING.place(x = 400, y = 120)
	U_RATING.place(x = 400, y = 140)
	IMDB_Rating.place(x = 400, y = 160)
	

# Initialize main GUI elements
top = Tkinter.Tk() # root tkinter thingy

######Global Vars#######
isMovie = True
query_type = 0
rb_choice = Tkinter.IntVar()
rb_choice.set(1)
release_Date_text = Tkinter.StringVar()
MPAA_RATING_text = Tkinter.StringVar()
C_RATING_text = Tkinter.StringVar()
U_RATING_text = Tkinter.StringVar()
IMDB_Rating_text = Tkinter.StringVar()
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

entryFrame = Tkinter.Frame(top, bd = 4)
resultFrame = Tkinter.Frame(top)

result_listbox = Tkinter.Listbox(resultFrame, height =25, width = 80, bg = "white")
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

release_Date = Tkinter.Label(top, textvariable=release_Date_text)
MPAA_RATING = Tkinter.Label(top, textvariable=MPAA_RATING_text)
C_RATING = Tkinter.Label(top, textvariable=C_RATING_text)
U_RATING = Tkinter.Label(top, textvariable=U_RATING_text)
IMDB_Rating= Tkinter.Label(top, textvariable=IMDB_Rating_text)

# Making GUI items visible
entry_field.pack(side = Tkinter.RIGHT)
entry_label.pack( side = Tkinter.RIGHT)

rb_movie.pack(anchor = Tkinter.W)
rb_tvshow.pack(anchor = Tkinter.W)
rb_movie_genre.pack(anchor = Tkinter.W)
rb_path_to_hundred.pack(anchor = Tkinter.W)

query_button.pack(anchor = Tkinter.S)

entryFrame.pack(anchor = Tkinter.CENTER)

image_container.pack()#anchor = Tkinter.W, fill='both')#expand='yes')#, side='top', , )

resultFrame.pack(anchor = Tkinter.S)
# main()
top.mainloop()
