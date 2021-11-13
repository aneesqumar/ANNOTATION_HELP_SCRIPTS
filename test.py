import cv2

cv2.namedWindow('test')
while True:
	k  = cv2.waitKey(0)
	if not k == -1: print(k)
