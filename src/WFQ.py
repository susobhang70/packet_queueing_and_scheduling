import queue
import time
import threading

from socket import *

PORT = 50000
SENDPORT = 50001
MAXRECVSTRING = 100

# three dicts where each entry in dict should be a
# (key, value) with key = index (the packet number)
# start from 0 for key
# and value a list with [arrival time - in ms, actual packet]
# finish number will be appended to this value list
# also arrival time = time.time() - start_time
A = {}
B = {}
C = {}

A_weight, A_packetsize = 1.0, 100
B_weight, B_packetsize = 2.0, 50
C_weight, C_packetsize = 0.5, 100

# one for each of A, B, C
# 0 indicates inactive
active_conn_list = [0,0,0]

# the queue with Transmit instructions
send_queue = queue.Queue()

# current finish numbers
cur_finish_nums = [0,0,0]

# last transmit time
last_trans_time = -100

# start time
start_time = 0

def make_inactive(index):
	# make connection of that index inactive
	active_conn_list[index] = 0
def make_active(index):
	# make connection of that index active
	active_conn_list[index] = 1
def get_num_of_active_conns():
	# return (the number of ones * weight)
	return (A_weight*active_conn_list[0]) +\
		   (B_weight*active_conn_list[1]) +\
		   (C_weight*active_conn_list[2])

def receive_packet():
	# add received packets to respective dicts
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', PORT))
	# count of packets of each connection, used for indexing
	A_count, B_count, C_count = 0,0,0
	# count of all packets received
	count = 0
	while(count < 1600):
		m = s.recvfrom(MAXRECVSTRING)
		if len(m) != 0:
			# if A connection
			if m[0][0] == '1':
				A[A_count] = [(time.time() - start_time)*1000, m]
				A_count += 1
			# if B connection
			elif m[0][0] == '2':
				B[B_count] = [(time.time() - start_time)*1000, m]
				B_count += 1
			# if C connection
			elif m[0][0] == '3':
				C[C_count] = [(time.time() - start_time)*1000, m]
				C_count += 1
			# update count of messages received
			count += 1

def add_to_send_queue(dict_name, index):
	# add the packet to the queue which holds packets to be transmitted
	send_queue.put(dict_name[index])

def send_packet():
	# a process which sends packets from send_queue
	# counter of number of packets sent
	count = 0
	while True:
		# get only the message, hence ()[1][0]
		if not send_queue.empty():
			item = send_queue.get()[1][0]

			s = socket(AF_INET, SOCK_DGRAM)
			s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
			s.sendto(item, ('127.255.255.255', SENDPORT))

			count += 1
			if(count == 1600):
				break

			# The link rate is taken to be 1 byte/ms, so sleep for that much time
			time.sleep(len(item) / 1000)

def calc_round_num(prev_round_num, time_diff):
	try:
		return prev_round_num + ((1/get_num_of_active_conns())*time_diff)
	except:
		# when no connection is active
		return 0

