from __future__ import print_function
import os
class net:
	def __init__(self,nm):
		self.pins={}# name : (x,y)
		self.transmissionLine=False	
		self.name= nm
		self.number=-1#Assigned at the time of routing
		self.estimatedLength=0
		self.actualLength=0
		self.bends=0
	def estimateLength(self):	
		for i in range (0,len(self.pins)-1):
			pin1 = self.pins[self.pins.keys()[i]]
			pin2 = self.pins[self.pins.keys()[i+1]]
			self.estimatedLength+=abs(pin1[0]-pin2[0])+abs(pin1[1]-pin2[1]) #abs(x1-x2) + abs(y1-y2)
	def returnBbox(self):
		xmax=0
		ymax=0
		xmin=float("inf")
		ymin=float("inf")
		for pin in self.pins.values():
			x,y=pin
			if(x>xmax):
				xmax=x
			if(x<xmin):
				xmin=x
			if(y>ymax):
				ymax=y
			if(y<ymin):
				ymin=y
			
		return ((xmin,ymin),(xmax,ymax))
		#print self.estimatedLength
		
	
cellLocation={}
setOfNets={}
def dumpNets(nets):
	for key in nets.keys():
		print( key , nets[key].pins, nets[key].estimatedLength, nets[key].transmissionLine)
def dumpRoutedLength(nets,fname):
	f= open(fname+".rwl","w")
	print ("Length of Nets after Routing ",file=f)
	totalNetLength=0
	totalTLLength=0
	totalBends=0
	totalRouted=0
	for key in nets.keys():
		totalNetLength+=nets[key].actualLength
		totalBends+=nets[key].bends
		if(nets[key].actualLength>0):
			totalRouted+=1
		if(nets[key].transmissionLine):
			totalTLLength+=nets[key].actualLength
			totalNetLength+=2* nets[key].actualLength
			totalBends+=2*nets[key].bends

		print (key+" :"+  str(nets[key].actualLength)+ ", Number of bends,"+str(nets[key].bends) ,file=f)
	print ("Total Length of Nets after Routing "+ str(totalNetLength),file=f)
	print ("Total Area under   Routing "+ str(totalNetLength),file=f)
	print ("Total Transmission line Length of Nets after Routing "+ str(totalTLLength),file=f)
	print ("Total Area under  Transmission line afer Routing "+ str(totalTLLength),file=f)
	print ("Total Bends afterr Routing "+ str(totalBends),file=f)
	print ("Routing complete by:  "+ str(100* float(totalRouted)/len(nets.keys()) )+" % ",file=f)
def dumpEstimatedLength(nets,fname):
	f= open(fname+".ewl","w")
	print ("Estimated Length of Nets Before Routing in descendnig order of length",file=f)
	temp={}
	for key in nets.keys():
		leng= nets[key].estimatedLength
		if(leng in temp.keys()):
			temp[leng].append(key)
		else:
			temp[leng]=[key]
	tempKeys=temp.keys()
	tempKeys.reverse()
	for leng in tempKeys:	
		for key in temp[leng]:
			print (key +":"+ str( nets[key].estimatedLength)+", Number of Pins,"+str(len(nets[key].pins.keys())),file=f)

def readNetsFromFile(nets, fileName):
	f= open( fileName, "rb")
	parseState =0 # 0 toplevel 1 reading nets 
	netDegree=0
	thisNet=0
	for line in f:
		l = line.split()
		 
		if(len(l)==0):
			continue
		if parseState ==0:
			if l[0]=="NetDegree":
				netDegree=int(l[2])
				parseState=1	
				netName=l[3]
				thisNet= net(netName)
		elif parseState==1:
				thisNet.pins[l[0]]=(0,0)
				netDegree=netDegree-1
				if(netDegree==0):
					nets[thisNet.name]=thisNet	
					parseState=0
