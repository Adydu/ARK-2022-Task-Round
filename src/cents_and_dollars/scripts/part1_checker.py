#!/usr/bin/env python3
import rospy
import std_msgs
from std_msgs.msg import Int64
import numpy as np
import random
import os

pub1 = rospy.Publisher('/check1', Int64, queue_size=100,latch=True)

tries = 0

def getDigits(num):
    return [int(i) for i in str(num)]

def noDuplicates(num):
    num_li = getDigits(num)
    if len(num_li) == len(set(num_li)):
        return True
    else:
        return False
  
def generateNum(lower_bound,upper_bound):
    while True:
        num = random.randint(lower_bound,upper_bound)
        if noDuplicates(num):
            return num
  
def guessCallback(data):
    global guess,lower_bound,upper_bound,digits
    guess = data.data
    msg = Int64()
    if not noDuplicates(guess):
        msg.data = -999
        pub1.publish(msg)
        print("Please enter number without duplicates. Try again."+str(guess))
        guess = None
        return
    if guess < lower_bound or guess > upper_bound:
        msg.data = -999
        pub1.publish(msg)
        print("Enter "+str(digits)+" digit number only. Try again.")
        return


def centsdollars():
    global guess,answer,tries,lower_bound,upper_bound
    msg = Int64()
    c,b=0,0
    answer_li = getDigits(answer)
    guess_li = getDigits(guess)
    if guess == answer:
        print("You win!")
        print("The correct number is: " + str(answer)+" with tries = "+str(tries))
        msg.data = 999
        pub1.publish(msg)
    else:
        tries+=1
        for i,j in zip(answer_li,guess_li):        
            if j in answer_li:
                if j == i:
                    b += 1 
                else:
                    c += 1
        msg.data = b*10 + c
        print("You have " + str(b) + " dollars and " + str(c) + " cents for "+str(guess))
        pub1.publish(msg)
        


def check1():
    global guess,answer,tries,lower_bound,upper_bound,digits
    guess = None
    answer = None
    rospy.init_node('centsdollars1')
    digits = rospy.get_param("/centsdollars1/digits")
    lower_bound = pow(10,digits-1)
    upper_bound = pow(10,digits)-1
    rospy.Subscriber("/guess_part1", Int64, guessCallback)
    answer = generateNum(lower_bound,upper_bound)
    # rate=rospy.Rate(2)
    while not rospy.is_shutdown():
        # rate.sleep()
        if guess is not None:
            centsdollars()
            tries+=1
            guess = None




if __name__ == '__main__':
    try:
        check1()
    except rospy.ROSInterruptException:
        pass