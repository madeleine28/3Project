import cv2 
import numpy as np
from scipy.spatial import distance as dist
import os
import win32api
import win32con
import ctypes
from collections import Counter
import time
import webbrowser


handYLocation =[]
handYLocationCount = 0
currentCommand = "none"
project = "two"
questionTwoHands = False
questionTwoHandsCount = 1
view = "streetView"
leftToRightBool = False
initialFrameCounter = 0
#streetViewTabValues = {'changeView': 12, 'showArea:' 21}
#earthViewTabValues = {'changeView':15}


def main():
	global leftToRightBool
	global view
	global questionTwoHands
	global questionTwoHandsCount
	global initialFrameCounter
	url = 'https://maps.google.com/'
	webbrowser.open_new_tab(url)
	
	cv2.namedWindow('Frame')
	cv2.namedWindow('Settings')
	cv2.createTrackbar('Euclid Distance','Settings',49,300,changeEuclidDistance) #trackbar name, window name. value, count, onchange
	cv2.createTrackbar('CntArea Hand', 'Settings', 10616, 50000, changeContourArea)
	cv2.createTrackbar('Brightness', 'Settings',0,100,changeBrightnessFake)
	cv2.createTrackbar('CntArea Horizontal Hand','Settings',3100,12000, changeAreaHorizontalHand)
	cv2.createTrackbar('SkinNo','Settings',34000,200000, changeSkinNo) ## change so we can set at which point 
	cv2.createTrackbar('2H SkinNo', 'Settings',100000,500000,change2HSkinNo)
	
	cap = cv2.VideoCapture(0)
	modeOfModesList = []

	while(cap.isOpened()): 
		numberCounterForThisList = []
		ret,frame = cap.read()
		if ret == True:
			initialFrameCounter+=1
			initialFrameCounter%= 2
			if initialFrameCounter == 0:

				frame = cv2.flip(frame,1)
				hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
				valBrightness = cv2.getTrackbarPos('Brightness','Settings')
				if valBrightness != 0:
					hsv = changeBrightness(valBrightness, hsv)
				mask = cv2.inRange(hsv,np.array([2,50,50]), np.array([15,255,255]))
				mask = cv2.GaussianBlur(mask,(15,15),0)
				xo,contours,hierachy = cv2.findContours(mask,2,1)
				## Check if any more skin has appeared
				numberOfSkinPixels = countSkinPixels(mask)
				valSkinNo = cv2.getTrackbarPos('SkinNo','Settings')

				maskCol = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
				numberCounterForThisFrame = 0
				for c in contours: 
					#questionTwoHands = False
					x,y,w,h = cv2.boundingRect(c)
					# define region of interest
					continueOnwards = False
					if leftToRightBool == False:
						if x < 250:
							continueOnwards = True
					elif leftToRightBool == True:
						continueOnwards = True
					if continueOnwards:

						if numberOfSkinPixels > valSkinNo:
							TwoHNo = cv2.getTrackbarPos('2H SkinNo', 'Settings')
							if numberOfSkinPixels > TwoHNo: ## TODO: change this alter
								questionTwoHands = True
							else:
								questionTwoHands = False
								if h > w: ## Check for hand!
									if w/h < 1/2:
										## then the hand is vertical but sideways on 
										checkHorizontalhand(c,maskCol,x,y,w,h)

									else:
										numberCounterForThisFrame = checkHandUp(c, maskCol,x,y,w,h, numberCounterForThisFrame)
										if numberCounterForThisFrame != 0:
											numberCounterForThisList.insert(0,numberCounterForThisFrame)
								elif (w > h): ## Check for horizontal hand
									checkHorizontalhand(c,maskCol,x,y,w,h)
						else:
							cv2.putText(maskCol,"No hand detected!", (0,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,255,155),2,cv2.LINE_AA)

					if questionTwoHands == True:

						checkForTwoHands(c,maskCol)
						if h>w:
							if w/h > 1/2:
								numberCounterForThisFrame = checkHandUp(c, maskCol,x,y,w,h,numberCounterForThisFrame)
								if numberCounterForThisFrame != 0:
									numberCounterForThisList.insert(0, numberCounterForThisFrame)

						
						


				dups1 = removeDups(handYLocation)
				analyseLocationList(dups1)


				if len(numberCounterForThisList) != 0:
					mode = findMode(numberCounterForThisList)
					if len(modeOfModesList) < 30: ## what s this? Don't get here often
						modeOfModesList.insert(0,mode)

					


				cv2.imshow('Frame', maskCol)
				if cv2.waitKey(25) & 0xFF == ord('q'):
					break
		else:
			break
	cap.release()
	modeOfModes = findMode(modeOfModesList)
	#print(handYLocation)
	dups = removeDups(handYLocation)
	
	'''
	print(handYLocation.count("LL"))
	print(handYLocation.count("LH"))
	print(handYLocation.count("HL"))
	print(handYLocation.count("HH"))
	'''
	printInfo(dups)
	


