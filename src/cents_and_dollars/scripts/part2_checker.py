#!/usr/bin/env python3
import rospy
import std_msgs
from std_msgs.msg import Int64
import numpy as np
import random
import os

pub1 = rospy.Publisher('/check2', Int64, queue_size=100)

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
        print("Please enter number without duplicates. Try again."+str(guess))
        guess = None
        msg.data = -999
        pub1.publish(msg)
        return
    if guess < lower_bound or guess > upper_bound:
        msg.data = -999
        pub1.publish(msg)
        print("Enter "+str(digits)+" digit number only. Try again."+str(guess))
        return

def centsdollars():
    global guess,answer,tries,lower_bound,upper_bound
    msg = Int64()
    c,b=0,0
    answer_li = getDigits(answer)
    guess_li = getDigits(guess)
    if guess == answer:
        print("You win!")
        print("The correct number is: " + str(answer)+" with "+str(tries)+" tries ")
        msg.data = 999
        pub1.publish(msg)
    else:
        tries+=1
        for i,j in zip(answer_li,guess_li):        
            if j in answer_li:
                if j == i:
                    b += 2 
                else:
                    c += 1
        msg.data = b+ c
        print("X is "+str(b+c)+" for guess "+str(guess))
        pub1.publish(msg)
        


def check2():
    global guess,answer,tries,lower_bound,upper_bound,digits
    guess = None
    answer = None
    rospy.init_node('centsdollars2')
    rospy.Subscriber("/guess_part2", Int64, guessCallback)
    digits = rospy.get_param("/centsdollars2/digits")
    lower_bound = pow(10,digits-1)
    upper_bound = pow(10,digits)-1
    answer = generateNum(lower_bound,upper_bound)
    while not rospy.is_shutdown():
        if guess is not None:
            centsdollars()
            tries+=1
            guess = None



if __name__ == '__main__':
    try:
        check2()
    except rospy.ROSInterruptException:
        pass