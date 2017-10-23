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

	def __init__(self, queue):
		self.__queue = queue
		self.__count = 1
		threading.Thread.__init__(self)

	def run(self):
		while 1:
			item = self.__queue.get()

			if self.__count == 1600:	# check for total number of packets
				break

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
	queue = Queue.Queue(0)

	Worker(queue).start()

	while(count < 1600):
		m = s.recvfrom(MAXRECVSTRING)
		if len(m) != 0:
			queue.put(m[0])
			count += 1

if __name__ == '__main__':
	main()