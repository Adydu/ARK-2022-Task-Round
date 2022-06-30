#!/usr/bin/env python3
from ast import Continue
from part1_checker import noDuplicates
import rospy
import std_msgs
from std_msgs.msg import Int64
import numpy as np
import os
import random

pub = rospy.Publisher('/guess_part2', Int64, queue_size=100)

def xCallback(data):
    global x
    x = data.data

def generateNo(k): # Function to generate no from list 
    a=0
    for i in range(len(k)):
        a=10*a+k[i]
    return a

def randomNumberGenerator(): # Function that takes dollar array and creates next guess to try
    global dollars_array,posd,digits
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


def strategy():
    global x,dollars_array,posd,digits
    msg = Int64()
    flag=0
    rate=rospy.Rate(1)
    while(x!=999):
        if(digits==10):
            ''' Since dollar= X-10 for digits=10 we can use same strategy as in part 1'''
            # Generating guess according to dollars found and finding no of dollars
            guess=randomNumberGenerator()
            msg.data=generateNo(guess)
            pub.publish(msg)
            rate.sleep()
            dollar1=x-10 # dollar1 stores no of dollars of guess
            if(x==999):
                return
            if(dollar1==0 or dollar1==1): # We wont check if no of dollars is 0 or 1 as it wastes iterations
                continue
            a=0
            # Switching up digits
            for i in range(9):
                if(len(dollars_array)!=0): # If we have no dollars yet then we should use the general switching process to find dollars else we assign i as first non zero dollar
                    if(dollars_array[0]!=0):
                        i=posd[0]
                    else:
                        posd[1]
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
                    if(x==999):
                        return
                    dollar2=x-10
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
        if(digits<10):
            ''' Strategy:- First we replace each digit with another digit in order to find initial dollars(flag=0 part)
            Once we find some dollars we move into the second part(flag=0) 
            Here we generate random digit and by replacing it with another dollar we check if it is cent or not
            Dependng on whether it is cent or not we replace it with other digits in the number to find dollars '''
            # Generating guess and finding x
            rate.sleep()
            guess=randomNumberGenerator()
            msg.data=generateNo(guess)
            pub.publish(msg)
            rate.sleep()
            ori_x=x
            if(ori_x==999):
                return
            # It will enter this if there is dollar in dollars array
            if(flag==1):
                # Choosing random digit
                if(digits==9 and 0 not in guess):
                    t=0
                    flag2=1
                else:
                    t=random.choice(list(set([x for x in range(1,10)])-set(guess)))
                # Replacing a dollar with the digit to check whether it is cent or not
                guess2=guess.copy()
                guess2[posd[-1]]=t
                msg.data=generateNo(guess2)
                pub.publish(msg)
                rate.sleep()
                new_x=x
                if(new_x==999):
                   return
                # If new_x - ori_x==-2 it means that digit is not cent
                if(new_x-ori_x==-2):
                    iscent=0
                # Else it means that digit is cent
                else:
                    iscent=1
                guess2=guess.copy()
                # We replace digits of number with t and use the differences in x to find dollars
                for i in range(len(guess2)):
                    if(flag2==1): # If t is 0 then we have 0 skip first one
                        flag2=0
                        continue
                    guess2=guess.copy()
                    if(i in posd): # If i is posd then we skip
                        continue
                    # Generating new no and finding x
                    guess2[i]=t
                    msg.data=generateNo(guess2)
                    pub.publish(msg)
                    rate.sleep()
                    new_x=x
                    if(new_x==999):
                        return
                    # If diff is 2 then it means digit at pos i in original no is dollar
                    if(ori_x-new_x==2):
                        dollars_array.append(guess[i])
                        posd.append(i)
                    # If diff is -2 then it means digit at pos i in new no is dollar
                    if(ori_x-new_x==-2):
                        dollars_array.append(guess2[i])
                        posd.append(i)
                    # If diff is 1 and digit is cent then digit in original no is dollar
                    if(ori_x-new_x==1 and iscent==1):
                        dollars_array.append(guess[i])
                        posd.append(i)
            # It will enter this if there is no dollar in dollars array yet
            if(flag==0):
                flag2=0
                # Choosing random digit
                if(digits==9 and 0 not in guess):
                    t=0
                    flag2=1
                else:
                    t=random.choice(list(set([x for x in range(1,10)])-set(guess)))
                for i in range(len(guess)):
                    if(flag2==1): # If t=0 then we will ahev to skip first iteration
                        flag2=0
                        continue
                    # Creating new number by replacing digits with t and finding new_x
                    guess2=guess.copy()
                    guess2[i]=t
                    msg.data=generateNo(guess2)
                    pub.publish(msg)
                    rate.sleep()
                    new_x=x
                    if(new_x==999):
                        return
                    # If diff is 2 then that means digit at pos i in original no is dollar
                    if(ori_x-new_x==2):
                        dollars_array.append(guess[i])
                        posd.append(i)
                    # If diff is -2 then that means digit at pos i in new no is dollar
                    if(ori_x-new_x==-2):
                        dollars_array.append(guess2[i])
                        posd.append(i)
                if(len(dollars_array)!=0):
                    flag=1
                        


def play():
    global x,dollars_array,posd,digits
    x=0
    dollars_array=[]
    posd=[]
    digits = rospy.get_param("/centsdollars2/digits")
    rospy.init_node('player2')
    rospy.Subscriber("/check2", Int64, xCallback)
    while not rospy.is_shutdown():
        strategy()
        break

if __name__ == '__main__':
    try:
        play()
    except rospy.ROSInterruptException:
        pass