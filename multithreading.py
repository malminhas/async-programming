#!/usr/bin/python

# Notes:
# -------
# 1) Thread:
# 
# 2) Termination:
# There is no easy way to kill long-running threads in Python.
# The pattern used below involves a StoppableThread which uses a threading.Event.
# See: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread

import threading
import datetime
import time
import random
import queue
import sys
import signal

thread_pool = []

def getTimestamp():
	now = datetime.datetime.now()
	dt = now.strftime("%d-%m-%Y %H:%M:%S.%f")
	return dt

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Producer(StoppableThread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
		super(Producer,self).__init__()
		self.target = target
		self.name = name
		self.q = args[0]
		self.n = 0
		
	def generateEvent(self):
		lower = self.n - 10
		upper = self.n + 10
		if lower < 0:
			lower = 0
		if upper > 255:
			upper = 255
		self.n = random.randint(lower,upper)
		event = f"event:{self.n}"
		return event

	def run(self):
		self.threadid = threading.get_ident()
		while True:
			if not self.q.full():
				msg = self.generateEvent()
				self.q.put(msg)
				tstamp = getTimestamp()
				print(f"{tstamp}: Producer(tid={self.threadid}) produced =>\t'{msg}'")
				interval = 0.1
				time.sleep(interval)
				if self.stopped():
					print(f"Stopping '{self.name}' thread")
					return
		return

class Consumer(StoppableThread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
		super(Consumer,self).__init__()
		self.target = target
		self.name = name
		self.q = args[0]

	def run(self):
		self.threadid = threading.get_ident()
		while True:
			if not self.q.empty():
				item = self.q.get()
				tstamp = getTimestamp()
				print(f"{tstamp}: Consumer(tid={self.threadid}) consumed =>\t'{item}'")
				#time.sleep(0.01)
				if item == 'END':
					return
			if self.stopped():
				print(f"Stopping '{self.name}' thread")
				return
		return

def signal_handler(signal, frame):
	print(f"---- Ctrl+C picked up in main thread.  Shutting down ----")
	for t in thread_pool:
		print(f"---- Stopping thread '{t.name}' with threadid={t.threadid} ----")
		t.stop()
	sys.exit(0)


if __name__ == '__main__':
	tid = threading.get_ident()
	signal.signal(signal.SIGINT, signal_handler)
	
	print(f"---- Main thread tid={tid} ----")
	print(f"---- Creating event queue,producer and consumer ----")
	eventQ = queue.Queue(100)
	p = Producer(name='producer', args=(eventQ,))
	thread_pool.append(p)
	c = Consumer(name='consumer', args=(eventQ,))
	c.daemon = True	# Must have this here or otherwise consumer doesn't die
	thread_pool.append(c)
	
	print(f"---- Starting producer and consumer processes ----")
	for each in thread_pool:
		each.start()

	# We end up blocking here if we enable this
	#for each in thread_pool:
	#	each.join()
		
	print(f"---- Holding loop in main thread ----")
	while True:
		time.sleep(0.1)

	print(f"---- Exiting! ----")