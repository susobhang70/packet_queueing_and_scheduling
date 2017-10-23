#!/usr/bin/env python
import threading
import Queue
import time, random

from socket import *

PORT = 50000
SENDPORT = 50001
MAXRECVSTRING = 100

class Worker(threading.Thread):
	'''The worker thread is responsible for sending packets'''

	def __init__(self, S1, S2, S3):
		self.__S1 = S1
		self.__S2 = S2
		self.__S3 = S3

		self.__count = 1

		self.__nextQueue = 0

		threading.Thread.__init__(self)

	def run(self):
		while 1:
			
			if self.__count == 1600:	# check for total number of packets
				break
			
			if self.__nextQueue == 0:
				if self.__S1.empty():
					self.__nextQueue = (self.__nextQueue + 1) % 3
					continue

				item = self.__S1.get()

			elif self.__nextQueue == 1:
				if self.__S2.empty():
					self.__nextQueue = (self.__nextQueue + 1) % 3
					continue

				item = self.__S2.get()

			elif self.__nextQueue == 2:
				if self.__S3.empty():
					self.__nextQueue = (self.__nextQueue + 1) % 3
					continue

				item = self.__S3.get()

			self.__nextQueue = (self.__nextQueue + 1) % 3
			self.__count += 1

			# Sends the item via UDP broadcast to destination
			s = socket(AF_INET, SOCK_DGRAM)
			s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
			s.sendto(item, ('127.255.255.255', SENDPORT))

			# The link rate is taken to be 1 byte/ms, so sleep for that much time
			time.sleep(len(item) / 1000)

def main():
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', PORT))

	count = 1

	S1 = Queue.Queue(0)
	S2 = Queue.Queue(0)
	S3 = Queue.Queue(0)

	Worker(S1, S2, S3).start()

	while(count < 1600):
		m = s.recvfrom(MAXRECVSTRING)
		if len(m) != 0:
			if m[0][0] == '1':
				S1.put(m[0])
			elif m[0][0] == '2':
				S2.put(m[0])
			else:
				S3.put(m[0])
			count += 1

if __name__ == '__main__':
	main()