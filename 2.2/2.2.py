import cv2
import numpy as np
import statistics
from matplotlib import pyplot as plt

# Reading the images
img1=cv2.imread('left.png',cv2.IMREAD_COLOR)
img2=cv2.imread('right.png',cv2.IMREAD_COLOR)
bike=cv2.imread('bike.png',cv2.IMREAD_COLOR) 

# Converting images to grayscale
gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
bike_gray=cv2.cvtColor(bike,cv2.COLOR_BGR2GRAY)

# Generating depth map
stereo = cv2.StereoBM_create(numDisparities=0, blockSize=5)
depth_map = stereo.compute(gray1,gray2)
plt.imshow(depth_map,'gray')
plt.show()

# Finding the bike in left image using template matching
res=cv2.matchTemplate(gray1,bike_gray,cv2.TM_SQDIFF_NORMED)
min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)


# tl stores the coordinate from where we will scan 
# We bring tl to middle of bike as we want to have accurate reading
top_left=min_loc
bottom_right=(int(top_left[0]+bike_gray.shape[1]),int(top_left[1]+bike_gray.shape[0]))
tl=(top_left[0],top_left[1]+int(0.6*(bottom_right[1]-top_left[1])))

img1_temp=img1.copy()

#Showing the bike found in img1
cv2.rectangle(img1_temp,top_left,bottom_right,(255,255,255),1)
cv2.imshow("img1 bike found",img1_temp.astype(np.uint8))

# Finding the bike in right image using template matching
res=cv2.matchTemplate(gray2,bike_gray,cv2.TM_SQDIFF_NORMED)
min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)

# tl2 stores the coordinate from where we will scan 
# We bring tl2 to middle of bike as we want to have accurate reading
top_left2=min_loc
bottom_right2=(int(top_left[0]+bike_gray.shape[1]),int(top_left[1]+bike_gray.shape[0]))
tl2=(top_left2[0],top_left2[1]+int(0.6*(bottom_right2[1]-top_left2[1])))

img2_temp=img2.copy()

cv2.rectangle(img2_temp,top_left2,bottom_right2,(255,255,255),1)
cv2.imshow("img2 bike found",img2_temp.astype(np.uint8))

sum=list()
min=10000
sad=0 # sum of absolute difference

pr=5 # The range in which we check in order to find corresponding pixels

# Calculating distance from camera
for i in range(tl[0],bottom_right[0]):
    for j in range(tl2[0],bottom_right2[0]):
        img1[tl[1],i]=[0,255,0]
        for r in range(2*pr+1):
            sad+=abs(int(gray1[tl[1],i-pr+r])-int(gray2[tl[1],j-pr+r]))
        if sad<min:
            min=sad
            pos=j
        sad=0
    min=10000
    sum.append(abs(pos-i))

''' Distance=f*(distance between cameras)/disparity
    fx=focal length
    disparity = difference in corresponding pixels in stereo images

    p_left on solving using QR normalization= [[640 0 640]  [[1 0 0 2]
                                               [0 480 480]   [0 1 0 -0.25]
                                               [0   0   1]]  [0 0 1 0.25]]

    p_right on solving using QR normalization= [[640 0 640]  [[1 0 0 2]
                                               [0 480 480]   [0 1 0 0.25]
                                               [0   0   1]]  [0 0 1 0.25]]

    therefore distance between cameras = 0.25-(-0.25)= 0.5m
    Since difference is in y direction fy=480
    Therefore fy*distance = 240 

'''

disparity=statistics.mode(sum)
print("The distance of the bike is "+str(240/disparity)+" in m")

cv2.imshow("img1 area scanned",img1.astype(np.uint8))

cv2.waitKey(0)
cv2.destroyAllWindows





