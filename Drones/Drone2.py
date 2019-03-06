#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from random import randint
import socket
import math
from math import sin, cos, sqrt, atan2
from dronekit_sitl import SITL
import threading
visitedNodeSize = 0

def calculateDistance(lat1,long1,lat2,long2):
		R = 6373.0
		PI = 3.14159265359
		dlon = long2-long1
		dlat = lat2-lat1
		a = (sin(dlat/2*PI/180))**2 + cos(lat1*PI/180) * cos(lat2*PI/180) * (sin(dlon/2*PI/180))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		return R*c*1000
		
def sendDronePos(threadName,delay,finish):
	prevLat = vehicle.location.global_relative_frame.lat
	prevLon = vehicle.location.global_relative_frame.lon
	odometer = 0
	while finish == False:
		time.sleep(delay)
		odometer += calculateDistance(prevLat, prevLon, vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
		prevLat = vehicle.location.global_relative_frame.lat
		prevLon = vehicle.location.global_relative_frame.lon
		ServerSend.sendto((str(vehicle.location.global_relative_frame.lat) + "," + str(vehicle.location.global_relative_frame.lon) 
				+ ":" + str(vehicle.attitude.yaw) + "," + str(vehicle.attitude.roll) + "," + str(vehicle.attitude.pitch)
				+ ":" + str(vehicle.airspeed) + "," + str(vehicle.groundspeed)
				+ ":" + str(vehicle.battery.voltage) + "," + str(vehicle.battery.current) + "," + str(vehicle.battery.level)
				+ ":" + str(odometer)
				+ ":" + str(visitedNodeSize)),(UDP_IP,Server_Send_Port))
				
		
class myThread (threading.Thread):
	finish = False
	def __init__(self, tID, Name,finito):
		threading.Thread.__init__(self)
		self.threadID = tID
		self.name = Name
		self.finish = finito
		print("created")
		
	def run(self):
		print ("Starting " + self.name)
		sendDronePos(self.name,0.1,self.finish)
		print ("Exiting " + self.name)

UDP_IP = "127.0.0.1"
Send_Port= 5006
Recv_Port = 5005
Server_Send_Port = 5010
Server_Recv_Port = 5009

DroneSend = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM) 


DroneRecv = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM)
                     
ServerSend = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM)
                  
ServerRecv = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM)

ServerRecv.settimeout(1)
DroneRecv.settimeout(1)

# Set up option parsing to get connection string
import argparse
connSend = ""
connRecv = ""
class Node:
	x = 0
	y = 0
	visited = False
	def __init__(self,x,y):
		self.x = float(x)
		self.y = float(y)
	
class Point:
	x = 0
	y = 0
	def __init__(self, coordx, coordy):
		self.x = float(coordx)
		self.y = float(coordy)
		
def getDroneLocation(data):
	point = Point(data.lat,data.lon)
	return point
	
def pointDistance(p1,p2):
	x2 = (p1.lon-p2.lon)*(p1.lon-p2.lon)
	y2 = (p1.lat-p2.lat)*(p1.lat-p2.lat)
	dist = math.sqrt(x2+y2)
	return dist
		

		
