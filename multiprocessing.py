#!/usr/bin/python

# Notes:
# -------
# 1) Process:
# Python multiprocessing Process class is an abstraction that sets up another Python process, 
# provides it to run code and a way for the parent application to control execution.
# First, we need to write a function, that will be run by the process.  Then, we need to instantiate a Process object.
# If we create a Process object, nothing will happen until we tell it to start processing via start() function. 
# Then, the process will run and return its result. After that we tell the process to complete via join() function.
# Without join() function call, process will remain idle and won't terminate.
# If you want to pass any argument through the process you need to use args keyword argument.
# 2) Queue:
# Python multiprocessing provides a Queue class that is exactly a First-In-First-Out data structure. 
# Queues can store any pickle Python object (though simple ones are best) and are extremely useful 
# for sharing data between processes. Queues are specially useful when passed as a parameter to a Process'
# target function to enable the Process to consume data. By using put() function we can insert data to 
# then queue and using get() we can get items from queues.
# 3) Lock:
# The task of the multiprocessing Lock class is quite simple. It allows code to claim lock so that no other process 
# can execute the similar code until the lock has be released. So the task of Lock class is twofold: a) to claim the lock 
# and b) to release the lock. To claim lock the, acquire() function is used and to release lock release() function is used.
# Note that the python Queue class is already synchronized. That means, we don't need to use the Lock class to block 
# multiple process to access the same queue object. That's why, we don't need to use Lock class below.

import signal
import sys
from multiprocessing import Process,Queue,Lock
from multiprocessing import cpu_count
import random
import datetime
import time 
import os

process_pool = []

def getTimestamp():
	now = datetime.datetime.now()
	dt = now.strftime("%d-%m-%Y %H:%M:%S.%f")
	return dt


'''
def proximity_sensing_func():
	ser = serial.Serial('COM5', 115200, timeout=0,parity=serial.PARITY_EVEN, rtscts=1)
	while True:
		try:
			b = ser.readline(1024)       # read up to 1k bytes
			s = b.decode('utf-8')
			if len(s):
				d = json.loads(s)
				proximity = int(d.get("detail").get("proximity"))
				print(f"{proximity}")
		except Exception as e:
			print(f"Exiting loop: {e}")	
'''

class Producer:
	def __init__(self):
		self.n = 0

	def signal_handler(self, signal, frame):
		print(f"Producer - Ctrl+C picked up. Exit process, pid={self.pid} now")
		sys.exit(0)

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

	def produce_msg(self, consumer_lock, queue):
		signal.signal(signal.SIGINT, self.signal_handler)
		#signal.signal(signal.SIGINT, signal.SIG_IGN) # Doesn't seem to work at least on Windows
		self.pid = os.getpid()
		while True:
			try:
				consumer_lock.acquire()
				msg = self.generateEvent()
				queue.put(msg)
				tstamp = getTimestamp()
				print(f"{tstamp}: Producer(pid={self.pid}) produced =>\t'{msg}'")
				consumer_lock.release()
				interval = 0.1
				time.sleep(interval)
			except Exception as e:
				print(f"Producer exception {e}")
				sys.exit(0)

class Consumer:
	def __init__(self):
		self.msg = None
		
	def signal_handler(self, signal, frame):
		print(f"Consumer - Ctrl+C picked up. Exit process, pid={self.pid} now")
		sys.exit(0)

	def consume_msg(self, producer_lock, queue):
		signal.signal(signal.SIGINT, self.signal_handler)
		#signal.signal(signal.SIGINT, signal.SIG_IGN) # Doesn't seem to work at least on Windows
		self.pid = os.getpid()	
		while True:
			try:
				producer_lock.acquire()
				#if queue.qsize() != 0:
				if queue.empty():
					self.msg = None
					#print('Queue empty')
				else:
					self.msg = queue.get()
					tstamp = getTimestamp()
					print(f"{tstamp}: Consumer(pid={self.pid}) consumed =>\t'{self.msg}'")
				producer_lock.release()
				#time.sleep(random.randrange(1,5))
			except Exception as e:
				print(f"Consumer exception {e}")
				sys.exit(0)

if __name__ == "__main__":
	pid = os.getpid()
	print(f"---- Main thread pid={pid} ----")
	ncores = cpu_count()
	nproc = 2
	print(f"---- Creating {nproc} processes with {ncores} CPUs ----")
	
	print(f"---- Creating producer_lock,consumer_lock,event queue,producer and consumer ----")
	producer_lock = Lock()
	consumer_lock = Lock()
	eventQ = Queue()	
	producer = Producer() 
	consumer = Consumer()
	p = Process(target=producer.produce_msg, args=(consumer_lock, eventQ,))
	process_pool.append(p)
	p = Process(target=consumer.consume_msg, args=(producer_lock, eventQ,))
	process_pool.append(p)

	print(f"---- Starting producer and consumer processes ----")
	for each in process_pool:
		each.start()

	for each in process_pool:
		try:
			each.join()
		except KeyboardInterrupt:
			print("---- join exception on KeyboardInterrupt ----")
		except Exception as e:
			print(f"---- join exception {e} ----")