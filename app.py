import PIL
from PIL import Image
import numpy as np 
import streamlit as st 
import requests
import json
from Recipe_API.utils import *
from Emission_computing.emission_preprocessing import *
from Edamam_api import *

# Function to Read and Convert Images
def load_image(img):
    im = Image.open(img)
    image = np.array(im)
    return image

# Uploading the Image to the Page
uploadFile = st.file_uploader(label="Upload image", type=['jpg', 'png'])

# Checking the Format of the page
if uploadFile is not None:
    # Perform  Manipulations 
    img = load_image(uploadFile)
    st.image(img)
    # st.write(img)
    st.write("📸 Image Uploaded Successfully !")
    
    # Reshape the image
    X = img.reshape(img.shape[0]*img.shape[1]*img.shape[2])
    X=X.tolist()
    X_json=json.dumps(X)
    # Call the POST
    url = "http://127.0.0.1:8000/predict/"
    
    data=json.dumps({"image_reshape":X_json,
                     "height": img.shape[0],
                     "width": img.shape[1],
                     "color": img.shape[2]})
    
    headers = {'Content-type': 'application/json'}
    response = requests.post(url,data,headers=headers).json()
    response = response.replace("_", " ")
    st.write(f"FRITZ thinks the recipe is a {response}")
    st.write("FRITZ is finding the ingredients")
    st.write(getingredients(response))


    # Try packaging
    output_dict=getingredients(response)
    output_df=fill_empties(output_dict)
    st.write(fill_empties(output_dict))
    final_df, missing_ingredients=match_ingredients(output_df)
    st.write(final_df, missing_ingredients)
    st.write(convert(final_df))
else:
    st.write("Make sure you image is in JPG/PNG Format.")
    