class Graph:
	numberOfNode = 0
	cols = 0
	rows = 0
	Matrix = None
	connSend = ""
	List = []
	visited = 0
	
	def __init__(self,a,b,c,d,res):
		self.cols = int(min((b.x - a.x),(d.x - c.x))/res) + 1 
		self.rows = int(min((a.y - c.y),(b.y - d.y))/res) + 1
		print(self.rows)
		print(self.cols)
		k = a.x
		g = a.y
		self.Matrix = [[Node((k + res*j),(g - res*i)) for j in range(self.cols)] for i in range(self.rows)]
		for k in range(self.cols):
			for g in range(self.rows):
				self.List.append(Node(k,g))
		
		
	def calculateDistance(self,lat1,long1,lat2,long2):
		R = 6373.0
		dlon = long2-long1
		dlat = lat2-lat1
		a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		return R*c

	def updateGraph(self, connRecv):
		if (len(connRecv) > 2 and len(connRecv) < 6):
			x,y = connRecv.split(",",1)
			self.Matrix[int(x[0])][int(y[0])].visited = True
			self.visited = self.visited + 1
			for n in range(len(self.List)-1):
				if(self.List[n].x == int(x[0]) and self.List[n].y == int(y[0])):
					self.List.pop(n)
			global visitedNodeSize
			visitedNodeSize = self.visited

			
		
	def sendDataToDrone(self):
		while True:
			try:
				data, addr = DroneRecv.recvfrom(1024)
				self.updateGraph(data)
				self.connSend = ""
			except socket.timeout:
				print("No data timeout")
			DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
			time.sleep(0.5)
			
			
	def run(self):
		t1 = threading.Thread(target=self.sendDataToDrone)
		t1.start()
	
	def maze_vertical(self,minRow,maxRow,minCol,maxCol):
		arm_and_takeoff(10)
		time.sleep(5)
		i = maxRow 
		j = maxCol 
		count = 0
		vehicle.groundspeed = 10.0
		
		while(True):
			try:
				data, addr = ServerRecv.recvfrom(1024)
				print(data)
				if data == "stop":
					vehicle.mode = VehicleMode("RTL")
					break
			except socket.timeout:
				print("No data timeout")
			print ("count :",count)
			count = count +1
			print ("i :",i," j :",j)
			print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
			
			p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
			self.Matrix[i][j].visited = True
			self.updateGraph(str(i) + "," + str(j))
			self.connSend = self.connSend + str(i) + "," + str(j) 
			DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
			print (self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
			vehicle.simple_goto(p1)
			
			
			
			while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
				#print (self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
				time.sleep(1)
				
			if ((i-1) >= minRow) and ((self.Matrix[i-1][j]).visited == False) :
				i = i-1
			elif ((i+1) <= maxRow) and ((self.Matrix[i+1][j]).visited == False) :
				i = i+1
			elif ((j-1) >= minCol) and ((self.Matrix[i][j-1]).visited == False) :
				j = j-1
			else :
				break
	
	
					
	def maze_horizontal(self,minRow,maxRow,minCol,maxCol):
		arm_and_takeoff(10)
		i = maxRow 
		j = maxCol 
		count = 0
		k = 0
		vehicle.groundspeed = 10.0
		while(True):
			try:
				data, addr = ServerRecv.recvfrom(1024)
				print(data)
				if data == "stop":
					vehicle.mode = VehicleMode("RTL")
					break
			except socket.timeout:
				print("No data timeout")
			
			print ("count :",count)
			count = count +1
			print ("i :",i," j :",j)
			print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
			
			p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 10)
			
			self.Matrix[i][j].visited = True
			self.updateGraph(str(i) + "," + str(j))
			self.connSend = self.connSend + str(i) + "," + str(j) 
			DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
			for n in range(len(self.List)-1):
					if(self.List[n].x == int(i) and self.List[n].y == int(j)):
						self.List.pop(n)
			
			print (pointDistance(p1,vehicle.location.global_relative_frame))
			vehicle.simple_goto(p1)
			
			while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
				time.sleep(1)
				
			k = 1
			
			if ((j-1) >= minCol) and ((self.Matrix[i][j-1]).visited == False):
				j = j-1
			elif ((j+1) <= maxCol) and ((self.Matrix[i][j+1]).visited == False) :
				j = j+1
			elif ((i-1) >= minRow) and ((self.Matrix[i-1][j]).visited == False) :
				i = i-1
			else :
				break
				
	def spiral(self,minRow,maxRow,minCol,maxCol):
		arm_and_takeoff(10)
		i = ((maxRow + minRow)/2) + 1
		j = ((maxCol + minCol)/2) 
		count = 0
		counter1 = 1
		counter2 = 2
		start = True
		while(True):
			try:
				data, addr = ServerRecv.recvfrom(1024)
				print(data)
				if data == "stop":
					vehicle.mode = VehicleMode("RTL")
					break
			except socket.timeout:
				print("No data timeout")
			check = 0
			if (i == maxRow-1) and (j == maxCol-1) :
				self.connSend = ""
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
			if start == True:
				self.connSend = ""
				data, addr = DroneRecv.recvfrom(1024)
				
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
				start = False
			kgn = 0
			while (kgn < counter2) and (i-1 >= minCol) and ((self.Matrix[i-1][j]).visited == False) :
				try:
					data, addr = ServerRecv.recvfrom(1024)
					print(data)
					if data == "stop":
						vehicle.mode = VehicleMode("RTL")
						break
				except socket.timeout:
					print("No data timeout")
				i = i-1
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				
				
				
				
			
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
				check = check + 1
				kgn += 1
				
			counter2 += 1
			kgn = 0
			while (kgn < counter1) and (j+1 <= maxCol) and ((self.Matrix[i][j+1]).visited == False) :
				try:
					data, addr = ServerRecv.recvfrom(1024)
					print(data)
					if data == "stop":
						vehicle.mode = VehicleMode("RTL")
						break
				except socket.timeout:
					print("No data timeout")
				j = j+1
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				
		
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
				check = check + 1
				kgn += 1
			counter1 += 1
			kgn = 0
			while (kgn <  counter2) and (i+1 <= maxRow) and ((self.Matrix[i+1][j]).visited == False) :
				try:
					data, addr = ServerRecv.recvfrom(1024)
					print(data)
					if data == "stop":
						vehicle.mode = VehicleMode("RTL")
						break
				except socket.timeout:
					print("No data timeout")
				i = i+1
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				
				
				
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
				check = check + 1
				kgn += 1
			counter2 += 1
			kgn = 0
			while (kgn < counter1) and (j-1 >= 0) and ((self.Matrix[i][j-1]).visited == False) :
				try:
					data, addr = ServerRecv.recvfrom(1024)
					print(data)
					if data == "stop":
						vehicle.mode = VehicleMode("RTL")
						break
				except socket.timeout:
					print("No data timeout")
				j = j-1
				print ("count :",count)
				count = count +1
				print ("i :",i," j :",j)
				print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
				
				p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
				self.Matrix[i][j].visited = True
				self.updateGraph(str(i) + "," + str(j))
				self.connSend = self.connSend + str(i) + "," + str(j) 
				DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
				
				
			
				vehicle.simple_goto(p1)
				while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
					time.sleep(1)
				check = check + 1
				kgn += 1
			counter1 += 1
			if check == 0 :
				break
			
	def random_traverse(self,minRow,maxRow,minCol,maxCol) :
		arm_and_takeoff(10)
		i = maxRow 
		j = maxCol 
		count = 0
		while(True):
			try:
				data, addr = ServerRecv.recvfrom(1024)
				print(data)
				if data == "stop":
					vehicle.mode = VehicleMode("RTL")
					break
			except socket.timeout:
				print("No data timeout")
			list = []
			print ("count :",count)
			count = count +1
			print ("i :",i," j :",j)
			print ("x :",(self.Matrix[i][j]).x," y :",(self.Matrix[i][j]).y)
			p1 = LocationGlobalRelative((self.Matrix[i][j]).y, (self.Matrix[i][j]).x, 20)
			for n in range(len(self.List)-1):
				if(self.List[n].x == i) and (self.List[n].y == j):
					self.List.pop(n)
			self.Matrix[i][j].visited = True
			self.connSend = self.connSend + str(i) + "," + str(j) 
			DroneSend.sendto(self.connSend,(UDP_IP,Send_Port))
			self.updateGraph(str(i) + "," + str(j))
			vehicle.simple_goto(p1)
			
			while(self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon) > 0.1):
				#vehicle.simple_goto(p1)
				#print ("distance :",self.calculateDistance(p1.lat,p1.lon,vehicle.location.global_relative_frame.lat,vehicle.location.global_relative_frame.lon))
				time.sleep(1)
			if ((j+1) <= maxCol) and ((self.Matrix[i][j+1]).visited == False) :
				list.append('f')
			if ((i+1) <= maxRow) and ((self.Matrix[i+1][j]).visited == False) :
				list.append('r')
			if ((i-1) >= minRow) and ((self.Matrix[i-1][j]).visited == False) :
				list.append('l')
			if ((j-1) >= minCol) and ((self.Matrix[i][j-1]).visited == False) :
				list.append('b')
				
			if len(list) == 0 :
				
				break
			else :	
				rand = randint(0,len(list)-1)
				if list[rand] == 'f' :
					j = j + 1
				elif list[rand] == 'r' :
					i = i + 1
				elif list[rand] == 'l' :
					i = i - 1
				elif list[rand] == 'b'	:
					j = j - 1
					
			
			
			
			
			
		
		


		
			
		
	
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

	

			


	
			

	
	

