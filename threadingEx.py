import threading


def print_a():
	while(True):
		print("A")

def print_b():
	while(True):
		print("B")

class Meep:
	def __init__(self):
		self.num = 1
	def job(self):
		while(True):
			self.num+=1
			print self.num, 



boop = Meep()
t1 = threading.Thread(target=boop.job)
t2 = threading.Thread(target=boop.job)


t1.start()
t2.start()

