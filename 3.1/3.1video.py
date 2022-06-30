import cv2
import cv2.aruco as aruco
import numpy as np

cap=cv2.VideoCapture(0)

while True:
    ret,frame=cap.read()
    if(ret==False):
        break
    img1=frame
    gray1=cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)

    key=getattr(aruco,f'DICT_6X6_250')
    arucoDict=aruco.Dictionary_get(key)
    arucoParam=aruco.DetectorParameters_create()
    bbox,ids,_=aruco.detectMarkers(img1,arucoDict,parameters=arucoParam)

    bbox2=np.array(bbox,np.int32)
    if(bbox2.size==0):
        cv2.imshow("video",img1.astype(np.uint8))
        k = cv2.waitKey(1)
        if k%256 == 27:
            print("Escape hit, closing...")
            break
        continue
    aruco.drawDetectedMarkers(img1,bbox)

    position = (10,50)

    with np.load('Camera parameters.npz') as file:
        mtx,dist,rvec,tvec=[file[i] for i in ('cameraMatrix','dist','rvecs','tvecs')]

    h,  w = img1.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    new_rvec,new_tvec,_=aruco.estimatePoseSingleMarkers(bbox, 0.05, mtx,dist)

    img1=cv2.drawFrameAxes(img1,mtx,dist,new_rvec,new_tvec,0.03)

    cv2.putText(img1,"tag id={}".format(ids[0,0]),position,cv2.FONT_HERSHEY_SIMPLEX,1, (255,0,0),3) 

    cv2.imshow("video",img1.astype(np.uint8))
    
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break

cap.release()
cv2.destroyAllWindows