connection_string = args.connect
sitl = SITL()


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = 'tcp:127.0.0.1:5762'


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)



def arm_and_takeoff(aTargetAltitude):
    

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1) 

        
     

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
  

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)
	time.sleep(5)
    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) 

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

ServerRecv.bind((UDP_IP,Server_Recv_Port))
print("Ready!")



while True:
	try:
		data, addr = ServerRecv.recvfrom(1024)
		print(data)
		point1,point2,point3,point4 = data.split(":",4)
		lat1,lon1 = point1.split(",",1)
		lat2,lon2 = point2.split(",",1)
		lat3,lon3 = point3.split(",",1)
		lat4,lon4 = point4.split(",",1)
		corner1 = Point(lon1,lat1)
		corner2 = Point(lon2,lat2)
		corner3 = Point(lon3,lat3)
		corner4 = Point(lon4,lat4)
		
		graphG = Graph(corner1,corner2,corner3,corner4,0.00015)
	except socket.timeout:
		print("No data timeout")
		continue
	
	
	if data is not None:
		break

DroneRecv.bind((UDP_IP,Recv_Port))
DroneSend.sendto("Drone2 geldi",(UDP_IP,Send_Port))
while True:
	data, addr = DroneRecv.recvfrom(1024)
	print(data)
	DroneSend.sendto("Drone2 geldi",(UDP_IP,Send_Port))
	if data is not None:
		break
		


