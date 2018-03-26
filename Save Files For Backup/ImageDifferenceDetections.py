import cv2
import numpy as np 
import time 
def main():
	frame1 = []
	counterForFrames = 0
	cam = cv2.VideoCapture(0)
	while(cam.isOpened()):
		ret, img = cam.read()
		if ret == True:
			if len(frame1)== 0:
				counterForFrames = counterForFrames+1
				print(counterForFrames)

			img = cv2.flip(img, 1)
			hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(hsv,np.array([2,50,50]), np.array([15,255,255]))
			mask = cv2.GaussianBlur(mask,(15,15),0)
			xo,contours,hierachy = cv2.findContours(mask,2,1)
			print(len(frame1) == 0,counterForFrames > 30,(len(frame1) == 0 and counterForFrames > 30))
			if (len(frame1) == 0 and counterForFrames > 30):
				print('here')
				frame1 = mask
			cv2.imshow('Frame',mask)
			if (len(frame1)!=0):

				cv2.imshow('Orig', frame1)
				aminusb = cv2.subtract(mask, frame1)
				cv2.imshow('Difference', aminusb)
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
		else:
			break
	cam.release()


if __name__ == '__main__':
	main()