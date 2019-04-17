#!/usr/bin/python

# Notes:
# -------
# From: https://realpython.com/async-io-python/
# 1) async:
# The syntax async def introduces either a native coroutine or an asynchronous generator. 
# The expressions async with and async for are also valid.
# A function that you introduce with async def is a coroutine. 
# It may use await, return, or yield, but all of these are optional
# 2) await:
# The keyword await passes function control back to the event loop. 
# It suspends the execution of the surrounding coroutine. 
# If Python encounters an await f() expression in the scope of g(), await tells the event loop, 
# "Suspend execution of g() until whatever I'm waiting on - the result of f() - is returned. 
# In the meantime, go let something else run."
# Using await and/or return creates a coroutine function. To call a coroutine function, 
# you must await it to get its results.
# 3) older forms:
# Note that generator-based coroutine support has been outdated since the async/await 
# syntax was put in place in Python 3.5.

import asyncio
import random
import datetime
import sys

LIMIT = 10000

task_pool = []

def getTimestamp():
        now = datetime.datetime.now()
        dt = now.strftime("%d-%m-%Y %H:%M:%S.%f")
        return dt

class Producer(object):
	def __init__(self):
		self.n = 0
		self.eventQ = None

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

	async def produce_msg(self,eventQ,interval):
		self.eventQ = eventQ
		self.interval = interval
		count = 0
		while True:
			msg = self.generateEvent()
			await self.eventQ.put(msg)
			tstamp = getTimestamp()
			print(f"{tstamp}: Producer() produced =>\t'{msg}'")
			await asyncio.sleep(self.interval)
			count += 1
			if count >= LIMIT:
				print("Putting None into queue")
				await self.eventQ.put(None)
				return
			
class Consumer(object):
	def __init__(self):
		self.msg = None
		self.eventQ = None
				
	async def consume_msg(self,eventQ):
		self.eventQ = eventQ
		# Fake a delay before consumer starts
		await asyncio.sleep(1)
		while True:
			self.msg = await eventQ.get()
			if self.msg == None:
				print("Read None from queue")
				return
			# At this point we got something - don't examine if queue is empty
			if eventQ.empty():
				print("isEmpty eventQ")
			tstamp = getTimestamp()
			print(f"{tstamp}: Consumer() consumed =>\t'{self.msg}'")

def loop_exception_handler(loop,ctx):
	print(f"loop_exception_handler - stop and close loop")
	loop.stop()
	loop.close()

if __name__ == '__main__':
	eventQ = asyncio.Queue()
	loop = asyncio.get_event_loop()
	loop.set_exception_handler(loop_exception_handler)
	
	p = Producer()
	c = Consumer()
	#
	interval = 0.01
	t1 = p.produce_msg(eventQ,interval)
	#loop.create_task(t1)
	task_pool.append(t1)
	t2 = c.consume_msg(eventQ,)
	#loop.create_task(t2)
	task_pool.append(t2)
	try:
		#loop.run_forever() # This way we don't terminate properly after LIMIT events
		loop.run_until_complete(asyncio.gather(t1,t2))
	except KeyboardInterrupt:
		print("Keyboard Interrupt main loop - stopping loop here")
	except:
		print("Exception")
		
	for t in task_pool:
		t.close()
	loop.stop()
	loop.close()