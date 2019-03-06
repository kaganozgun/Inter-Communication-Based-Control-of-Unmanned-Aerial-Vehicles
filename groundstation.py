from qgmap import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import socket
import threading
import datetime

class DroneInfo:
	connection = False
	lon = None
	lat = None
	yaw = None
	roll = None
	pitch = None
	airspeed = None
	groundspeed = None
	voltage = None
	current = None
	battery = None
	odometer = None
	visitedSize = None 
	
class Node:
	x = 0
	y = 0
	visited = False
	def __init__(self,x,y):
		self.x = float(x)
		self.y = float(y)
		
class Location:
	lat = None
	lon = None
	
	def __init__(self, latitude,longitude):
		self.lat = latitude
		self.lon = longitude
	
class Graph:
	numberOfNode = 0
	cols = 0
	rows = 0
	Matrix = None
	connSend = ""
	List = []

	
	def __init__(self,a,b,c,d,res):
		self.rows = int(min((b.lon - a.lon),(d.lon - c.lon))/res) + 1 
		self.cols = int(min((a.lat - c.lat),(b.lat - d.lat))/res) + 1
		print(self.cols)
		print(self.rows)
		k = a.lon
		g = a.lat
		self.Matrix = [[Node((k + res*j),(g - res*i)) for j in range(self.rows)] for i in range(self.cols)]
		for k in range(self.rows):
			for g in range(self.cols):
				self.List.append(Node(k,g))

class Mission:
	def __init__(self):
		self.minRow = None
		self.maxRow = None
		self.minCol = None
		self.maxCol = None
		self.algo = None
	
	def setNewMission(self,minrow,maxrow,mincol,maxcol,algo):
		self.minRow = minrow
		self.maxRow = maxrow
		self.minCol = mincol
		self.maxCol = maxcol
		self.algo = algo
		
	def setRow(self,Row):
		self.minRow,self.maxRow = Row.split(",",1)

	def setCol(self,Col):
		self.minCol, self.maxCol = Col.split(",",1)
	
	def setAlgo(self,algo):
		self.algo = algo
		
	def getString(self):
		string = "M" + ":" + str(self.algo) + ":" + str(self.minRow) + "," + str(self.maxRow) + ":" + str(self.minCol) + "," + str(self.maxCol) 
		return string
	
d1Mission = Mission()
d2Mission = Mission()	
	
class Form(QDialog):
	def __init__(self, placeHolder,droneNo,Type, parent=None):
		super(Form,self).__init__(parent)
		self.d1Row = QLineEdit()
		self.d1Row.setObjectName("Row")
		self.d1Row.setPlaceholderText(placeHolder)
		self.droneNo = droneNo
		self.btn = QPushButton()
		self.btn.setObjectName("connect")
		self.btn.setText("OK")
		self.Type = Type
		layout = QFormLayout()
		layout.addWidget(self.d1Row)
		layout.addWidget(self.btn)
		
		self.setLayout(layout)
		self.connect(self.btn, SIGNAL("clicked()"),self.button_click)
		
	def button_click(self):
		shost = self.d1Row.text()
		print(shost)
		if(self.droneNo == 1):
			if(self.Type == "Row"):
				d1Mission.setRow(shost)
			else:
				d1Mission.setCol(shost)
		else:
			if(self.Type == "Row"):
				d2Mission.setRow(shost)
			else:
				d2Mission.setCol(shost)
		

		
workspaceList = []
workspaceFlag = False	
workspaceString = "Workspace:"

		
drone1Info = DroneInfo()
drone2Info = DroneInfo()
timer = 0
graphG = None



