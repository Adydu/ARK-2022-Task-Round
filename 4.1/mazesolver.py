import cv2
import numpy as np

def remove_blob_bfs(img,point):
    visited=np.full(img.shape,0) # array to store whether we have visited a point or not
    queue=list() # our queue for bfs application
    queue.append(point) # appends point to queue
    while(len(queue)!=0):
        point=queue.pop(0) # popping point from queue
        for i in range(-1,2):
            for j in range(-1,2):
                if((point[0]+i>=img.shape[0] or point[0]+i<0) or (point[1]+j>=img.shape[1] or point[1]+j<0)): # Checking if it doesnt breach boundaries
                    continue
                if((i+j)%2==0): # So that we only have neigbours 
                    continue
                # If our point belongs to red blob we add it to queue and make it white to remove it
                if((img[point[0]+i][point[1]+j]<30 and img[point[0]+i][point[1]+j]>20) and visited[point[0]+i][point[1]+j]!=1):
                    queue.append((point[0]+i,point[1]+j))
                    visited[point[0]+i][point[1]+j]=1 # We have visited the point so we make it 1
                    img[point[0]+i][point[1]+j]=255
    return img # Returning img with removed blob
    

def maze_solve_bfs(img):
    visited=np.full(img.shape,0) # array to store whether we have visited a point or not
    parent=[[0 for i in range(img.shape[1])] for i in range(img.shape[0])] # Array to store parent of point
    queue=list() # Queue to implement bfs
    i,j,flag=0,0,0
    # Loop to find start point
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if(img[i][j]>140 and img[i][j]<160): # If point is green
                flag=1
                break
        if(flag==1):
            break
    start=(i,j) # We store start point
    queue.append(start) # We append start point to queue 
    flag=0 # To store whether we found end point or not
    while len(queue)!=0 and flag!=1:
        point=queue.pop(0) # Popping fist element of list
        for i in range(-1,2):
            for j in range(-1,2):
                if((i+j)%2==0): # Checking for only neighbours
                    continue
                if((point[0]+i>=img.shape[0] or point[0]+i<0) or (point[1]+j>=img.shape[1] or point[1]+j<0)): # Checking if it doesnt breach boundaries
                    continue
                # If point is white and it is not visited
                if(img[point[0]+i][point[1]+j]!=0 and visited[point[0]+i][point[1]+j]!=1):
                    queue.append((point[0]+i,point[1]+j))
                    visited[point[0]+i][point[1]+j]=1
                    parent[point[0]+i][point[1]+j]=(point[0],point[1])
                # If point is red we can end
                if(img[point[0]+i][point[1]+j]<30 and img[point[0]+i][point[1]+j]>20):
                    end=(point[0]+i,point[1]+j)
                    flag=1
                    break
            if(flag==1):
                break
    path=list() # This will store the path
    point=end 
    while(point!=start): # Loop that append point and then its parent to path
        path.append(point)
        point=parent[point[0]][point[1]]
    # As path would be reversed, we reverse it to find path from start point. It wont matter in this program but might come handy for some other application
    path.reverse()
    return path


img=cv2.imread('maze.png',cv2.IMREAD_COLOR) # Reading img

gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

path=maze_solve_bfs(gray) # Calling function first to solve for first end point
# Adding path to img
for a in range(len(path)): 
    img[path[a][0]][path[a][1]]=(255,0,0)

new_gray=remove_blob_bfs(gray,path[-1]) # Removing first end blob

path=maze_solve_bfs(new_gray) # Calling function to solve the second end point
# Adding path to img
for a in range(len(path)): 
    img[path[a][0]][path[a][1]]=(255,0,0)

cv2.imshow('maze',img.astype(np.uint8))

cv2.waitKey(0)
cv2.destroyAllWindows
