import pandas as pd
import streamlit as st
import plotly.express as px
import os
import json
from streamlit_option_menu import option_menu
from PIL import Image
import cv2
import os
import re
import easyocr # (Optical Character Recognition)
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
from base64 import b64encode, b64decode
import base64
from io import BytesIO



# os.environ['KMP_DUPLICATE_LIB_OK']='True'



icon = Image.open(r"./logo.png")

st.set_page_config(page_title= "BizCardX",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded"
                   )


st.sidebar.header("**BizCardX**")
#mysql://avnadmin:AVNS_s_HdHvArnDqdjRnwycG@mysql-c357b62-shubhangiborse-715c.a.aivencloud.com:16467/defaultdb?ssl-mode=REQUIRED
connection_string = "mysql+mysqlconnector://root:borse123@127.0.0.1:3306/ocr"
# connection_string = "mysql+mysqlconnector://avnadmin:AVNS_s_HdHvArnDqdjRnwycG@mysql-c357b62-shubhangiborse-715c.a.aivencloud.com:16467/defaultdb"

engine = create_engine(connection_string, echo=True)
with engine.connect() as connection:
    result = connection.execute(text('''CREATE TABLE IF NOT EXISTS vcard
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    company_name TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(11),
                    image LONGBLOB)'''))
    

conn = st.connection(
    "local_db",
    type="sql",
    url=connection_string
)






reader = easyocr.Reader(['en'])

with st.sidebar:
    selected = option_menu("Menu", ["Home","BizCardX", "Update","About Me"], 
                icons=["house","bar-chart-line", "exclamation-circle"],
                menu_icon= "menu-button-wide",
                default_index=0,
                styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#b0c8ef"},
                        "nav-link-selected": {"background-color": "#16a535"}})
    

# MENU 1 - HOME
if selected == "Home":
    st.image("./logo.png", "BizCardX", width=300)

    st.markdown("# BizCardX: Extracting Business Card Data with OCR]")
    st.markdown("## Technologies : OCR,streamlit GUI, SQL,Data Extraction")
    
# MENU 1.A - HOME:About me
if selected == "About Me":
    st.image("./logo.png", "BizCardX", width=300)

    st.markdown("# Dr. Shubhangi Borse")
    st.markdown("## Research Analyst")
    st.markdown("[![LinkedIn](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/dr-shubhangi-borse-48990565/)") 
    st.markdown("[![Github](https://img.icons8.com/material-outlined/48/000000/github.png)](https://github.com/shubhangiborse)") 
    st.markdown("[![Medium](https://static-00.iconduck.com/assets.00/medium-icon-256x256-sszkhuhr.png)](https://medium.com/@drshubhangi)") 
    

if selected == "BizCardX":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join("cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer()) 
                
        st.image(uploaded_card)
        #save card  
        save_card(uploaded_card)
        
        def image_preview(image,res): 
            RGB_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            for (bbox, text, prob) in res: 
              # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                
                cv2.rectangle(RGB_img, tl, br, (0, 255, 0), 2)
                # cv2.putText(RGB_img, text, (tl[0], tl[1] - 10),
                # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(RGB_img)
        
        
        
        
        #easy OCR
        saved_img = os.getcwd()+ "/cards/"+ uploaded_card.name
        result = reader.readtext(saved_img)
        
        
        # DISPLAYING THE UPLOADED CARD
        with st.spinner("Processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                image = cv2.imread(saved_img)
                st.markdown("## Data Extracted")
                st.pyplot(image_preview(image,result)) 
        
             
                
            
        
        
        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
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
                "pin_code" : [],
                "image" : img_to_binary(saved_img)
               }

        def get_data(res):
            for ind,(bbox,i, p)  in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4][1] +"." + res[5][1]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) ==2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pin_code"].append(i[10:])
        get_data(result)
        
        
        df = pd.DataFrame(data)
        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                #here %S means string values 
                img = b64encode(data["image"])
                with engine.connect() as connection:
                    connection.execute(text(f'''INSERT INTO vcard (card_holder, designation,mobile_number, email, company_name, website, area, city, state, pin_code, image) VALUES ('{data['card_holder'][0]}', '{data['designation'][0]}', '{data['mobile_number'][0]}', '{data['email'][0]}', '{data['company_name'][0]}', '{data['website'][0]}', '{data['area'][0]}', '{data['city'][0]}', '{data['state'][0]}', '{data['pin_code'][0]}', "{img}");'''))

                    connection.commit()

                
            st.success("#### Uploaded to database successfully!")
   
if selected == "Update":

    st.markdown("## Update or Delete")
  
    df = conn.query("SELECT card_holder FROM vcard", ttl=1)
    names = []
    for index, row in df.iterrows():
        names.append(row[0])
        
    selected_card = st.selectbox("Select a card holder name to update", names)
    st.markdown("#### Update or modify any data below")
    df = conn.query(f"SELECT company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code, image from vcard WHERE card_holder='{selected_card}' LIMIT 1", ttl=1)

    if selected_card is not None:
        
        for index, row in df.iterrows():
            result = row
            
        col1, col2 = st.columns(2)
        # with col1:
            
        #     # img = b64decode(result[10])
            
            
        #     # st.image(img)


        #     st.header("A cat")
            
        # with col2:
        
        
            
        # DISPLAYING ALL THE INFORMATIONS
        company_name = st.text_input("Company Name", result[0])
        card_holder = st.text_input("Card Holder Name", result[1])
        designation = st.text_input("Designation", result[2])
        mobile_number = st.text_input("Mobile Number", result[3])
        email = st.text_input("Email", result[4])
        website = st.text_input("Website", result[5])
        area = st.text_input("Area", result[6])
        city = st.text_input("City", result[7])
        state = st.text_input("State", result[8])
        pin_code = st.text_input("Pin Code", result[9])

    if st.button("SAVE to MySQL"):
        with engine.connect() as connection:
                connection.execute(text(f"UPDATE vcard SET company_name='{company_name}',card_holder='{card_holder}',designation='{designation}',mobile_number='{mobile_number}',email='{email}',website='{website}',area='{area}',city='{city}',state='{state}',pin_code='{pin_code}' WHERE card_holder='{card_holder}'"))

                connection.commit()
        
        st.success("Information updated in database successfully.")


    if st.button("Delete the Entry"):
        with engine.connect() as connection:
                connection.execute(text(f"DELETE FROM vcard WHERE card_holder='{selected_card}'"))

                connection.commit()
        
        st.success("Business card information deleted from database.")

   