if __name__ == '__main__' :
	UDP_IP = "127.0.0.1"
	Send_Drone1_Port = 5007
	Recv_Drone1_Port = 5008
	Send_Drone2_Port = 5009
	Recv_Drone2_Port = 5010


	Drone1Send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	Drone2Send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	Drone1Recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	Drone2Recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	Drone1Recv.settimeout(1)
	Drone2Recv.settimeout(1)
	
	def goCoords() :
		def resetError() :
			coordsEdit.setStyleSheet('')
		try : latitude, longitude = coordsEdit.text().split(",")
		except ValueError :
			coordsEdit.setStyleSheet("color: red;")

			#QtCore.QTimer.singleShot(500, resetError)
		else :
			gmap.centerAt(latitude, longitude)
			gmap.moveMarker("MyDragableMark", latitude, longitude)

	def goAddress() :
		def resetError() :
			addressEdit.setStyleSheet('')
		coords = gmap.centerAtAddress(addressEdit.text())
		'''
		if coords is None :
			addressEdit.setStyleSheet("color: red;")
			QtCore.QTimer.singleShot(500, resetError)
			return
		'''
		gmap.moveMarker("MyDragableMark", *coords)
		coordsEdit.setText("{}, {}".format(*coords))

	def onMarkerMoved(key, latitude, longitude) :
		print("Moved!!", key, latitude, longitude)
		coordsEdit.setText("{}, {}".format(latitude, longitude))
	def onMarkerRClick(key) :
		print("RClick on ", key)
		gmap.setMarkerOptions(key, draggable=False)
	def onMarkerLClick(key) :
		print("LClick on ", key)
	def onMarkerDClick(key) :
		print("DClick on ", key)
		gmap.setMarkerOptions(key, draggable=True)

	def onMapMoved(latitude, longitude) :
		print("Moved to ", latitude, longitude)
	def onMapRClick(latitude, longitude) :
		print("RClick on ", latitude, longitude)
		if(len(workspaceList) < 4):
			workspaceList.append(Location(latitude,longitude))
			global workspaceString
			workspaceString = "Workspace:"
			for x in range(0, len(workspaceList)):
				workspace.clear()
				workspaceString += "\nPoint" + str(x+1) + ":  \n" + "lat: " + str(workspaceList[x].lat) + "   long: " + str(workspaceList[x].lon)
				workspace.insertPlainText(workspaceString)
				workspace.update()
				app.processEvents()
				markername = "\nPoint" + str(x+1)
				gmap.addMarker(markername ,workspaceList[x].lat,workspaceList[x].lon , **dict(
				icon="http://www.google.com/mapfiles/ms/micons/green-dot.png",
				draggable=False,
				title = markername
				))
				
	def onMapLClick(latitude, longitude) :
		print("LClick on ", latitude, longitude)
	def onMapDClick(latitude, longitude) :
		print("DClick on ", latitude, longitude)
		
	def stopDrone1():
		print("stopdrone1")
		Drone1Send.sendto("stop",(UDP_IP,Send_Drone1_Port))
	
	def stopDrone2():
		print("stopdrone2")
		Drone2Send.sendto("stop",(UDP_IP,Send_Drone2_Port))
	
	def startDrone1():
		print("startdrone1")
		print(d1Mission.getString())
		Drone1Send.sendto(d1Mission.getString(),(UDP_IP,Send_Drone1_Port))
		
	
	def startDrone2():
		print("startdrone2")
		print(d2Mission.getString())
		Drone2Send.sendto(d2Mission.getString(),(UDP_IP,Send_Drone2_Port))
		
		
	def btnstate(btn):
		if btn.text() == "Zigzag H":
			if btn.isChecked() == True:
				d1Mission.setAlgo("ZH")
				print("Zigzag H")
		if btn.text() == "Zigzag V":
			if btn.isChecked() == True:
				d1Mission.setAlgo("ZV")
				print("Zigzag V")
		if btn.text() == "Spiral":
			if btn.isChecked() == True:
				d1Mission.setAlgo("SP")
				print("Spiral")
		if btn.text() == "Random":
			if btn.isChecked() == True:
				d1Mission.setAlgo("RA")
				print("Random")
				
	def btnstate2(btn):
		if btn.text() == "Zigzag H":
			if btn.isChecked() == True:
				d2Mission.setAlgo("ZH")
				print("Zigzag H")
		if btn.text() == "Zigzag V":
			if btn.isChecked() == True:
				d2Mission.setAlgo("ZV")
				print("Zigzag V")
		if btn.text() == "Spiral":
			if btn.isChecked() == True:
				d2Mission.setAlgo("SP")
				print("Spiral")
		if btn.text() == "Random":
			if btn.isChecked() == True:
				d2Mission.setAlgo("RA")
				print("Random")
		
		
	def setWorkspace():
		wpString = str(workspaceList[0].lat) + "," + str(workspaceList[0].lon) + ":" + str(workspaceList[1].lat) + "," + str(workspaceList[1].lon) + ":" + str(workspaceList[2].lat) + "," + str(workspaceList[2].lon) + ":" + str(workspaceList[3].lat) + "," + str(workspaceList[3].lon)
		Drone1Send.sendto(wpString,(UDP_IP,Send_Drone1_Port))
		Drone2Send.sendto(wpString,(UDP_IP,Send_Drone2_Port))
		global workspaceFlag
		workspaceFlag = True
		graphG = Graph(workspaceList[0],workspaceList[1],workspaceList[2],workspaceList[3],0.00015)
		workspace.clear()
		global workspaceString
		workspaceString += "\nColumns: " + str(graphG.cols) + "   " + "Rows: " + str(graphG.rows)
		workspace.insertPlainText(workspaceString)
		workspace.update()
		app.processEvents()

	app = QtGui.QApplication([])
	w = QtGui.QDialog()
	subLayout1 = QtGui.QHBoxLayout()
	subLayout2 = QtGui.QHBoxLayout()
	subLayout3 = QtGui.QHBoxLayout()
	subLayout4 = QtGui.QHBoxLayout()
	leftLayout = QtGui.QVBoxLayout()
	rightLayout = QtGui.QVBoxLayout()
	i1TextLayout = QtGui.QHBoxLayout()
	i1AlgoLayout = QtGui.QVBoxLayout()
	i1ButtonLayout = QtGui.QVBoxLayout()
	i1RowLayout = QtGui.QFormLayout()
	i1ColLayout = QtGui.QHBoxLayout()
	i2TextLayout = QtGui.QHBoxLayout()
	i2AlgoLayout = QtGui.QVBoxLayout()
	i2ButtonLayout = QtGui.QVBoxLayout()
	i2RowLayout = QtGui.QHBoxLayout()
	i2ColLayout = QtGui.QHBoxLayout()
	mainLayout = QtGui.QHBoxLayout(w)
	infoBox1 = QtGui.QTextEdit()
	#infoBox1.setFixedHeight(30)
	infoBox1.setReadOnly(True)
	infoBox1.setLineWrapMode(QtGui.QTextEdit.NoWrap)
	infoBox1.insertPlainText("Drone-1 : " + "Not Connected" + "\nLat: " + str(drone1Info.lat) + "\nLong: " + str(drone1Info.lon) + 
		"\nRoll: " + str(drone1Info.roll) + "\nPitch: " + str(drone1Info.pitch) + "\nYaw: " + str(drone1Info.yaw) + 
		"\nGroundSpeed: " + str(drone1Info.groundspeed) + "\nAirSpeed: " + str(drone1Info.airspeed) + 
		"\nBattery \n   V: " + str(drone1Info.voltage) + "\n   A: " + str(drone1Info.current) + "\n   %: " + str(drone1Info.battery)+
		"\nVisited Nodes: " + str(drone1Info.visitedSize))
	stopButton1 = QtGui.QPushButton("Stop")
	stopButton1.clicked.connect(stopDrone1)
	stopButton2 = QtGui.QPushButton("Stop")
	stopButton2.clicked.connect(stopDrone2)
	infoBox2 = QtGui.QTextEdit()
	infoBox2.setReadOnly(True)
	infoBox2.setLineWrapMode(QtGui.QTextEdit.NoWrap)
	infoBox2.insertPlainText("Drone-2 : " + "Not Connected" + "\nLat: " + str(drone2Info.lat) + "\nLong: " + str(drone2Info.lon) + 
		"\nRoll: " + str(drone2Info.roll) + "\nPitch: " + str(drone2Info.pitch) + "\nYaw: " + str(drone2Info.yaw) + 
		"\nGroundSpeed: " + str(drone2Info.groundspeed) + "\nAirSpeed: " + str(drone2Info.airspeed) + 
		"\nBattery \n   V: " + str(drone2Info.voltage) + "\n   A: " + str(drone2Info.current) + "\n   %: " + str(drone2Info.battery)+
		"\nVisited Nodes: " + str(drone2Info.visitedSize))
	timeBox = QtGui.QTextEdit()
	timeBox.setFixedHeight(30)
	infoBox1.setFixedHeight(260)
	infoBox2.setFixedHeight(260)
	timeBox.setFixedHeight(30)
	timeBox.setReadOnly(True)
	timeBox.setLineWrapMode(QtGui.QTextEdit.NoWrap)
	timeBox.insertPlainText("Simulation Time: " + str(timer))
	blue = QtGui.QColor(0, 0, 255)
	red = QtGui.QColor(255, 0, 0)
	workspace = QtGui.QTextEdit()
	workspace.setReadOnly(True)
	workspace.setLineWrapMode(QtGui.QTextEdit.NoWrap)
	workspace.setFixedHeight(180)
	workspace.insertPlainText( "Workspace:")
	setWorkspaceButton = QtGui.QPushButton("Set Workspace")
	setWorkspaceButton.clicked.connect(setWorkspace)
	
	infoBox1.setTextColor(blue)
	infoBox2.setTextColor(red)
	
	cb1_1 = QCheckBox("Zigzag H")
	cb1_1.stateChanged.connect(lambda:btnstate(cb1_1))
	cb1_2 = QCheckBox("Zigzag V")
	cb1_2.stateChanged.connect(lambda:btnstate(cb1_2))
	cb1_3 = QCheckBox("Spiral")
	cb1_3.stateChanged.connect(lambda:btnstate(cb1_3))
	cb1_4 = QCheckBox("Random")
	cb1_4.stateChanged.connect(lambda:btnstate(cb1_4))
	startBtn1 = QPushButton("Start")
	startBtn1.clicked.connect(startDrone1)
	
	cb2_1 = QCheckBox("Zigzag H")
	cb2_1.stateChanged.connect(lambda:btnstate2(cb2_1))
	cb2_2 = QCheckBox("Zigzag V")
	cb2_2.stateChanged.connect(lambda:btnstate2(cb2_2))
	cb2_3 = QCheckBox("Spiral")
	cb2_3.stateChanged.connect(lambda:btnstate2(cb2_3))
	cb2_4 = QCheckBox("Random")
	cb2_4.stateChanged.connect(lambda:btnstate2(cb2_4))
	
	startBtn2 = QPushButton("Start")
	startBtn2.clicked.connect(startDrone2)
	
	gmap = QGoogleMap(w)
	gmap.mapMoved.connect(onMapMoved)
	gmap.markerMoved.connect(onMarkerMoved)
	gmap.mapClicked.connect(onMapLClick)
	gmap.mapDoubleClicked.connect(onMapDClick)
	gmap.mapRightClicked.connect(onMapRClick)
	gmap.markerClicked.connect(onMarkerLClick)
	gmap.markerDoubleClicked.connect(onMarkerDClick)
	gmap.markerRightClicked.connect(onMarkerRClick)
	
	i1TextLayout.addWidget(infoBox1)
	i1AlgoLayout.addWidget(cb1_1)
	i1AlgoLayout.addWidget(cb1_2)
	i1AlgoLayout.addWidget(cb1_3)
	i1AlgoLayout.addWidget(cb1_4)
	d1RowForm = Form("Row",1,"Row")
	d1ColForm = Form("Column",1,"Col")
	i1RowLayout.addWidget(d1RowForm)
	i1ColLayout.addWidget(d1ColForm)
	d2RowForm = Form("Row",2,"Row")
	d2ColForm = Form("Column",2,"Col")
	i2RowLayout.addWidget(d2RowForm)
	i2ColLayout.addWidget(d2ColForm)
	i1ButtonLayout.addLayout(i1RowLayout)
	i1ButtonLayout.addLayout(i1ColLayout)
	i1ButtonLayout.addWidget(startBtn1)
	i1ButtonLayout.addWidget(stopButton1)
	
	i2TextLayout.addWidget(infoBox2)
	i2AlgoLayout.addWidget(cb2_1)
	i2AlgoLayout.addWidget(cb2_2)
	i2AlgoLayout.addWidget(cb2_3)
	i2AlgoLayout.addWidget(cb2_4)
	i2ButtonLayout.addLayout(i2RowLayout)
	i2ButtonLayout.addLayout(i2ColLayout)
	i2ButtonLayout.addWidget(startBtn2)
	i2ButtonLayout.addWidget(stopButton2)
	
	subLayout1.addLayout(i1TextLayout)
	subLayout1.addLayout(i1AlgoLayout)
	subLayout1.addLayout(i1ButtonLayout)
	subLayout2.addLayout(i2TextLayout)
	subLayout2.addLayout(i2AlgoLayout)
	subLayout2.addLayout(i2ButtonLayout)
	subLayout3.addWidget(timeBox)
	subLayout4.addWidget(workspace)
	subLayout4.addWidget(setWorkspaceButton)
	
	leftLayout.addLayout(subLayout4)
	leftLayout.addLayout(subLayout1)
	leftLayout.addLayout(subLayout2)
	leftLayout.addLayout(subLayout3)
	rightLayout.addWidget(gmap)
	mainLayout.addLayout(leftLayout)
	mainLayout.addLayout(rightLayout)
	
	
	
	gmap.setSizePolicy(
		QtGui.QSizePolicy.MinimumExpanding,
		QtGui.QSizePolicy.MinimumExpanding)
	w.show()
	w.raise_()

	gmap.waitUntilReady()

	
	
	
	
	# Many icons at: https://sites.google.com/site/gmapsdevelopment/
	x = 0
	def gotoPoint(gmap,lon,lat,lon2,lat2):
		
		gmap.addMarker("X",lon,lat , **dict(
				icon="http://www.google.com/mapfiles/ms/micons/blue-dot.png",
				draggable=False,
				title = "X"
				))
		
		gmap.addMarker("Y",lon2, lat2 , **dict(
			icon="http://www.google.com/mapfiles/ms/micons/blue-dot.png",
			draggable=False,
			title = "Y"
			))
		
		
		gmap.addMarker("Z",lon2, lat2 , **dict(
			icon="http://www.google.com/mapfiles/ms/micons/blue-dot.png",
			draggable=False,
			title = "Z"
			))
		
		gmap.update()
		app.processEvents()
		
	def printDronesPos(gmap):
		data_old = None
		data2_old = None
		timer = datetime.datetime.now()
		counter1 = 0
		counter2 = 0 
		d1  = "d1"
		d2 = "d2"
		while True:
			try:
				data, addr = Drone1Recv.recvfrom(1024)
				data2, addr2 = Drone2Recv.recvfrom(1024)
				timer2 = datetime.datetime.now()
				if(data_old != data) or (data2_old != data2):
					location1, rpy1, speed1, battery1, odometer,visitedNodes = data.split(":",5)
					drone1Info.lon, drone1Info.lat = location1.split(",",1)
					drone1Info.roll, drone1Info.pitch, drone1Info.yaw = rpy1.split(",",2)
					drone1Info.airspeed, drone1Info.groundspeed = speed1.split(",",1)
					drone1Info.voltage,drone1Info.current,drone1Info.battery = battery1.split(",",2)
					drone1Info.odometer = odometer
					drone1Info.visitedSize = visitedNodes
					location2, rpy2, speed2,battery2, odometer2, visitedNodes2 = data2.split(":",5)
					drone2Info.lon, drone2Info.lat = location2.split(",",1)
					drone2Info.roll, drone2Info.pitch, drone2Info.yaw = rpy2.split(",",2)
					drone2Info.airspeed, drone2Info.groundspeed = speed2.split(",",1)
					drone2Info.voltage,drone2Info.current,drone2Info.battery = battery2.split(",",2)
					drone2Info.odometer = odometer2
					drone2Info.visitedSize = visitedNodes2
					
					if counter1%30 == 0:
						d1 += str(counter1)
						gmap.addMarker(d1,float(drone1Info.lon),float(drone1Info.lat) , **dict(
								icon="http://labs.google.com/ridefinder/images/mm_20_blue.png",
								draggable=True,
								))
					if counter2%30 == 0:
						d2 += str(counter2)
						gmap.addMarker(data2,float(drone2Info.lon),float(drone2Info.lat) , **dict(
								icon="http://labs.google.com/ridefinder/images/mm_20_red.png",
								draggable=True,
								))
					infoBox1.clear()
					infoBox1.insertPlainText("Drone-1 : " + "Connected" + "\nLat: " + str(drone1Info.lat) + "\nLong: " + str(drone1Info.lon) + 
						"\nRoll: " + str(float(drone1Info.roll)*3.14/180) + "\nPitch: " + str(float(drone1Info.pitch)*3.14/180) + "\nYaw: " + str(float(drone1Info.yaw)*3.14/180) + 
						"\nGroundSpeed: " + str(drone1Info.groundspeed) + "\nAirSpeed: " + str(drone1Info.airspeed) + 
						"\nBattery \n   V: " + str(drone1Info.voltage) + "\n   A: " + str(drone1Info.current) + "\n   %: " + str(drone1Info.battery)+
						"\nOdometer: " + str(drone1Info.odometer) +
						"\nVisited Nodes: " + str(drone1Info.visitedSize))
					infoBox2.clear()
					infoBox2.insertPlainText("Drone-2 : " + "Connected" + "\nLat: " + str(drone2Info.lat) + "\nLong: " + str(drone2Info.lon) + 
						"\nRoll: " + str(float(drone2Info.roll)*3.14/180) + "\nPitch: " + str(float(drone2Info.pitch)*3.14/180) + "\nYaw: " + str(float(drone2Info.yaw)*3.14/180) + 
						"\nGroundSpeed: " + str(drone2Info.groundspeed) + "\nAirSpeed: " + str(drone2Info.airspeed) + 
						"\nBattery \n   V: " + str(drone2Info.voltage) + "\n   A: " + str(drone2Info.current) + "\n   %: " + str(drone2Info.battery)+
						"\nOdometer: " + str(drone2Info.odometer) +
						"\nVisited Nodes: " + str(drone2Info.visitedSize))
					timeBox.clear()
					timeBox.insertPlainText("Simulation Time: " + str(timer2 - timer) + "\n")
					infoBox1.update()
					infoBox2.update()
					timeBox.update()
					data_old = data
					data2_old = data2
					gmap.update()
					app.processEvents()
			except socket.timeout:
				print("No data timeout")
				
	
			app.processEvents()
			gmap.update()
			counter1 += 1
			counter2 += 1
			time.sleep(0.1)
			
			
			
	
	
	gmap.centerAt(41.105296,29.023084)
	gmap.setZoom(18)
	
	Drone1Recv.bind((UDP_IP,Recv_Drone1_Port))
	Drone2Recv.bind((UDP_IP,Recv_Drone2_Port))
	
	
	
			
	
	printDronesPos(gmap)
	app.exec_()
	
	
	
	
		
			
		
			
			
			
				

	
	

	
	#gotoPoint(gmap, 41.35, 2.05, 41.35, 20.05)
	



	