def readTransmissionLine(nets,fileName):
	if(not os.path.exists(fileName+".tl")):	
		print("Improve routing by specifying nets in "+ fileName+".tl to be routed as transmission lines") 
		return
	f= open( fileName+".tl", "rb")
	
	for l in f :
		line = l.strip("\n")
		
		if(line==""):
			continue
		if(line in nets.keys()):
			nets[line].transmissionLine=True
		
def readCells(cells,fileName):
	f=open(fileName+".conf","rb")
	for line in f:
		line.strip()
		x=line.split("=")
		if(x[0]=="negCompX"):
			negCompX=int(x[1].strip())
		if(x[0]=="negCompY"):
			negCompY=int(x[1].strip())
		if(x[0]=="resolutionFact"):
			resolutionFact=int(x[1].strip())

	f=open(fileName+".pl","rb")	
	i=0
	for line in f:
		i=i+1
		if(i<7):
			continue
		l = line.split()
		cells[l[0]]=( int((int(l[1])+negCompX)/resolutionFact), (int(l[2]) +negCompY)/resolutionFact )	
		
def matchNetsAndCell(cells , nets ):
	for key in nets.keys():
		net = nets[key]
		for cell in net.pins.keys():
			if(cell in cells):
				net.pins[cell]=cells[cell]
		 
def calculateEstimatedLengths(nets):
	for net in nets.keys():
		nets[net].estimateLength()
def extractNets(cellLocation,setOfNets, f):
	readNetsFromFile(setOfNets,f+".nets")
	readCells(cellLocation,f)
	matchNetsAndCell(cellLocation , setOfNets)
	calculateEstimatedLengths(setOfNets)
	readTransmissionLine(setOfNets,f)
	#ndumpNets(setOfNets)
#nn	dumpEstimatedLength(setOfNets,"temp")
def returnNetOrdering(nets,Grid,scale,netNumDict):
	orderNet=[]
	for key in nets.keys():
		net = nets[key]
		if(key in orderNet):
			continue	
		if net.transmissionLine:
			orderNet.append(key)
	for key in nets.keys():
		net = nets[key]
		if(key in orderNet):
			continue
		tempList=[]
		(x1,y1),(x2,y2)=net.returnBbox()
		for i in range(x1*scale,x2*scale):
			for j in range ( y1*scale,y2*scale):	
				if((not Grid[i][j]==net.number) and Grid[i][j]>2):
					net2 = netNumDict[Grid[i][j]]
					if( net2.name in orderNet or net2.name in tempList):	
						pass
					else:
						if checkAllPinsInside(net2,x1,x2,y1,y2):
							orderNet.append(net2.name)
						else :	
							tempList.append(net2.name)
		orderNet+=tempList
		orderNet.append(key)
	orderNetObject=[]
	for key in orderNet:
		orderNetObject.append(nets[key])

	return orderNetObject	

def returnNetOrdering1(nets,Grid,scale,netNumDict):
	orderNet=[]
	for key in nets.keys():
		net = nets[key]
		if(net in orderNet):
			continue	
		if net.transmissionLine:
			orderNet.append(net)
	for key in nets.keys():
		net = nets[key]
		if(net in orderNet):
			continue
		tempList=[]
		(x1,y1),(x2,y2)=net.returnBbox()
		for i in range(x1*scale,x2*scale):
			for j in range ( y1*scale,y2*scale):	
				if((not Grid[i][j]==net.number) and Grid[i][j]>2):
					net2 = netNumDict[Grid[i][j]]
					if( not net2 in orderNet):	
						if checkAllPinsInside(net2,x1,x2,y1,y2):
							orderNet.append(net2)
						else :	
							tempList.append(net2)
		orderNet+=tempList
		orderNet.append(net)
	return orderNet	
			
			
def checkAllPinsInside(net,x1,x2,y1,y2):
	for pin in net.pins.values():
		x=pin[0]
		y=pin[1]
		if x<x1 or x>x2:	
			return False
		if y<y1 or y>y2:
			return False
	return True
	
#extractNets(cellLocation,setOfNets,"new")


