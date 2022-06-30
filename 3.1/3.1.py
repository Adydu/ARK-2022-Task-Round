import cv2
import cv2.aruco as aruco
import numpy as np

# Reading and converting to grayscale
img1=cv2.imread('img2.png',cv2.IMREAD_COLOR)
gray1=cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)

#Detecting aruco marker
key=getattr(aruco,f'DICT_6X6_250')
arucoDict=aruco.Dictionary_get(key)
arucoParam=aruco.DetectorParameters_create()
bbox,ids,rejected=aruco.detectMarkers(img1,arucoDict,parameters=arucoParam)

#Drawing Aruco Marker
aruco.drawDetectedMarkers(img1,bbox)

position = (10,50)

# Loading camera parameters stored in file
with np.load('Camera parameters.npz') as file:
    mtx,dist,rvec,tvec=[file[i] for i in ('cameraMatrix','dist','rvecs','tvecs')]

h,  w = img1.shape[:2]
newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

#Estimating pose
new_rvec,new_tvec,_=aruco.estimatePoseSingleMarkers(bbox, 0.05, mtx,dist)

# Drawing axes
for i in range(len(new_rvec)):
    img1=cv2.drawFrameAxes(img1,mtx,dist,new_rvec[i],new_tvec[i],0.03)

cv2.putText(img1,"tag id={}".format(ids[0,0]),position,cv2.FONT_HERSHEY_SIMPLEX,1, (255,0,0),3) 

cv2.imshow("aruco",img1.astype(np.uint8))
cv2.waitKey(0)
cv2.destroyAllWindows