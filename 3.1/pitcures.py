import cv2

cam = cv2.VideoCapture(0)

img_counter = 1

calibration=0 # 1 for calibration 0 for captruing aruco marker images

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)
    k = cv2.waitKey(1)
    if k%256 == 27: # If esc is pressed we exit
        print("Escape hit, closing...")
        break
    elif k%256 == 32: # If space is pressed we exit
        if(calibration == 1):
            img_name = "cali{}.png".format(img_counter)
        else:
            img_name="opticalflow{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()