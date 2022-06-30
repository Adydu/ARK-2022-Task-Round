import cv2
from cv2 import THRESH_BINARY
from matplotlib.pyplot import contour 
import cv2.aruco as aruco
import numpy as np

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Function that detects squarish contours
def detectSquare(contours):
    k=list()
    for i in range(len(contours)):
        # approxpolyDP approxiamtes the contour to minimumn no of points
        a=cv2.approxPolyDP(contours[i],0.1*cv2.arcLength(contours[i],True),True)

        if(len(a)!=4 or cv2.isContourConvex(a)!=True):
            continue
        if(cv2.contourArea(a)<100):
            continue
        k.append(a)
    return k

#Function that detects contours
def detectAruco(img1,contours):
    new_contour=list()
    for contour in contours:
        new=[[0,200],[0,0],[200,0],[200,200]]
        # Transforming perspective of squarish contours
        mat=cv2.getPerspectiveTransform(np.float32(contour),np.float32(new))
        result=cv2.warpPerspective(img1,mat,(200,200))
        result=cv2.cvtColor(result,cv2.COLOR_RGB2GRAY)
        _,result=cv2.threshold(result,0,255,cv2.THRESH_OTSU)
        # Dividing result into 8 by 8 grid and checking if it is aruco
        k2=[]
        for i in range(9):
            k2.append(i*result.shape[0]//8)
        flag=0
        c1=0
        c2=0
        for i in range(8):
            for j in range(8):
                a=(k2[i]+k2[i+1])//2
                b=(k2[j]+k2[j+1])//2
                temp=result[a-5:a+5,b-5:b+5]
                if(temp.mean()>=240): # If bit is white
                    c1+=1
                if(temp.mean()<=10): # If bit is black
                    c2+=1
        # If sum not = 64 then it is not aruco | c1 and c2 condition to check if it is not simply blank
        if((c1+c2)!=64 or c1<=10 or c2<=10):
            flag=1
        if(flag==0):
            new_contour.append(contour)
            #Showing detected aruco
            cv2.imshow("Detected aruco",result.astype(np.uint8))   
        return new_contour
       
img1=cv2.imread("img1.png",cv2.IMREAD_COLOR)
shape=img1.shape
print(shape)

img1=cv2.resize(img1,(int(img1.shape[1]/2),int(img1.shape[0]/2))) # Resizing image

# Converting image to grayscale
gray1=cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)

#Doing adaptive threshold and then reversing the image
gray1=cv2.adaptiveThreshold(gray1,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,17,7)
gray1=255-gray1

# Detecting Arucos
contours, hierarchy = cv2.findContours(gray1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
contours=detectSquare(contours)
contours=detectAruco(img1,contours)

# Drawing detected arucos
cv2.drawContours(img1, contours, -1, (0, 255, 0), 1)

# Showing image
cv2.imshow("img1",img1.astype(np.uint8))
cv2.waitKey(0)
cv2.destroyAllWindows

