import psycopg2
import getpass
import sys
import Tkinter

# TODO: Fix any sort of case sensitivity for the database queries

def queryForStuff():
	cur = connection.cursor() # constructs the cursor, try this before evey query
	if query_type != 2: # for the first two options
		if query_type == 1:
			isMovie = False
		else:
			isMovie = True
		try:
			print "executing select upper " + str(E1.get()) + str(isMovie)
			cur.execute("SELECT * from media WHERE title=%s AND type=%s;", (str(E1.get()), str(isMovie)))
			
			count = 0
			for tuple in cur.fetchall():
				count += 1
				print tuple
				Lb1.insert(count, str(tuple))

		except StandardError, e:
			print str(e)
	else:
		try:
			print "executing select lower for genre " + str(E1.get()) 
			sql = "SELECT * from genre WHERE title LIKE \'%"+E1.get()+"%\';"
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
				Lb1.insert(count, str(tuple))

		except StandardError, e:
			print str(e)


	Lb1.pack(fill=Tkinter.BOTH, expand=1)
	cur.close()

def sel():
	print "var: " + str(var.get())
	global query_type
	if var.get() == 1:		
		query_type = 0 # if it is a Movie
	elif var.get() == 2:
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

top = Tkinter.Tk() # root tkinter thingy
top.maxsize(700,700)
top.minsize(700,700)

######Global Vars#######
query_type = 0
var = Tkinter.IntVar()
var.set(1)
########################

entryFrame = Tkinter.Frame(top)
resultFrame = Tkinter.Frame(top)

E1 = Tkinter.Entry(entryFrame, bd =5)
L1 = Tkinter.Label(entryFrame, text="Title")
Lb1 = Tkinter.Listbox(resultFrame, height =35, width = 80)

E1.pack(side = Tkinter.RIGHT)
L1.pack( side = Tkinter.RIGHT)
B = Tkinter.Button(entryFrame, text ="Query!", command = queryForStuff)


R1 = Tkinter.Radiobutton(entryFrame, text="Movie Title", variable=var, value=1, command=sel)
R1.pack(anchor = Tkinter.W)

R2 = Tkinter.Radiobutton(entryFrame, text="TV Show Title", variable=var, value=2, command=sel)
R2.pack(anchor = Tkinter.W)

R3 = Tkinter.Radiobutton(entryFrame, text="Genre for Movies", variable=var, value=3, command=sel)
R3.pack(anchor = Tkinter.W)
B.pack(anchor = Tkinter.S)
entryFrame.pack(anchor = Tkinter.CENTER)
resultFrame.pack()
# main()
top.mainloop()