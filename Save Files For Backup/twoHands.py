import cv2
import numpy as np 


def main():
	cap = cv2.VideoCapture(0)
	while(cap.isOpened()):
		ret,frame = cap.read()
		if ret == True:
			frame = cv2.flip(frame,1)
			hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
			mask = cv2.inRange(hsv,np.array([2,50,50]), np.array([15,255,255]))
			mask = cv2.GaussianBlur(mask,(15,15),0)
			xo,contours,hierachy = cv2.findContours(mask,2,1)

			cv2.imshow('Frame', mask)
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
		else:
			break
	cap.release()
	




if __name__ == '__main__':
	main()