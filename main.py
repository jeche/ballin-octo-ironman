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
from updateMovieOpenings import UpdateNowPlaying
from updateTV import UpdateTv


class SimpleTable(Tkinter.Frame):
    def __init__(self, parent, rows=10, columns=2):
        # use black background so it "peeks through" to 
        # form grid lines
        Tkinter.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Tkinter.Label(self, text="%s/%s" % (row, column), 
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

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

		for tuple in cur.fetchall():
			list_of_workers.append(tuple)

	except StandardError, e:
		print str(e)

	cur.close()
	return list_of_workers

def queryWorkerFromMediaId(media_id, media_type):
	"""media_name is a case sensitive title for the media, media_type is a boolean
	denoting if it is a movie or not, True is for if it is a movie, False if it is a TV show"""
	cur = connection.cursor()
	list_of_workers = []
	try:
		cur.execute("SELECT * from media, jobs WHERE media.ID=%s AND media.type=%s AND jobs.media_id=media.ID AND jobs.type=True", [media_id, media_type])

		for tuple in cur.fetchall():

			list_of_workers.append(tuple)

	except StandardError, e:
		print str(e)

	cur.close()
	return list_of_workers

def queryForWorkerInfoOnId(worker_id):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from workers WHERE W_ID=%s ", [worker_id])

		for tuple in cur.fetchone():
			list_of_movies.append(tuple)

	except StandardError, e:
		print str(e)
	cur.close()
	return list_of_movies

# returns a list of movie tuples for a given actor or worker
def queryMediaFromWorkerForRB(worker_name, isMovie):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT DISTINCT media.title from media, jobs, workers WHERE workers.Name=%s AND jobs.media_id=media.ID AND workers.W_ID=jobs.W_ID AND media.type=%s", [worker_name, isMovie])

		for tuple in cur.fetchall():
			list_of_movies.append(tuple[0])

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

		for tuple in cur.fetchall():
			list_of_movies.append(tuple)

	except StandardError, e:
		print str(e)

	cur.close()
	return list_of_movies

# returns a list of movie tuples for a given actor or worker
def queryMediaFromWorkerId(worker_name, isM):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, jobs WHERE jobs.media_id=media.ID AND jobs.W_ID=%s AND media.type=%s AND jobs.type=True", [worker_name, isM])

		for tuple in cur.fetchall():
			list_of_movies.append(tuple)

	except StandardError, e:
		print str(e)

	cur.close()
	return list_of_movies

# returns a list of movies with the specified rating
def findMovieBasedOnCRating(rating):
	cur = connection.cursor()
	list_of_movies = []
	try:
		cur.execute("SELECT * from media, movies WHERE movies.media_id=media.ID AND movies.CRATING=%s", [str(rating)])

		for tuple in cur.fetchall():
			list_of_movies.append(tuple)

	except StandardError, e:
		print str(e)

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
	
	try:
		init_id = queryForAllInfo(movie_name,True)[0]
	except StandardError, e:
		print "Film not found"
		return -1

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
				cur_item = cur_item.parent
				
			final.append(init_item)
			final.reverse()
			return final
		elif isActor:
			result = queryMediaFromWorkerId(cur_item.id, True)
		else:
			result = queryWorkerFromMediaId(cur_item.id, True)


		for item in result:
			if isActor:
				item = item[0]
			else:
				item = item[6]
			new_tup = item_container(item, cur_item, not isActor)
			if new_tup not in found:
				q.append(new_tup)
	return final

def queryForNowPlayingInfo(movie_name):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		cur.execute("SELECT * from media, movies, now_playing WHERE title=%s AND type=True AND media.ID=movies.media_id AND movies.movie_id = now_playing.m_id;", [movie_name])
		
		for item in cur.fetchone():
			title_list.append(item)

	except StandardError, e:
		print str(e)
	cur.close()

	return title_list

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

	except StandardError, e:
		print str(e)
	cur.close()

	return title_list

def queryForAllInfoOnId(media_id, isM):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:

		if isM:
			cur.execute("SELECT * from media, movies WHERE media.ID=%s AND type=True AND media.ID=movies.media_id;", [media_id])
		else:
			cur.execute("SELECT * from media, tv WHERE media.ID=%s=%s AND type=False AND media.ID=tv.media_id;", [media_id])
		
		for item in cur.fetchone():
			title_list.append(item)

	except StandardError, e:
		print str(e)
	cur.close()

	return title_list

# returns a list of media tuples with the appropriate title
def queryFromMediaTitle(media_title, isMovie):
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		cur.execute("SELECT * from media WHERE title=%s AND type=%s;", [media_title, str(isMovie)])
		for tuple in cur.fetchall():
			title_list.append(tuple[2])

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

		genre = cur.fetchone()
		print genre[0]

		sql2 = "SELECT * FROM media where id in (SELECT media_id from genre_mtv WHERE g_id="+str(genre[0])+");"
		cur.execute(sql2)
		for tuple in cur.fetchall():
			media_list.append(tuple[2])
			print tuple
	except StandardError, e:
		print str(e)
	cur.close()
	return media_list

def queryTop100Critics():
	global NowPlayingVar
	global top100
	top100 = True

	NowPlayingVar = False#global to manipulate onSelect
	result_listbox.delete(0, Tkinter.END)
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		cur.execute("SELECT * from media,movies WHERE type=True AND movies.crating > 0 AND media.ID=movies.media_id ORDER BY movies.CRATING DESC Limit 100;")
		
		for tuple in cur.fetchall():
			title_list.append(tuple[2])

	except StandardError, e:
		print str(e)
	cur.close()

	for item in title_list:
		result_listbox.insert(Tkinter.END, str(item))
	result_listbox.pack(fill=Tkinter.BOTH, expand=1)

def queryTop100Users():
	global NowPlayingVar
	global top100
	top100 = True

	NowPlayingVar = False#global to manipulate onSelect
	result_listbox.delete(0, Tkinter.END)
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	try:
		cur.execute("SELECT * from media,movies WHERE type=True AND movies.urating > 0 AND media.ID=movies.media_id ORDER BY movies.URATING DESC Limit 100;")
		
		for tuple in cur.fetchall():
			title_list.append(tuple[2])

	except StandardError, e:
		print str(e)
	cur.close()
	
	for item in title_list:
		result_listbox.insert(Tkinter.END, str(item))
	result_listbox.pack(fill=Tkinter.BOTH, expand=1)

# Does the query based on what you picked
def queryDatabase():
	result_listbox.delete(0, Tkinter.END)
	print query_type
	top100 = False
	# cur = connection.cursor() # constructs the cursor, try this before evey query
	if query_type == 3:
		# result = findPathTo100Percent("Primeval")
		result = findPathTo100Percent(entry_field.get())
		
		#error checking
		if result == -1:
			return -1

		for item in result:
			if item.isActor:
				item = "     --->"+ str(queryForWorkerInfoOnId(item.id)[1])
			else:
				item = queryForAllInfoOnId(item.id, True)[2]
			result_listbox.insert(Tkinter.END, str(item))

		result_listbox.pack(fill=Tkinter.BOTH, expand=1)
		return

	elif query_type == 4: 
		#workers
		result1 = queryMediaFromWorkerForRB(entry_field.get(), True)
		result2 = queryMediaFromWorkerForRB(entry_field.get(), False)

		result = []

		for item in result1:
			result.append("Movie: "+item)

		for item in result2:
			result.append("TV Show: "+item)

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
	global NowPlayingVar

	NowPlayingVar = False#global to manipulate onSelect

	if rb_choice.get() == 1:		
		query_type = 0 # if it is a Movie
		isMovie = True
	elif rb_choice.get() == 2:
		query_type = 1 # if it is a TV Show
		isMovie = False
	elif rb_choice.get() == 4:
		query_type = 3 # if it is a rating for a movie
	elif rb_choice.get() == 5:
		query_type = 4 # Worker
	else:
		query_type = 2 # if it is a Genre
		isMovie = True

	print  "query_type: " + str(query_type)


try:
	# makes connection
	connection = psycopg2.connect( database = "OnlyMovies", user = "jaleo", password = "jaleo")
	print "SUCCESS: connection made"
except StandardError, e:
	print str(e)
	exit

def listoftimes():
	time_list = []
	sql_time = "SELECT DISTINCT time FROM current_tv_schedule ORDER BY time;"
	cur = connection.cursor() # constructs the cursor, try this before evey query
	try:
		print( "weee")
		cur.execute(sql)
		
		for tuple in cur.fetchall():
			if tuple[3] not in resultDict:
				resultDict[tuple[3]] = []
			resultDict[tuple[3]].append(tuple)
			print(tuple)
			title_list.append(tuple[2])

	except StandardError, e:
		print str(e)
	return time_list

def pickTime():
	global isProvider
	isProvider = False
	sched_pick_listbox.delete(0, Tkinter.END)
	sched_result_listbox.delete(0, Tkinter.END)
	# time_list = listoftimes()
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	sql = "SELECT DISTINCT time from current_tv_schedule ORDER BY time;"
	
	try:
		cur.execute(sql)
		for tuple in cur.fetchall():
			sched_pick_listbox.insert(Tkinter.END, tuple[0])
			# if tuple[3] not in resultDict:
			# 	resultDict[tuple[3]] = []
			# resultDict[tuple[3]].append(tuple)
			# print(tuple)
			# title_list.append(tuple[2])

	except StandardError, e:
		print str(e)
	# sched_result_listbox.pack(fill=Tkinter.BOTH, expand=1)
	# sched_result_listbox.pack(fill=Tkinter.BOTH, expand=1)
	pass

def pickProvider():
	global isProvider
	isProvider = True
	# sched_result_listbox.pack(fill=Tkinter.BOTH, expand=1)
	sched_pick_listbox.delete(0, Tkinter.END)
	sched_result_listbox.delete(0, Tkinter.END)
	# time_list = listoftimes()
	cur = connection.cursor() # constructs the cursor, try this before evey query
	title_list = []
	sql = "SELECT DISTINCT broad_comp from current_tv_schedule ORDER BY broad_comp;"
	
	try:
		cur.execute(sql)
		for tuple in cur.fetchall():
			sched_pick_listbox.insert(Tkinter.END, tuple[0])
			# if tuple[3] not in resultDict:
			# 	resultDict[tuple[3]] = []
			# resultDict[tuple[3]].append(tuple)
			# print(tuple)
			# title_list.append(tuple[2])

	except StandardError, e:
		print str(e)
	# count = 0
	# col = 0
	# row = 0 
	# tv_table = Tkinter.Listbox(tv_frame)
	# for item in resultDict.keys():
	# 	# for show in item:
	# 	tv_table.insert(Tkinter.END, item + str(resultDict[item]))
	# 	col = col + 1
	# 	col = 0
	# 	row = row + 1
	# 	# break
	# tv_table.pack()
	# tv_frame.pack()
	cur.close()

	pass
def on_select_result(event):
	global sched_img_container
	info = sched_result_listbox.get(Tkinter.ACTIVE)
	info_list = info.split("-> ")
	title = info_list[1].strip()
	date = info_list[0].strip() # .strip("(").strip(")").strip()
	cur = connection.cursor()
	if isProvider:
		sql = "SELECT * from media, tv, current_tv_schedule WHERE media.type=False AND media.ID=tv.media_id AND tv.TV_ID=current_tv_schedule.TV_ID AND media.title=%s AND current_tv_schedule.time=%s AND current_tv_schedule.broad_comp=%s"

		cur.execute(sql, [title, date, pick])
	else:
		sql = "SELECT * from media, tv, current_tv_schedule WHERE media.type=False AND media.ID=tv.media_id AND tv.TV_ID=current_tv_schedule.TV_ID AND media.title=%s AND current_tv_schedule.broad_comp=%s AND current_tv_schedule.time=%s"

		cur.execute(sql, [title, date, pick])
	
	fin = cur.fetchone()
	print "title " + title
	print "date " + date
	print "pick " + pick
	title_text.set("Title: " + fin[2])
	try:
		description_text.set("Description: " + str(fin[len(fin)-1]))
	except StandardError, e:
		description_text.set("Description: N/A")

	print fin
	try:
		image_byt = urllib2.urlopen(base_url+fin[4].strip().strip("'").strip(')').strip("'")).read()
	except StandardError, e:
		image_byt = urllib2.urlopen("http://i60.tinypic.com/15o6j61.png").read()

	data_stream = io.BytesIO(image_byt)
	pil_image = Image.open(data_stream)
	w, h = pil_image.size
	photo = ImageTk.PhotoImage(pil_image)
	sched_img_container.configure(image = photo, justify = Tkinter.LEFT)
	sched_img_container.image = photo
	sched_img_container.pack(anchor = Tkinter.W)

	title_label.place(x = 200, y = 180)
	description_label.place(x = 200, y = 220) # was IMDB rating

	cur.close()
	pass

def on_select_pick(event):
	global pick
	sched_result_listbox.delete(0, Tkinter.END)
	pick = sched_pick_listbox.get(Tkinter.ACTIVE)
	list_pick = []
	cur = connection.cursor()
	if isProvider:
		sql = "SELECT * from current_tv_schedule WHERE broad_comp=%s ORDER BY time"
	else:
		sql = "SELECT * from current_tv_schedule WHERE time=%s ORDER BY broad_comp"
	cur.execute(sql, [pick])
	for tuple in cur.fetchall():
		print tuple
		# sched_result_listbox.insert(Tkinter.END, tuple)
		list_pick.append(tuple)
	cur.close()
	cur = connection.cursor()

	if isProvider:
		for item in list_pick:
			sql2 = "SELECT media.title FROM media, tv, current_tv_schedule WHERE media.type=False AND media.ID=tv.media_id AND tv.TV_ID=current_tv_schedule.TV_ID AND tv.TV_ID=%s;" # 
			try:
				cur.execute(sql2, [item[0]])
				out2 =cur.fetchone()
				sched_result_listbox.insert(Tkinter.END,str(item[1])+"-> " + str(out2[0]) )
			except StandardError, e:
				print(str(e))
	else:
		for item in list_pick:
			sql2 = "SELECT media.title FROM media, tv, current_tv_schedule WHERE media.type=False AND media.ID=tv.media_id AND tv.TV_ID=current_tv_schedule.TV_ID AND tv.TV_ID=%s;" # 
			try:
				cur.execute(sql2, [item[0]])
				out2 =cur.fetchone()
				sched_result_listbox.insert(Tkinter.END,str(item[3])+"-> " + str(out2[0]) )
			except StandardError, e:
				print(str(e))

	cur.close()
	pass

def tvSchedule():
	global tv_sched_window
	global sched_result_listbox
	global sched_pick_listbox
	global isProvider
	global title_text
	global sched_img_container
	global title_label
	global description_label
	global description_text
	title_text = Tkinter.StringVar()
	description_text = Tkinter.StringVar()
	resultDict = {}
	tv_sched_window = Tkinter.Toplevel()
	tv_sched_window.title('TV Schedule')
	
	tv_sched_window.maxsize(700,700)
	tv_sched_window.minsize(700,700)

	entryFrame = Tkinter.Frame(tv_sched_window, bd = 4)
	buttonFrame = Tkinter.Frame(tv_sched_window)
	resultFrame = Tkinter.Frame(tv_sched_window)
	sched_pick_listbox = Tkinter.Listbox(resultFrame, height =25, width = 80, bg = "white")
	sched_result_listbox = Tkinter.Listbox(resultFrame, height =25, width = 80, bg = "white")
	sched_result_listbox.bind('<<ListboxSelect>>', on_select_result)
	sched_pick_listbox.bind('<<ListboxSelect>>', on_select_pick)
	

	time_button = Tkinter.Button(buttonFrame, text ="Pick by Time", command = pickTime, background = "slate gray")
	provider_button = Tkinter.Button(buttonFrame, text ="Pick by Provider", command = pickProvider, background = "slate gray")

	# rb stands for RadioButton

	sched_img_container = Tkinter.Label(tv_sched_window, image=photo)


	title_label = Tkinter.Label(tv_sched_window, textvariable=title_text)
	description_label= Tkinter.Label(tv_sched_window, textvariable=description_text, wrap = 470, justify =Tkinter.LEFT)

	# Making GUI items visible

	time_button.pack(side = Tkinter.LEFT)
	provider_button.pack(side = Tkinter.LEFT)

	entryFrame.pack(anchor = Tkinter.CENTER)

	buttonFrame.pack(side = Tkinter.BOTTOM)

	sched_img_container.pack()#anchor = Tkinter.W, fill='both')#expand='yes')#, side='top', , )

	resultFrame.pack(anchor = Tkinter.S)
	
	sched_pick_listbox.pack(side = Tkinter.LEFT, fill=Tkinter.Y, expand=1)
	sched_result_listbox.pack(side = Tkinter.LEFT, fill=Tkinter.Y, expand=1)
	sched_result_listbox.config(width=40)
	sched_pick_listbox.config(width=40)
	# main()
	# otherlabel.pack(side = Tkinter.TOP, fill = Tkinter.BOTH, expand = Tkinter.YES)
	tv_frame = Tkinter.Frame(tv_sched_window)


def nowPlaying():
	global NowPlayingVar

	NowPlayingVar = True#global to manipulate onSelect
	result_listbox.delete(0, Tkinter.END)

	cur = connection.cursor() # constructs the cursor, try this before evey query
	cur2 = connection.cursor() 
	title_list = []
	sql = "SELECT * from now_playing;"
	try:
		cur.execute(sql)
		output1 = cur.fetchall()
		for tuple in output1:
			print tuple[0]
			sql2 = "SELECT media.title FROM movies, media WHERE media.type=True AND media.ID=movies.media_id AND movies.movie_id="+str(tuple[0])+";" # 
			try:
				
				cur2.execute(sql2)
				out2 =cur2.fetchone()[0] 
				if out2 != "": 
					title_list.append(out2)

			except StandardError, e:
				print str(e)	

	except StandardError, e:
		print str(e)
	cur.close()

	for item in title_list:
		result_listbox.insert(Tkinter.END, str(item))
	result_listbox.pack(fill=Tkinter.BOTH, expand=1)

def on_select(event):
	global image_byt
	global data_stream
	global pil_image
	global w
	global h
	global isMovie
	global query_type
	global NowPlayingVar
	global top100

	movieTitle = result_listbox.get(Tkinter.ACTIVE)

	if NowPlayingVar:
		movieInfo = queryForNowPlayingInfo(movieTitle)
		print movieInfo

		release_Date_text.set("Release_Date: "+ movieInfo[14].isoformat())
		MPAA_RATING_text.set("Running Time:  "+ str(movieInfo[15]))
		IMDB_Rating_text.set("Description: " + str(movieInfo[16]))
		C_RATING_text.set("")
		U_RATING_text.set("")

	elif query_type == 4 and not top100:
		movieTitle = movieTitle.split(": ")
		if len(movieTitle) > 2:
			movieTitle = [movieTitle[0], movieTitle[1]+": "+movieTitle[2]]
		print movieTitle

		if movieTitle[0] == "Movie":
			movieInfo = queryForAllInfo(movieTitle[1], True)
			print movieInfo

			release_Date_text.set("Release_Date: "+ movieInfo[8].isoformat())
			MPAA_RATING_text.set("MPAA Rating:  "+ str(movieInfo[12]))
			IMDB_Rating_text.set("IMDB Rating:  " + ("N/A" if  movieInfo[11] < 0 else str(movieInfo[11])))
			C_RATING_text.set("Rotten Tomatoes' Critic Rating: "+ ("N/A" if  movieInfo[9] < 0 else str(movieInfo[9])))
			U_RATING_text.set("Rotten Tomatoes' User Rating:  "+  ("N/A" if movieInfo[10] < 0 else str(movieInfo[10])))
		
		else:
			movieInfo = queryForAllInfo(movieTitle[1], False)
			print movieInfo

			release_Date_text.set("First Air Date:  "+ movieInfo[7].isoformat())
			MPAA_RATING_text.set("Last Air Date:  "+ movieInfo[8].isoformat())
			IMDB_Rating_text.set("")
			C_RATING_text.set("Episodes:    " + str(movieInfo[9]))
			U_RATING_text.set("Seasons:     "+ str(movieInfo[10]))
	elif top100:
		movieInfo = queryForAllInfo(movieTitle, True)
		print movieInfo

		if len(movieInfo) < 2:
			print "No info found TOP 100"
			return 0

		if movieInfo != None:
			release_Date_text.set("Release_Date: "+ movieInfo[8].isoformat())
			MPAA_RATING_text.set("MPAA Rating:  "+ str(movieInfo[12]))
			IMDB_Rating_text.set("IMDB Rating:  " + ("N/A" if  movieInfo[11] < 0 else str(movieInfo[11])))
			C_RATING_text.set("Rotten Tomatoes' Critic Rating: "+ ("N/A" if  movieInfo[9] < 0 else str(movieInfo[9])))
			U_RATING_text.set("Rotten Tomatoes' User Rating:  "+  ("N/A" if movieInfo[10] < 0 else str(movieInfo[10])))

	else:
		movieInfo = queryForAllInfo(movieTitle, isMovie)
		print movieInfo

		if len(movieInfo) < 2:
			print "No info found"
			return 0

		if movieInfo != None:
			if isMovie:
				release_Date_text.set("Release_Date: "+ movieInfo[8].isoformat())
				MPAA_RATING_text.set("MPAA Rating:  "+ str(movieInfo[12]))
				IMDB_Rating_text.set("IMDB Rating:  " + ("N/A" if  movieInfo[11] < 0 else str(movieInfo[11])))
				C_RATING_text.set("Rotten Tomatoes' Critic Rating: "+ ("N/A" if  movieInfo[9] < 0 else str(movieInfo[9])))
				U_RATING_text.set("Rotten Tomatoes' User Rating:  "+  ("N/A" if movieInfo[10] < 0 else str(movieInfo[10])))
			else:
				release_Date_text.set("First Air Date:  "+ movieInfo[7].isoformat())
				if movieInfo[8] != None:
					MPAA_RATING_text.set("Last Air Date:  "+ movieInfo[8].isoformat())
				else:
					MPAA_RATING_text.set("Last Air Date:  N/A")

				IMDB_Rating_text.set("")
				C_RATING_text.set("Episodes:    " + str(movieInfo[9]))
				U_RATING_text.set("Seasons:     "+ str(movieInfo[10]))

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

	release_Date.place(x = 200, y = 180)
	MPAA_RATING.place(x = 200, y = 200)
	IMDB_Rating.place(x = 200, y = 220)
	C_RATING.place(x = 400, y = 180)
	U_RATING.place(x = 400, y = 200)
	
# movieUpdate = UpdateNowPlaying()
# tvUpdate   = UpdateTv()
# t1 = threading.Thread(target=movieUpdate.run)
# t2 = threading.Thread(target=tvUpdate.run)

# t1.start()
# t2.start()
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
NowPlayingVar = False
top100 = False
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
buttonFrame = Tkinter.Frame(top)
resultFrame = Tkinter.Frame(top)

result_listbox = Tkinter.Listbox(resultFrame, height =25, width = 80, bg = "white")
result_listbox.bind('<<ListboxSelect>>', on_select)

entry_field = Tkinter.Entry(entryFrame, bd =5)
entry_label = Tkinter.Label(entryFrame, text="Title")

tvsched_button = Tkinter.Button(buttonFrame, text ="TV Schedule!", command = tvSchedule, background = "slate gray")
nowplay_button = Tkinter.Button(buttonFrame, text ="Now Playing!", command = nowPlaying, background = "slate gray")
cr100_button = Tkinter.Button(buttonFrame, text ="Top 100 by Critic Rating", command = queryTop100Critics, background = "slate gray")
ur100_button = Tkinter.Button(buttonFrame, text ="Top 100 by User Rating", command = queryTop100Users, background = "slate gray")


query_button = Tkinter.Button(entryFrame, text ="Query!", command = queryDatabase, background = "slate gray")

# rb stands for RadioButton
rb_movie = Tkinter.Radiobutton(entryFrame, text="Movie Title", variable=rb_choice, value=1, command=radioSelection)
rb_tvshow = Tkinter.Radiobutton(entryFrame, text="TV Show Title", variable=rb_choice, value=2, command=radioSelection)
rb_movie_genre = Tkinter.Radiobutton(entryFrame, text="Genre for Movies", variable=rb_choice, value=3, command=radioSelection)
rb_path_to_hundred = Tkinter.Radiobutton(entryFrame, text="Path to 100", variable=rb_choice, value=4, command=radioSelection)
rb_workers = Tkinter.Radiobutton(entryFrame, text="Worker/Star", variable=rb_choice, value=5, command=radioSelection)
image_container = Tkinter.Label(top, image=photo)


release_Date = Tkinter.Label(top, textvariable=release_Date_text)
MPAA_RATING = Tkinter.Label(top, textvariable=MPAA_RATING_text)
C_RATING = Tkinter.Label(top, textvariable=C_RATING_text)
U_RATING = Tkinter.Label(top, textvariable=U_RATING_text)
IMDB_Rating= Tkinter.Label(top, textvariable=IMDB_Rating_text, wrap = 470, justify =Tkinter.LEFT)

# Making GUI items visible
entry_field.pack(side = Tkinter.RIGHT)
entry_label.pack( side = Tkinter.RIGHT)

nowplay_button.pack(side = Tkinter.LEFT)
tvsched_button.pack(side = Tkinter.LEFT)
cr100_button.pack(side = Tkinter.LEFT)
ur100_button.pack(side = Tkinter.LEFT)

rb_movie.pack(anchor = Tkinter.W)
rb_tvshow.pack(anchor = Tkinter.W)
rb_workers.pack(anchor = Tkinter.W)
rb_movie_genre.pack(anchor = Tkinter.W)
rb_path_to_hundred.pack(anchor = Tkinter.W)

query_button.pack(anchor = Tkinter.S)

entryFrame.pack(anchor = Tkinter.CENTER)

buttonFrame.pack(side = Tkinter.BOTTOM)

image_container.pack()#anchor = Tkinter.W, fill='both')#expand='yes')#, side='top', , )

resultFrame.pack(anchor = Tkinter.S)
# main()
top.mainloop()