def checkHandUp(c, maskCol,x,y,w,h, returnN):
	global questionTwoHands
	global currentCommand
	area = cv2.contourArea(c)
	cntArea = cv2.getTrackbarPos('CntArea Hand','Settings')
	if area > cntArea:
		cv2.drawContours(maskCol,[c],0,(100,50,140),3)
		hull=cv2.convexHull(c, returnPoints=False)
		rect = w*h
		if (rect > 11000): ## don't really understand what this is.
			cv2.rectangle(maskCol,(x,y),(x+w,y+h),(0,255,0),2)
			defects=cv2.convexityDefects(c,hull)

			for i in range(defects.shape[0]):
			    s,e,f,d = defects[i,0]
			    start = tuple(c[s][0])
			    end = tuple(c[e][0])
			    far = tuple(c[f][0])
			    cv2.line(maskCol,start,end,[0,255,0],5)
			    cv2.circle(maskCol,far,5,[0,0,255],-1)
			    euclidDist = cv2.getTrackbarPos('Euclid Distance','Settings')

			    if(dist.euclidean(start,far) > euclidDist): # if change distance away then this will have to change as well!
			    	cv2.line(maskCol,start,far,[200,20,0],5)
			    	returnN += 1
			    	## Q: need the fingersCounted if statement?
		str1 = "Fingers detected: " + str(returnN)
		strFullHand = "Five fingers detected: FULL HAND"
		strStart = "No fingers detected: STARTING"
		if ((returnN == 5 or returnN == 4)):
			cv2.putText(maskCol,strFullHand, (0,475), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,255,155),2,cv2.LINE_AA)
			successfullFunction("fullHand")

		elif (returnN == 0):
			cv2.putText(maskCol, strStart, (0,475), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,255,155),2,cv2.LINE_AA)
			successfullFunction("start")

		else:
			cv2.putText(maskCol,str1, (0,475), cv2.FONT_HERSHEY_SIMPLEX, 1, (200,255,155),2,cv2.LINE_AA)

		

	return returnN

	'''#area  = cv2.contourArea(c)
	cntArea = cv2.getTrackbarPos('ContourArea','Frame')
	if area > cntArea:
		cv2.drawContours(maskCol,[c],0,(100,50,140),3)
		hull = cv2.convexHull(c,returnPoints=False)
		x,y,w,h = cv2.boundingRect(c)
		rect = w*h
		if rect > 11000:
			cv2.rectangle(maskCol,(x,y),(x+w,y+h),(0,255,0),2)
			## INSERT DEFECTS ETC 

'''
def checkHorizontalhand(c,maskCol,x,y,w,h):
	global handYLocationCount
	global handYLocation
	area = cv2.contourArea(c)
	cntAreaHori = cv2.getTrackbarPos('CntArea Horizontal Hand', 'Settings')
	if area > cntAreaHori:
		cv2.drawContours(maskCol, [c],0,(100,50,140),3)
		cv2.rectangle(maskCol,(x,y),(x+w,y+h),(0,255,0),2)
		## Check whether is vertical or horizontal:
		position = ""
		if h < w:
			position = locateLowOrHighVertical(x,y) # This means along the vertical axis, so the hand moving up or down,
		else:
			position = locateLowOrHighHorizontal(x,y) # Along horizontal axis, hand moving side to side
		if handYLocationCount == 10 and position != "":
			lenPos = len(position)
			if len(handYLocation) >= 2:
				if len(handYLocation[-1]) == lenPos and len(handYLocation[-2]) == lenPos:
					handYLocation.append(position)
				else: handYLocationCount -+ 1
			else:
				handYLocation.append(position)
		else:
			handYLocationCount+= 1





