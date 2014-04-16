import psycopg2
import getpass
import sys
import Tkinter

# TODO: Fix any sort of case sensitivity for the database queries

# Does the query based on what you picked
def queryDatabase():
	cur = connection.cursor() # constructs the cursor, try this before evey query
	if query_type != 2: # for the first two options
		if query_type == 1:
			isMovie = False
		else:
			isMovie = True
		try:
			print "executing select upper " + str(E1.get()) + str(isMovie)
			cur.execute("SELECT * from media WHERE title=%s AND type=%s;", (str(entry_field.get()), str(isMovie)))
			
			count = 0
			for tuple in cur.fetchall():
				count += 1
				print tuple
				result_listbox.insert(count, str(tuple))

		except StandardError, e:
			print str(e)
	else:
		try:
			print "executing select lower for genre " + str(entry_field.get()) 
			sql = "SELECT * from genre WHERE title LIKE \'%"+v.get()+"%\';"
			print sql
			cur.execute(sql)

			genre = cur.fetchone()
			print genre[0]

			sql2 = "SELECT * FROM media where id in (SELECT media_id from genre_mtv WHERE g_id="+str(genre[0])+");"
			print sql2
			cur.execute(sql2)
			
			count = 0
			for tuple in cur.fetchall():
				count += 1
				print tuple
				result_listbox.insert(count, str(tuple))

		except StandardError, e:
			print str(e)


	result_listbox.pack(fill=Tkinter.BOTH, expand=1)
	cur.close()
	
# Deals with the RadioButton based on the selection
def radioSelection():
	print "rb_choice: " + str(rb_choice.get())
	global query_type
	if rb_choice.get() == 1:		
		query_type = 0 # if it is a Movie
	elif rb_choice.get() == 2:
		query_type = 1 # if it is a TV Show
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
	
######Global Vars#######
query_type = 0
rb_choice = Tkinter.IntVar()
rb_choice.set(1)
########################

# Initialize main GUI elements
top = Tkinter.Tk() # root tkinter thingy
top.maxsize(700,700)
top.minsize(700,700)

entryFrame = Tkinter.Frame(top)
resultFrame = Tkinter.Frame(top)

result_listbox = Tkinter.Listbox(resultFrame, height =35, width = 80)

entry_field = Tkinter.Entry(entryFrame, bd =5)
entry_label = Tkinter.Label(entryFrame, text="Title")

query_button = Tkinter.Button(entryFrame, text ="Query!", command = queryDatabase)

# rb stands for RadioButton
rb_movie = Tkinter.Radiobutton(entryFrame, text="Movie Title", variable=rb_choice, value=1, command=radioSelection)
rb_tvshow = Tkinter.Radiobutton(entryFrame, text="TV Show Title", variable=rb_choice, value=2, command=radioSelection)
rb_movie_genre = Tkinter.Radiobutton(entryFrame, text="Genre for Movies", variable=rb_choice, value=3, command=radioSelection)

# Making GUI items visible
entry_field.pack(side = Tkinter.RIGHT)
entry_label.pack( side = Tkinter.RIGHT)

rb_movie.pack(anchor = Tkinter.W)
rb_tvshow.pack(anchor = Tkinter.W)
rb_movie_genre.pack(anchor = Tkinter.W)

query_button.pack(anchor = Tkinter.S)

entryFrame.pack(anchor = Tkinter.CENTER)
resultFrame.pack()
# main()
top.mainloop()
