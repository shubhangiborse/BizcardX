#import important library
import easyocr # (Optical Character Recognition)
import numpy as np
import PIL
from PIL import Image, ImageDraw
import cv2
import os
import re


reader = easyocr.Reader(['en'])

result =reader.readtext('./2.png')
print(result)



def img_to_binary(file):
    # Convert image data to binary format
    with open(file, 'rb') as file:
        binaryData = file.read()
    return binaryData

data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : []
               
               }

def get_data(res):
    website=""
    email=""
    mobile_number=""
    company_name=""
    card_holder=""
    designation=""
    area=""
    city=""
    state=""
    pin_code=""
    

    
    for ind,(bbox,i, p) in enumerate(res):

        # To get WEBSITE_URL
        if "www " in i.lower() or "www." in i.lower():
            website = i
        elif "WWW" in i:
            website = res[4][1]+"." + res[5][1]

        # To get EMAIL ID
        elif "@" in i:
            email = i

        # To get MOBILE NUMBER
        elif "-" in i:
            mobile_number = i
            if len(mobile_number) ==2:
                mobile_number = " & ".join(mobile_number)

        # To get COMPANY NAME  
        elif ind == len(res)-1:
            company_name = i

        # To get CARD HOLDER NAME
        elif ind == 0:
            card_holder = i
        # To get DESIGNATION
        elif ind == 1:
            designation = i

        # To get AREA
        if re.findall('^[0-9].+, [a-zA-Z]+',i):
            area = i.split(',')[0]
        elif re.findall('[0-9] [a-zA-Z]+',i):
            area = i

        # To get CITY NAME
        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*',i)
        if match1:
            city = match1[0]
        elif match2:
            city = match2[0]
        elif match3:
            city = match3[0]

        # To get STATE
        state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
        if state_match:
                state = i[:9]
        elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
            state = i.split()[-1]
        if len(state)== 2:
            state.pop(0)

        # To get PINCODE        
        if len(i)>=6 and i.isdigit():
            pin_code = i
        elif re.findall('[a-zA-Z]{9} +[0-9]',i):
            pin_code = i[10:]

    
    # if designation == "":
    #     name_index = card_holder.index(" ")
    #     designation = card_holder[name_index+1:]
    #     card_holder = card_holder[:name_index]
        
    # if email == "":
    #     if website.index("@")>0:
    #         email_index = website.rfind(" ")
    #         email = website[email_index+1:]
    #         website = website[:email_index]
        
    data["website"].append(website)
    data["email"].append(email)
    data["mobile_number"].append(mobile_number)
    data["company_name"].append(company_name)
    data["card_holder"].append(card_holder)
    data["designation"].append(designation)
    data["area"].append(area)
    data["city"].append(city)
    data["state"].append(state)
    data["pin_code"].append(pin_code)
    
get_data(result)

print(data)