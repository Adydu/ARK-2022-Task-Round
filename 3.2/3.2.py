import cv2
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

def drawof(img1,u,v,w): # This function draws the optical flow on the image
    # Looping through the image
    for h in range(int((w-1)/2),img1.shape[0]-int((w-1)/2),w):
        for k in range(int((w-1)/2),img1.shape[1]-int((w-1)/2),w):
            if(abs(u[h,k])+abs(v[h,k])<0.8): # If the optical flow is small we dont draw it to avoid noise
                continue
            # We add the u array to k because we defined u as the change in positive x direction which corresponds to columns
            img1=cv2.arrowedLine(img1,(k,h),(int(k+u[h,k]),int(h+v[h,k])),(0,0,255),1)
    return img1

def findopticalflow(img1,img2,w,gauss):
    first_image=list()
    second_image=list()
    first_image.append(img1)
    second_image.append(img2)
    # Creating gaussian pyramid
    for i in range(1,gauss):
        first_image.append(cv2.pyrDown(first_image[i-1]))
        second_image.append(cv2.pyrDown(second_image[i-1]))
    # Calculating optical flow of last image
    u,v=opticalflow(first_image[gauss-1],second_image[gauss-1],w)
    for i in range(gauss-1,0,-1):
        # Interpolating u and v for new u and v
        shape=(2*u.shape[0],2*u.shape[1])
        u_new=np.full(shape,0).astype(np.float64)
        v_new=np.full(shape,0).astype(np.float64)
        for k in range(u_new.shape[0]):
            for l in range(u_new.shape[1]):
                if(k%2!=0 or l%2!=0):
                    continue
                u_new[k,l]=2*u[k//2,l//2]
                v_new[k,l]=2*v[k//2,l//2]
        u=u_new
        v=v_new
        # Applying u and v to image and then finding new optical flow
        warped=first_image[i-1].copy()
        for h in range(warped.shape[0]):
            for k in range(warped.shape[1]):
                if(u[h][k]==0 and v[h][k]==0):
                    continue
                if((h+v[h][k]>=warped.shape[0] or h+v[h][k]<0) or (k+u[h][k]>=warped.shape[1] or k+u[h][k]<0)):
                    continue
                warped[int(h+v[h][k])][int(k+u[h][k])]=first_image[i-1][h][k]
        u_corr,v_corr=opticalflow(warped,second_image[i-1],w)
        # Adding corrected optical flow to original guesses
        u=u+u_corr
        v=v+v_corr
    return u,v

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

w=5 # The window size, according to this we will search around a point in a window of size w

img1=cv2.imread('1.png',cv2.IMREAD_COLOR)
img2=cv2.imread('2.png',cv2.IMREAD_COLOR)

gray1=cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)
gray2=cv2.cvtColor(img2,cv2.COLOR_RGB2GRAY)

gaussian=3 # The no of layers in the gaussian pyramid

u,v=findopticalflow(gray1,gray2,w,gaussian) # Finds u and v
of=drawof(img1,u,v,w) # Draws optical flow on image

cv2.imshow("new",of.astype(np.uint8)) # Shows first image with optical flow drawn
cv2.imshow("img2",img2) # Shows second image

cv2.waitKey(0)
cv2.destroyAllWindows