def set_finish_num():
	# last time we added something to the send_queue
	last_trans_time = 0
	# add to queue count
	add_to_queue = 0
	# used to calculate when we put next packet in send_queue
	prev_finish_num = 0
	# used to make connections inactive
	prev_finish_nums = [0,0,0]
	# indexes which we are currently trying to send
	A_cur, B_cur, C_cur = 0, 0, 0
	# round number variable
	round_num = 0
	# set the start time
	start_time = time.time()
	
	while True:
		cur_time = time.time()
		time_diff = cur_time - start_time
		# every millisecond
		if time_diff >= 0.001:
			# caclulate the round number
			round_num = calc_round_num(round_num, time_diff)
			# check if some connection becomes inactive
			for i in xrange(len(prev_finish_nums)):
				if prev_finish_nums[i] <= round_num and cur_finish_nums[i] == 0:
					make_inactive(i)
			# if current index is in dict
			if A_cur in A:
				value = A[A_cur]
				if A_cur == 0:
					finish_num = round_num + (A_packetsize/A_weight)
				else:
					# we know that finish number of previous index is already calculated, hence [A_cur-1][2]
					finish_num = max(round_num,A[A_cur-1][2]) + (A_packetsize/A_weight)
				value.append(finish_num)
				# modify value of that key
				A[A_cur] = value
				if cur_finish_nums[0] == 0:
					cur_finish_nums[0] = [finish_num, A_cur]
					make_active(0)
				A_cur += 1
			# if current index is in dict
			if B_cur in B:
				value = B[B_cur]
				if B_cur == 0:
					finish_num = round_num + (B_packetsize/B_weight)
				else:
					# we know that finish number of previous index is already calculated, hence [B_cur-1][2]
					finish_num = max(round_num,B[B_cur-1][2]) + (B_packetsize/B_weight)
				value.append(finish_num)
				# modify value of that key
				B[B_cur] = value
				if cur_finish_nums[1] == 0:
					cur_finish_nums[1] = [finish_num, B_cur]
					make_active(1)
				B_cur += 1
			# if current index is in dict
			if C_cur in C:
				value = C[C_cur]
				if C_cur == 0:
					finish_num = round_num + (C_packetsize/C_weight)
				else:
					# we know that finish number of previous index is already calculated, hence [C_cur-1][2]
					finish_num = max(round_num,C[C_cur-1][2]) + (C_packetsize/C_weight)
				value.append(finish_num)
				# modify value of that key
				C[C_cur] = value
				if cur_finish_nums[2] == 0:
					cur_finish_nums[2] = [finish_num, C_cur]
					make_active(2)
				C_cur += 1

			# transmit from lowest finish number list
			if (cur_time - last_trans_time) * 1000 >= prev_finish_num:
				temp_val = 10000000
				i = -1
				# find the lowest finish number connection
				for j in xrange(len(cur_finish_nums)):
					try:
						if cur_finish_nums[j][0] < temp_val:
							i = j
							temp_val = cur_finish_nums[j][0]
					except:
						continue
				if i == 0:
					add_to_send_queue(A,cur_finish_nums[i][1])
					add_to_queue += 1
					prev_finish_num = cur_finish_nums[i][0]
					last_trans_time = cur_time
					next_index = cur_finish_nums[i][1] + 1
					prev_finish_nums[i] = cur_finish_nums[i][0]
					if next_index in A and len(A[next_index]) == 3:
						cur_finish_nums[0] = [A[next_index][2], next_index]
						make_active(0)
					else:
						cur_finish_nums[0] = 0
				elif i == 1:
					add_to_send_queue(B,cur_finish_nums[i][1])
					add_to_queue += 1
					prev_finish_num = cur_finish_nums[i][0]
					last_trans_time = cur_time
					next_index = cur_finish_nums[i][1] + 1
					prev_finish_nums[i] = cur_finish_nums[i][0]
					if next_index in B and len(B[next_index]) == 3:
						cur_finish_nums[1] = [B[next_index][2], next_index]
						make_active(1)
					else:
						cur_finish_nums[1] = 0
				elif i == 2:
					add_to_send_queue(C,cur_finish_nums[i][1])
					add_to_queue += 1
					prev_finish_num = cur_finish_nums[i][0]
					last_trans_time = cur_time
					next_index = cur_finish_nums[i][1] + 1
					prev_finish_nums[i] = cur_finish_nums[i][0]
					if next_index in C and len(C[next_index]) == 3:
						cur_finish_nums[2] = [C[next_index][2], next_index]
						make_active(2)
					else:
						cur_finish_nums[2] = 0

			# update time
			start_time = cur_time
			if add_to_queue == 1600:
				break

def main():
	start_time = time.time()
	t1 = threading.Thread(target=set_finish_num,args=())
	t2 = threading.Thread(target=receive_packet,args=())
	t3 = threading.Thread(target=send_packet,args=())
	t1.start()
	t2.start()
	t3.start()

if __name__ == '__main__':
	main()