def locateLowOrHighVertical(x,y):
	frameWidth = 500
	position = "Unknown"
	if y < frameWidth/4:
		position = "HH"
	elif y >= frameWidth/4 and y < frameWidth/2:
		position = "HL"
	elif y >= frameWidth/2 and y < (frameWidth * 3/4):
		position = "LH"
	elif y >= (frameWidth * 3/4) and y < frameWidth:
		position = "LL"
	return position


def locateLowOrHighHorizontal(x,y): 
	frameWidth = 500
	position = "Unknown"
	if x < frameWidth/4:
		position = "LHSLHS"
	elif x >= frameWidth/4 and x < frameWidth/2:
		position = "LHSRHS"
	elif x >= frameWidth/2 and x < (frameWidth * 3/4):
		position = "RHSLHS"
	elif x >= (frameWidth * 3/4) and x < frameWidth:
		position = "RHSRHS"
	return position    

def countSkinPixels(image):
	num = cv2.countNonZero(image)
	return num

def changeBrightness(value, img):
	mask = (255-img) < value
	img2 = np.where((255 - img) < value,255,img-value)	
	return img2

def removeDups(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def findMode(searchList):
	data = Counter (searchList)
	try:
		return data.most_common(1)[0][0]
	except(e):
		print(e)

#deciphers call and makes the command, then clears everything
def successfullFunction(functionCall):
	global currentCommand
	global modeOfModesList
	global numberCounterForThisList
	global handYLocationCount
	global handYLocation

	## Check for hand up, five fingers
	if functionCall == "fullHand":
		print("ZOOM IN")
		currentCommand="fullHand"
		# add_key : 0xBB
		pressOnce(0xBB)

	elif functionCall == "start":
		print("ZOOM OUT")
		currentCommand = "start"
		# -: 0xBD
		pressOnce(0xBD)


	elif functionCall == "rising":
		print("GO UP")
		pressOnce(0x26)
		releaseKey(0x26)
		# up arrow: 0x26
		currentCommand = "rising"

	elif functionCall == "falling":
		print("GO DOWN")
		# down arrow: 0x28
		pressOnce(0x28)
		releaseKey(0x26)
		currentCommand = "falling"

	elif functionCall == "leftToRight":
		print("leftToRight")
		pressOnce(0x27)
		#right arrow: 0x27
		#right shift: 0xA1
		currentCommand = "leftToRight"

	elif functionCall == "rightToLeft":
		print("rightToLeft")
		pressOnce(0x25)
		#left arrow:0x25
		#left shift: 0xA0
		currentCommand = "rightToLeft"

	handYLocationCount = 0
	handYLocation = []
	modeOfModesList = []
	numberCounterForThisList = []

def pressOnce(*args):
	print(args)

	for i in args:
		win32api.keybd_event(i,0,0,0)
		time.sleep(.05)

def releaseKey(*args):
	'''
	release depressed keys, accepts as many arguments I want
	'''
	for i in args:
		win32api.keybd_event(i,0,win32con.KEYEVENTF_KEYUP)
		time.sleep(0.04)

def analyseLocationList(dups):
	# print(dups)
	global currentCommand
	global leftToRightBool

	if len(dups) == 4:
	## Move hand up or down
		if dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HL" and dups[3] == "HH":
			successfullFunction("rising")
			
		elif dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LH" and dups[3] == "LL":
			successfullFunction("falling")

		## Move hand side to side
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSLHS" and dups[3] == "RHSRHS":
			successfullFunction("leftToRight")
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSRHS" and dups[3] == "LHSLHS":
			successfullFunction("rightToLeft")

	elif len(dups) == 3:

		## FOR SOUND UP
		if dups[0] == "LH" and dups[1] == "HL" and dups[2] == "HH":
			successfullFunction("rising")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HL":
			successfullFunction("rising")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HH":
			successfullFunction("rising")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HH":
			successfullFunction("rising")

		## FOR SOUND DOWN  
		if dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LH":
			successfullFunction("falling")
		elif dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LL":
			successfullFunction("falling")
		elif dups[0] == "HH" and dups[1] == "LH" and dups[2] == "LL":
			successfullFunction("falling")
		elif dups[0] == "HL" and dups[1] == "LH" and dups[2] == "LL":
			successfullFunction("falling")

		## FOR LEFT TO RIGHT
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSLHS":
			successfullFunction("leftToRight")
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSRHS":
			successfullFunction("leftToRight")
		elif dups[0] == "LHSLHS" and dups[1] == "RHSLHS" and dups[2] == "RHSRHS":
			successfullFunction("leftToRight")
		elif dups[0] == "LHSRHS" and dups[1] == "RHSLHS" and dups[2] == "RHSRHS":
			successfullFunction("leftToRight")

		## FOR RIGHT TO LEFT
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSRHS":
			successfullFunction("rightToLeft")
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSLHS":
			successfullFunction("rightToLeft")
		elif dups[0] == "RHSRHS" and dups[1] == "LHSRHS" and dups[2] == "LHSLHS":
			successfullFunction("rightToLeft")
		elif dups[0] == "RHSLHS" and dups[1] == "LHSRHS" and dups[2] == "LHSLHS":
			successfullFunction("rightToLeft")
	elif len(dups) == 2:
		if dups[0] == "LHSLHS" and dups[1] == "LHSRHS":
			leftToRightBool = True





def printInfo(dups):
	print("After removing duplicates our order is: ")
	if len(dups) == 4:
		## Move hand up or down
		if dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HL" and dups[3] == "HH":
			print("Turning the sound up")
		elif dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LH" and dups[3] == "LL":
			print("Turning the sound down")

		## Move hand side to side
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSLHS" and dups[3] == "RHSRHS":
			print("Hand moving left to right")
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSRHS" and dups[3] == "LHSLHS":
			print("Hand moving right to left")

	elif len(dups) == 3:

		## FOR SOUND UP
		if dups[0] == "LH" and dups[1] == "HL" and dups[2] == "HH":
			print("Still turning the sound up, missing LL")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HL":
			print("Still turning the sound up, missing HH")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HH":
			print("Still turning the sound up, missing HL")
		elif dups[0] == "LL" and dups[1] == "LH" and dups[2] == "HH":
			print("Still turning the sound up, missing HL")

		## FOR SOUND DOWN  
		if dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LH":
			print("Still turning the sound down, missing LL")
		elif dups[0] == "HH" and dups[1] == "HL" and dups[2] == "LL":
			print("Still turning the sound down, missing LH")
		elif dups[0] == "HH" and dups[1] == "LH" and dups[2] == "LL":
			print("Still turning the sound down, missing HL")
		elif dups[0] == "HL" and dups[1] == "LH" and dups[2] == "LL":
			print("Still turning the sound down, missing HH")

		## FOR LEFT TO RIGHT
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSLHS":
			print("Moving left to right, missing RHSRHS")
		elif dups[0] == "LHSLHS" and dups[1] == "LHSRHS" and dups[2] == "RHSRHS":
			print("Moving left to right, missing RHSLHS")
		elif dups[0] == "LHSLHS" and dups[1] == "RHSLHS" and dups[2] == "RHSRHS":
			print("Moving left to right, missing LHSRHS")
		elif dups[0] == "LHSRHS" and dups[1] == "RHSLHS" and dups[2] == "RHSRHS":
			print("Moving left to right, missing LHSLHS")

		## FOR RIGHT TO LEFT
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSRHS":
			print("Moving right to left, missing LHSLHS")
		elif dups[0] == "RHSRHS" and dups[1] == "RHSLHS" and dups[2] == "LHSLHS":
			print("Moving right to let, missing LHSRHS")
		elif dups[0] == "RHSRHS" and dups[1] == "LHSRHS" and dups[2] == "LHSLHS":
			print("Moving right to left, missing RHSLHS")
		elif dups[0] == "RHSLHS" and dups[1] == "LHSRHS" and dups[2] == "LHSLHS":
			print("Moving right to let, missing RHSRHS")


def checkForTwoHands(c,maskCol):
	x,y,w,h = cv2.boundingRect(c)
	cv2.putText(maskCol,"Two hands!", (350,475), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,255,155),2,cv2.LINE_AA)



def changeAreaHorizontalHand(number):
	pass

def changeEuclidDistance(number):
	pass

def changeContourArea(number):
	pass

def changeBrightnessFake(number):
	pass

def changeSkinNo(number):
	pass

def change2HSkinNo(number):
	pass

if __name__ == '__main__':
	main()