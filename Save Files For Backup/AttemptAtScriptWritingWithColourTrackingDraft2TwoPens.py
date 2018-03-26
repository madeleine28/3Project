import cv2
import numpy as np
from collections import deque
import argparse
import win32api, win32con
import time


def click(x,y):
	upOrDownCheck = win32api.GetKeyState(0x01)
	if (upOrDownCheck):
		print("it's lowered already")
		win32api.SetCursorPos((x,y))
	else:
   		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
   # time.sleep(0.05)
   # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)



   # win32api.SetCursorPos((x,y))
    ## Check if mouse is up or down
    ## If up then lower it
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    ##else just drag it to that positon


   # time.sleep(0.05)
   # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", help="path to the (optional) video file")
	ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
	args = vars(ap.parse_args())
	if not args.get("video", False):
		cam = cv2.VideoCapture(0)
	


	#lowerBound = np.array([33,80,40])
	#upperBound = np.array([102,255,255])
	#lowerBound = np.array([100,50,50]) # BLUE lowerBound
	#upperBound = np.array([130,255,255]) # BLUE upperBound
	#lowerBound = np.array([88,122,134]) # BLUE RULER lowerBound
	#upperBound = np.array([99,142,214]) # BLUE RULER upperBound
	#lowerBound = np.array([-6,92,40]) # BLUE RULER lowerBound 2
	#upperBound = np.array([14,112,120]) # BLUE RULER upperBound 2
	#lowerBound = np.array([77,166,205]) # BLUE RULER DOWNSTAIRS lowerBound 2
	#upperBound = np.array([97,186,285]) # BLUE RULER DOWNSTAIRS upperBound 2
	lowerBound = np.array([10, 208, 178]) # yellow pen lowerbound
	upperBound = np.array([30, 228, 258]) # yellow pen upperbound
	pen2lowerBound = np.array([23,117,89]) # green pen lowerbound
	pen2upperBound = np.array([43,137,169]) # green pen upperbound


	#cam = cv2.VideoCapture(0)
	pts = deque()
	pts2 = deque()
	while(cam.isOpened()):
		ret, img = cam.read()
		if ret == True: 
			img = cv2.flip(img,1)

			imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(imgHSV,lowerBound, upperBound)
			mask = cv2.erode(mask, None, iterations=2) ## Note: like these two lines!
			mask = cv2.dilate(mask, None, iterations=2) ## TRY REMOVING THIS
			greenPenMask = cv2.inRange(imgHSV,pen2lowerBound,pen2upperBound)
			greenPenMask = cv2.erode(greenPenMask, None, iterations=2) 
			greenPenMask = cv2.dilate(greenPenMask, None, iterations=2) 
			maskColours = img
			# Find contours and initalize current center
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
			center = None
			tempx,tempy = None,None
			if len(cnts) > 0:
				# find largest contour
				c = max(cnts, key=cv2.contourArea)
				# compute min. enclosing circle and centroid
				((x,y),radius) = cv2.minEnclosingCircle(c)
				M = cv2.moments(c)
				center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
				tempx,tempy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
				if radius > 10:
					cv2.circle(imgHSV, (int(x),int(y)), int(radius),(0,255,200),2)
					cv2.circle(imgHSV, center,5,(0,255,26),-1)

			pts.appendleft(center)
			if tempx != None and tempy != None:
				click(tempx, tempy)
			else:
				print('here')
				upOrDownCheck = win32api.GetKeyState(0x01)
				if (upOrDownCheck == 1):
					print("keyisdown")
					h_x,h_y = win32api.GetCursorPos()
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,h_x,h_y,0,0)

			for i in range(1,len(pts)):
				if pts[i-1] is None or pts[i] is None:
					continue
				thickness = int(np.sqrt(args["buffer"]/float(i+1)) * 2.5)
				cv2.line(imgHSV, pts[i - 1], pts[i],(0,0,255),thickness)
				cv2.line(maskColours, pts[i - 1], pts[i],(0,0,255),thickness)


			## and countours for second one
			cntsMask2 = cv2.findContours(greenPenMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
			center2 = None
			tempx2,tempy2 = None,None
			if len(cntsMask2) > 0:
				# find largest contour
				c = max(cntsMask2, key=cv2.contourArea)
				# compute min. enclosing circle and centroid
				((x,y),radius) = cv2.minEnclosingCircle(c)
				M = cv2.moments(c)
				center2 = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
				tempx2,tempy2 = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
				if radius > 10:
					cv2.circle(imgHSV, (int(x),int(y)), int(radius),(0,255,255),2)
					cv2.circle(imgHSV, center,5,(255,0,255),-1)

			
			pts2.appendleft(center2)
			if tempx2 != None and tempy2 != None:
				click(tempx2, tempy2)
			else:
				print('he2re')
				#upOrDownCheck = win32api.GetKeyState(0x01)
				#f (upOrDownCheck == 1):
				#	print("keyisdown")
				#	h_x,h_y = win32api.GetCursorPos()
				#	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,h_x,h_y,0,0)


			

				### check if its up or down
				##if its down get use
				#   h_x, h_y = win32api.GetCursorPos()
				## set cursor up


			for i in range(1,len(pts2)):
				if pts2[i-1] is None or pts2[i] is None:
					continue
				thickness = int(np.sqrt(args["buffer"]/float(i+1)) * 2.5)
				cv2.line(imgHSV, pts2[i - 1], pts2[i],(0,255,26),thickness)
				cv2.line(maskColours, pts2[i-1], pts2[i],(0,255,26), thickness)


			cv2.imshow("mask",mask)
			cv2.imshow("secondMask", greenPenMask)
			cv2.imshow("cam", imgHSV)
			#cv2.imshow("COLOURS", maskColours)
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
	cam.release()


if __name__ == '__main__':
	main()