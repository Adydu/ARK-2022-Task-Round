import cv2
import numpy as np
from scipy import signal

def drawof(img1,u,v,w): # This function draws the optical flow on the image
    # Looping through the image
    for h in range(int((w-1)/2),img1.shape[0]-int((w-1)/2),w):
        for k in range(int((w-1)/2),img1.shape[1]-int((w-1)/2),w):
            if(abs(u[h,k])+abs(v[h,k])<0.5): # If the optical flow is small we dont draw it to avoid noise
                continue
            # We add the u array to k because we defined u as the change in positive x direction which corresponds to columns
            img1=cv2.arrowedLine(img1,(k,h),(int(k+u[h,k]),int(h+v[h,k])),(0,0,255),1)
    return img1

def opticalflow(img1,img2,w):
    t=0.01 # A parameter to be used later
    kernel_x=np.array([[-0.125,0,0.125],[-0.25,0,0.25],[-0.125,0,0.125]]) # Sobel filter to find x derivative
    kernel_y=np.array([[-0.125,-0.25,-0.125],[0,0,0],[0.125,0.25,0.125]]) # Sobel filter to find y derivative
    # Normalizing the images
    img1=img1/255
    img2=img2/255
    # Finding fx, fy and ft
    Ix = signal.convolve2d(img1, kernel_x, boundary='symm')
    Iy = signal.convolve2d(img1, kernel_y, boundary='symm')
    It=img2-img1
    # To be used later
    shape=img1.shape
    # u and v store the corresponding optical flow
    u=np.full(shape,0).astype(np.float64)
    v=np.full(shape,0).astype(np.float64)
    # Looping through image
    for h in range(w//2, shape[0] - w//2,w):
        for k in range(w//2, shape[1] - w//2,w):
            # Getting Ix Iy and It values of window surrounding point
            Ix_window = Ix[h - w//2 : h + w//2 + 1, k- w//2 : k + w//2 + 1,].flatten()
            Iy_window = Iy[h - w//2 : h + w//2 + 1,k - w//2 : k + w//2 + 1,].flatten()
            It_window = It[h - w//2 : h + w//2 + 1,k - w//2 : k + w//2 + 1,].flatten()
            # Getting array A and b
            A = np.asarray([Ix_window, Iy_window]).reshape(-1, 2)
            b = np.asarray(It_window)
            # Getting A transpose A
            ATA = np.transpose(A) @ A
            eig, _ = np.linalg.eig(ATA)
            # Noise thresholding
            if eig[0] < t or eig[1]<t:
                continue
            # Getting soln
            ATAI = np.linalg.pinv(ATA)
            sol = ATAI @ np.transpose(A) @ b
            #Storing soln
            u[h, k], v[h, k] = sol[0],sol[1]

    return u,v

cap=cv2.VideoCapture("Vid_Sample1.mp4")

w=5
flag=0
c=-1

video=1 # If video sample 1 is used then put 1 else put 2

while True:
    ret,frame=cap.read()
    if(ret==False):
        break
    frame=cv2.resize(frame,(400,400)) # Resizing frame for faster and better optical flow estimation
    c+=1 # This is used if video sample 1 is used
    if(video==1): # Since there is practically no difference in frames in video sample 1 this is used
        if(c%15!=0):
            continue
    if flag==0: # Used to set prev_frame
        flag=1
        prev_frame=frame
        gray_prev=cv2.cvtColor(prev_frame,cv2.COLOR_RGB2GRAY)
        cv2.imshow("video",frame)
        continue
    # Converting frame to grayscale
    gray_now=cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    # Optical flow is calculated between prev frame and now
    u,v=opticalflow(gray_prev,gray_now,w)
    prev_frame=drawof(prev_frame,u,v,w)
    # Showing optical flow
    cv2.imshow("video",prev_frame.astype(np.uint8))
    gray_prev=gray_now
    prev_frame=frame
    if cv2.waitKey(100) & 0xFF==ord('q'): # If q is pressed
        break
    
cap.release()
cv2.destroyAllWindows

