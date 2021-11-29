import PIL
from PIL import Image
import numpy as np 
import streamlit as st 
import requests
import json
from Recipe_API.utils import *
from Recipe_API.keys import *
from Emission_computing.emission_preprocessing import *
from Edamam_api import *
import nltk
from nltk.stem import WordNetLemmatizer 
import base64

nltk.download('wordnet')

# Function to Read and Convert Images
def load_resize_image(img):
    im = Image.open(img)
    # image = im.resize((224,224)) 
    image = np.array(im)
    return image

url = "https://fritz-carbon-calc-y3qsfujzsq-uc.a.run.app/predict"
# url="http://127.0.0.1:8000/predict"

# CACHE :Loading the model
response = requests.get(url).json()

# Title
st.markdown("""
    # 🥙 FRITZ

    ## The first Meal Carbon Footprint Calculator powered by Deep Learning
""")
st.markdown("""Did you know that you **save more water** by **not eating** a steak than you would by **not showering** for **one month** ?""")

# Uploading the Image to the Page
uploadFile = st.file_uploader(label="🥘Upload image", type=['jpg', 'png'])

# Checking the Format of the page
if uploadFile is not None:
    
    # To send to API
    img = load_resize_image(uploadFile)
    image_coded = img.astype('uint8')
    height, width, channel = img.shape 
    img_reshape = image_coded.reshape(height*width*channel)
    img_enc = base64.b64encode(img_reshape)
    
    #Print image
    st.image(img)

    # st.write(img)
    st.write("📸 Image Uploaded Successfully !")
    st.write("🧠Wait a minute, FRITZ is identifying the recipe")

    # Reshape the image
    # X = img.reshape(img.shape[0]*img.shape[1]*img.shape[2])
    # X=X.tolist()
    # X_json=json.dumps(X)
    
    # Call the POST
    data={"image_reshape":img_enc.decode('utf8').replace("'", '"'),
                     "height": height,
                     "width": width,
                     "color": channel}
    headers = {'Content-type': 'application/json'}
    response = requests.post(url,json.dumps(data),headers=headers).json()
    st.write(response)
    response = response.replace("_", " ")
    st.write(f"FRITZ thinks the recipe is a **{response}**")
    
    st.write("🦑FRITZ is finding the ingredients")
    # st.write(getingredients(response))


    # Try packaging
    output_dict=getingredients(response)
    output_df=fill_empties(output_dict)
    st.write(fill_empties(output_dict))
    final_df, missing_ingredients=match_ingredients(output_df)
    st.write(final_df, missing_ingredients)
    st.write(convert(final_df))
    final_result=convert(final_df)["calculated gCO2e"].sum()
    st.write(f"1 portion of this {response} emits {final_result} grams of C02")

else:
    st.write("Make sure you image is in JPG/PNG Format.")
    



