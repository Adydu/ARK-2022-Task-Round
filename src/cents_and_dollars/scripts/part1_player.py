#!/usr/bin/env python3
from turtle import pos
from typing import no_type_check

from pyrfc3339 import generate
from part1_checker import centsdollars, noDuplicates
import rospy
import std_msgs
from std_msgs.msg import Int64
import numpy as np
import os
import random

pub = rospy.Publisher('/guess_part1', Int64, queue_size=100,latch=True)


def dollarcentCallback(data):
    global dollarcent,dollars_array,k,dollar,cents
    dollarcent = data.data

def randomNumberGenerator(): # Function that takes dollar array and creates next guess to try
    global dollarcent,dollars_array,posd,digits
    n=digits
    number=list()
    c=0
    r=[i for i in range(digits)]
    dollars_array=[i for _,i in sorted(zip(posd,dollars_array))] # Sorting dollar array and posd array
    posd.sort()
    print("Dollars "+str(dollars_array)+" at pos "+str(posd))
    r=list(set(r)-set(posd)) # Removing posd from r
    while c!=n-len(posd): #Generating random no with digits=(actual digits)-len(dollars array)
        t=random.choice(list(set([x for x in range(0, 10)]) - set(dollars_array)-set(number)))
        c+=1
        number.append(t)
    for i in range(len(posd)): # inserting dollars in the number to create final no
        number.insert(posd[i],dollars_array[i])
    if(number[0]==0):
        number[0],number[r[1]]=number[r[1]],number[0]
    return number

def generateNo(k): # Function to generate no from list 
    a=0
    for i in range(len(k)):
        a=10*a+k[i]
    return a


def strategy():
    flag=0 # Used for 9 digits numbers later
    c=0 # Used to check no of dollars found to be used later
    global dollarcent,dollars_array,posd,digits,prev_dollar,dollar,cents # Declaring global variables
    msg = Int64()
    rate=rospy.Rate(1)
    while(dollarcent!=999):
        # For 10 digit numbers
        if(digits==10):
            ''' Strategy:- We will switch two digits in the number and see what affect it has on the no of dollars
            For the first iteration we will keep switching up digits till we find the no of dollars
            After that we will switch only with a dollar in order to find dollars
            We will repeat the above till we find the right no
            '''
            # Generating guess according to dollars found and finding no of dollars
            guess=randomNumberGenerator()
            msg.data=generateNo(guess)
            pub.publish(msg)
            rate.sleep()
            dollar1=(dollarcent-2)//9 # dollar1 stores no of dollars of guess
            if(dollarcent==999):
                return
            if(dollar1==0 or dollar1==1): # We wont check if no of dollars is 0 or 1 as it wastes iterations
                continue
            a=0
            # Switching up digits
            for i in range(9):
                if(len(dollars_array)!=0): # If we have no dollars yet then we should use the general switching process to find dollars else we assign i as first non zero dollar
                    if(dollars_array[0]!=0 and posd[0]!=0):
                        i=posd[0]
                    else:
                        i=posd[1]
                for j in range(0,10):
                    #If we have no dollars then we are applying general switching process
                    if(len(dollars_array)==0 and j<i+1): 
                        continue
                    if(len(dollars_array)>=dollar1): # If we have found our dollars then we break
                        a=1
                        break
                    if(j==i): 
                        continue
                    # Generating new no to find dollars after switching digits
                    guess2=guess.copy()
                    if(i==0 and guess2[j]==0):
                        continue
                    guess2[i],guess2[j]=guess2[j],guess2[i]
                    msg.data=generateNo(guess2)
                    pub.publish(msg)
                    rate.sleep()
                    if(dollarcent==999):
                        return
                    dollar2=(dollarcent-2)//9
                    # If dollar 1 == dollar2 we break as that means that guess[i] is not dollar(If it was there would be some change)
                    if(dollar1==dollar2):
                        break
                    # If dollar1-dollar2=2 then digits at pos i and j are dollars in original number
                    if(dollar1-dollar2==2): 
                        if(guess[i] not in dollars_array):
                            dollars_array.append(guess[i])
                            posd.append(i)
                        if(guess[j] not in dollars_array):
                            dollars_array.append(guess[j])
                            posd.append(j)
                    # If dollar1-dollar2=-2 then digits at pos i and j are dollars in new number
                    if(dollar1-dollar2==-2):
                        if(guess2[i] not in dollars_array):
                            dollars_array.append(guess2[i])
                            posd.append(i)
                        if(guess2[j] not in dollars_array):
                            dollars_array.append(guess2[j])
                            posd.append(j)
                if(a==1):
                    break
        # For numbers with digits<10
        else:
            """ Strategy:- We will find a digit t such that it is not in our guess. 
            We will then iterate through our number replacing each digit with our new digit and seeing how it changes our dollars
            According to that we will update our dollars array and generate our next guess according to it
            We will repeat this process till we find the right number
            """
            guess=randomNumberGenerator() # Using random number generator to generate next guess
            # Publsihing our guess to get no of dollars
            msg.data=generateNo(guess)
            pub.publish(msg)
            rate.sleep()
            dollar=dollarcent//10
            if(dollarcent==999):
                return
            # If no of dollars is <=prev_dollar then there is no point in continuing
            if(dollar<=prev_dollar):
                continue
            else:
                flag=0
                c=0
                # Generating digit which is not in number
                for i in range(1,10):
                    if i not in guess:
                        t=i
                        break
                if(len(guess)==9 and 0 not in guess): # If digits=9 and no 0 in number then t has to be 0
                    flag=1
                    t=0
                for i in range(len(guess)):
                    if(i in posd): # If i in posd then we skip as we already know about the corresponding dollar
                        continue
                    if(flag==1): # If flag=1 that means that t=0 which we cant place in first position so we skip
                        flag=0
                        continue
                    # Generating new number by replacing original digit with new one
                    guess2=guess.copy()
                    guess2[i]=t
                    msg.data=generateNo(guess2)
                    pub.publish(msg)
                    rate.sleep()
                    new_dollar=dollarcent//10
                    if(dollarcent==999):
                        return
                    # If new_dollar-dollar==-1 then that means digit in original number was dollar
                    if(new_dollar-dollar==-1):
                        dollars_array.append(guess[i])
                        posd.append(i)
                        c+=1
                    # If new_dollar-dollar==1 then that means digit in new number is dollar
                    if(new_dollar-dollar==1):
                        dollars_array.append(guess2[i])
                        posd.append(i)
                        c+=1
                    if(c==dollar-prev_dollar+1): # If we find the dollars we need to find we escape in order to not waste loops
                        break
            prev_dollar= len(dollars_array) # Prev dollar to check whether new guess has more dollars or not
            

def play():
    print("Started")
    global dollarcent,dollars_array,posd,digits,prev_dollar,dollar,cents
    dollar=0
    cents=0
    prev_dollar=0
    dollars_array=[]
    posd=[]
    dollarcent = 0
    digits = rospy.get_param("/centsdollars1/digits")
    rospy.init_node('player1')
    rospy.Subscriber("/check1", Int64, dollarcentCallback)
    while not rospy.is_shutdown():
        strategy()
        break

if __name__ == '__main__':
    try:
        play()
    except rospy.ROSInterruptException:
        pass