thread1 = myThread(1, "Thread-1",False)
thread1.setDeamon = False
thread1.start()







graphG.run()

while True:
	try:
		data, addr = ServerRecv.recvfrom(1024)
		print(data)
		if(data[0] == "M"):
			m,algo,row,col = data.split(":",4)
			rowMin, rowMax = row.split(",",1)
			colMin, colMax = col.split(",",1)
			if(algo == "ZV"):
				graphG.maze_vertical(int(rowMin),int(rowMax),int(colMin),int(colMax))
			elif(algo == "ZH"):
				graphG.maze_horizontal(int(rowMin),int(rowMax),int(colMin),int(colMax))
			elif(algo == "SP"):
				graphG.spiral(int(rowMin),int(rowMax),int(colMin),int(colMax))
			elif(algo == "RA"):
				graphG.random_traverse(int(rowMin),int(rowMax),int(colMin),int(colMax))
	except socket.timeout:
		print("No data timeout")
		continue
		
#graphG.maze_vertical()
#graphG.spiral()
#graphG.random_traverse()
#print("Returning to Launch")
#vehicle.mode = VehicleMode("RTL")



# Close vehicle object before exiting script
print("Close vehicle object")
thread1.setDeamon = True
thread1.join()
vehicle.close()






# Shut down simulator if it was started.
"""if sitl:
    sitl.stop()"""

