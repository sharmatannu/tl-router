import pygame
import random
import sys
import net as netLib # my funtions
import os
# These Values get initialized once 

Inf= float("inf")
MapSize_x=40
MapSize_y=40
scaling=10
Wstraight = 2
spaceScale=5
WsameNet=1
WBendPenalty=1
inversion =False
screenX=800
screenY=600
numOfNets=0
StartNetNumber =4
GroundNumber=3
Grid =[ [0 for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
def DrawGrid():	
	global designName,netNumDic
	while(True):
		pygame.init()
		screen=pygame.display.set_mode((screenX,screenY))
		red = (255,0,0)
		black = (0,0,0)
		darkBlue = (0,0,128)
		white=(255,255,255)
		color=[(0,255,0), (0,0,255), (200,55,25), (105,200,20),(200,120,100),(100,0,200),(90,100,180)]
		screen.fill(white)
		startx=scaling
		starty=scaling
		thickness=1
		pygame.draw.rect(screen,black,(startx,starty,MapSize_x*scaling+scaling,MapSize_y*scaling+scaling),thickness)
		for event in pygame.event.get():
        		if event.type == pygame.QUIT:
		             pygame.quit(); return;
		for i in range(0,MapSize_x):
			for j in range(0,MapSize_y):
				ii=i
				jj=j
				if(inversion):
					ii=j
					jj=i	
				if Grid[i][j]==1:
					pygame.draw.rect(screen,red,(startx+ii*scaling,starty+jj*scaling,scaling,scaling),thickness)
				elif Grid[i][j]==2:
					pygame.draw.rect(screen,darkBlue,(startx+ii*scaling,starty+jj*scaling,scaling,scaling),thickness)
				elif Grid[i][j]==GroundNumber:
					pygame.draw.rect(screen,red,(startx+ii*scaling,starty+jj*scaling,scaling,scaling),thickness)
				elif Grid[i][j]>=StartNetNumber:
					val=Grid[i][j]
					col=color[(val-StartNetNumber)%7]
					if(netNumDic[val].transmissionLine):
						col=black
					pygame.draw.rect(screen,col,(startx+ii*scaling,starty+jj*scaling,scaling,scaling))
	
		pygame.display.update()
		if(not os.path.exists("./"+designName+".jpg")):
			pygame.image.save(screen,"./"+designName+".jpg")

#djikstra on Grid Initialization

Parent =[ [-1 for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
Distance =[ [Inf for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
#priority Queue
priorityQ={}

def MarkPathOnGrid((x,y),net,prevDir):
	if(Grid[x][y])==0:	
		net.actualLength+=1# another block added to this net . 
		Grid[x][y]=currentNumber#wire
		
	direction= Parent[x][y]
	if(net.transmissionLine):
		if(direction ==0 or direction==2):
			Grid[x][y-1]=GroundNumber#wire
			Grid[x][y+1]=GroundNumber#wire
		if(direction ==1 or direction==3):
			Grid[x-1][y]=GroundNumber#wire
			Grid[x+1][y]=GroundNumber#wire
	if(prevDir>-1): # detect bend ifor a valid direction only
		if((prevDir == 0 or prevDir==2) ):
			if(direction==1 or direction==3):
				net.bends+=1
		if((prevDir == 1 or prevDir==3) ):
			if(direction==0 or direction==2):
				net.bends+=1
				
	#print x,y,direction
	if direction ==-1:
		return ;
	if(direction==0):
		MarkPathOnGrid((x-1,y),net,direction) 
	if(direction==3):
		MarkPathOnGrid((x,y-1),net,direction) 
	if(direction==2):
		MarkPathOnGrid((x+1,y),net,direction) 
	if(direction==1):
		MarkPathOnGrid((x,y+1),net,direction) 
	
def markPinAsCurrentNet((x,y)):
	Grid[x][y]=currentNumber
	
def initializeSource((Sx,Sy)):
	global Parent,Distance,priorityQ
	Parent =[ [-1 for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
	Distance =[ [Inf for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
	#priority Queue
	Distance[Sx][Sy]=0
	priorityQ[0]=[(Sx,Sy)]# Source is Sx,Sy
	
def gridAvailable((x,y),net,horizontal):
	#print net.transmissionLine
	if net.transmissionLine:
		if(horizontal):
			if(y-1<0 or y+1>MapSize_y-1):
				return False 
			return Grid[x][ y-1]==0 and Grid[x][y+1]==0 and Grid[x][y]==0
		else:
			if(x-1<0 or x+1>MapSize_x-1):
				return False 
			return Grid[x-1][ y]==0 and Grid[x+1][y]==0 and Grid[x][y]==0
	else:
		if Grid[x][y] >0:
			return False
	return True
def gridSameNet((x,y)):
	if Grid[x][y] ==currentNumber:
		return True 
	return False
def currNetIsNotTL():
	return not netNumDic[currentNumber].transmissionLine

def addToQ(l,(x,y)):
	if(l in priorityQ.keys()):
		priorityQ[l].append((x,y))
	else:
		priorityQ[l]=[(x,y)]

def incrementinPQ(l,m,(x,y)):
	if( l in priorityQ.keys()): 
		if (x,y) in  priorityQ[l]:
			priorityQ[l].remove((x,y))
			if(len(priorityQ[l])==0):
				del priorityQ[l]	
	addToQ(m,(x,y))
def popPQ():
	ks=priorityQ.keys()
	ks.sort()
	u = ks[0]
	x =  priorityQ[u].pop() 
	if( len(priorityQ[u]) ==0):
		del priorityQ[u]
	return x
def emptyPQ():
	if len(priorityQ)==0:
		return True
def update(u,v,direction,net):
	newDist=Wstraight	
	horizontal=False
	#print "available"+str(gridAvailable(v,net,horizontal))
	if(direction ==1 and direction==3):
		horizontal=True
	if(gridSameNet(v) ):
		newDist=WsameNet
	elif (not gridAvailable(v,net,horizontal)):	
		return 
	if(not (Parent[u[0]][u[1]] ==direction )and not( Parent[u[0]][u[1]] == -1)):#extra cost for bend
		newDist+=WBendPenalty
	if(Distance[v[0]][v[1]]>Distance[u[0]][u[1]]+ newDist):
		incrementinPQ(Distance[v[0]][v[1]],Distance[u[0]][u[1]]+newDist,v)
		Distance[v[0]][v[1]]=Distance[u[0]][u[1]]+newDist
		Parent[v[0]][v[1]]=direction

def run_Dj(M, N,(x,y),net):
	while(not emptyPQ()):
		uu = popPQ()
		i = uu[0]
		j = uu[1]
		if(i==x and j==y):
			break
		if(i<M-1):
			update(uu, (i+1,j),0,net);
		if(j<N-1):
			update(uu,(i,j+1),3,net);
		if(i>0):
			update(uu, (i-1,j),2,net);
		if(j>0):
			update(uu,(i,j-1),1,net);


def markBlocks((x1,y1),(x2,y2)):
	for i in range(x1,x2):
		for j in range(y1,y2):
			Grid[i][j]=1
def markPins((x,y)):
	Grid[x][y]=2
def scaleBy((x,y)):
	#print x,y,"   :",x*5,y*5
	return (x*spaceScale,y*spaceScale) # obtain by mapsize / maximum value of coordinate seen . 
def getConf(fname):	
	global MapSize_x,MapSize_y,scaling,Wstraight,spaceScale,WsameNet,WBendPenalty,inversion ,screenX,screenY
	f=open(fname+".conf","rb")
	for line in f:
		line.strip()
		x=line.split("=")
		if(x[0]=="MapSize_x"):
			MapSize_x=int(x[1].strip())
		if(x[0]=="MapSize_y"):
			MapSize_y=int(x[1].strip())
		if(x[0]=="scaling"):
			scaling=int(x[1].strip())
		if(x[0]=="Wstraight" ):
			Wstraight =int(x[1].strip())
		if(x[0]=="spaceScale"):
			spaceScale=int(x[1].strip())
		if(x[0]=="WsameNet"):
			WsameNet=int(x[1].strip())
		if(x[0]=="WBendPenalty"):
			WBendPenalty=int(x[1].strip())
		if(x[0]=="inversion" ):
			inversion =int(x[1].strip())
		if(x[0]=="numOfNets"):
			numOfNets=int(x[1].strip())
		if(x[0]=="screenX"):
			screenX=int(x[1].strip())
		if(x[0]=="screenY"):
			screenY=int(x[1].strip())

####Main####
designName="new"
if(len(sys.argv)>1):
	designName=sys.argv[1]
getConf(designName)
Grid =[ [0 for y in range(0,MapSize_y) ]for x in range(0,MapSize_x)]
sys.setrecursionlimit(2100)
#This designs has only pins and no blocks . that is we are not marking blocks each module is a pin in itself .
setOfNets={}# name: net 
cellLocation={}# cellName : (x,y
currentNumber=StartNetNumber# blank Each net is numbered as per  
netNumDic={}#number:net# first used in ordering and then accesing ents by number from grid
netLib.extractNets(cellLocation,setOfNets,designName)
numOfNets=len(setOfNets.keys())
#net.dumpNets(setOfNets)
#print cellLocation
for netName in setOfNets.keys():
	net = setOfNets[netName]
	net.number=currentNumber
	netNumDic[currentNumber]=net
	for n in net.pins.keys():
		markPinAsCurrentNet(scaleBy(net.pins[n]))
	currentNumber+=1	
newOrder=netLib.returnNetOrdering(setOfNets,Grid,spaceScale,netNumDic)
print len(setOfNets)
print len(newOrder)

currentNumber=StartNetNumber
netNumDic={}

for  cell in cellLocation.keys():
	markPins(scaleBy(cellLocation[cell]))
DrawGrid()
#print x
netLib.dumpEstimatedLength(setOfNets,designName)
tlRouted=False
for net in newOrder:#setOfNets.keys():
	#net = setOfNets[netName]
	net.number=currentNumber
	netNumDic[currentNumber]=net
	print ("Routing Now : " +  net.name)
	if(tlRouted ==False and net.transmissionLine==False):
		tlRouted=True
		DrawGrid()
	#print net.pins.keys(), len(net.pins.keys())
	for n in net.pins.keys():
		markPinAsCurrentNet(scaleBy(net.pins[n]))
	for i in range(0, len(net.pins.keys())):
		if (i==0):
			continue
		initializeSource( scaleBy (net.pins[net.pins.keys()[0] ] ) )	
		run_Dj(MapSize_x,MapSize_y,scaleBy( net.pins[net.pins.keys()[i]] ),net)		
		MarkPathOnGrid(scaleBy( net.pins[net.pins.keys()[i]] ),net,-1)# initial direction is arbit when marking path
		#print "hahah"
	for n in net.pins.keys():
		markPins(scaleBy(net.pins[n]))
	currentNumber+=1	
netLib.dumpRoutedLength(setOfNets,designName)
DrawGrid()	
