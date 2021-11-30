import PIL
from PIL import Image
import numpy as np
import streamlit as st
import json
from Recipe_API.utils import *
from Recipe_API.keys import *
from Emission_computing.emission_preprocessing import *
from Edamam_api import *
import nltk
from nltk.stem import WordNetLemmatizer
import base64
from tensorflow import keras,image
from tensorflow.image import resize
nltk.download('wordnet')

st.set_page_config(
            page_title="fritz", # => Quick reference - Streamlit
            page_icon="🥑",
            layout="wide", # wide
            initial_sidebar_state="auto") # collapsed
#--------------------------------------------
# I. GETTING MODELS AND CLASSES
#--------------------------------------------
@st.cache(allow_output_mutation=True)
def get_model():
    model = keras.models.load_model('models/100_84_DN121_TL3_GAP.h5')
    return model

def load_classes(classes_path,index):
    classes=pd.read_csv(classes_path)
    return classes.iloc[index,0]

# Loading the model when the user opens the website
model_path="models/100_84_DN121_TL3_GAP.h5"
classes_path= 'models/100_84_DN121_TL3_GAP.csv'
model=get_model()

#--------------------------------------------
# II. Read and Convert Images
#--------------------------------------------
def load_resize_image(img):
    im = Image.open(img)
    # image = im.resize((224,224))
    image = np.array(im)
    return image


#--------------------------------------------
# III. FRONT END TITLE
#--------------------------------------------
image = Image.open('Recipe_API/fritz.png')

col1,col2 = st.columns([1,3])
col1.image(image,width=250)

#--------------------------------------------
# IV. IMAGE UPLOAD
#--------------------------------------------

uploadFile = col2.file_uploader(label="🥘Upload image", type=['JPEG', 'PNG','JPG'])

col2.markdown("<h1 style='font-family: Trebuchet MS; font-size:25px; text-align: center; color: #2E3333;\
    '>Did you know that you save more water by not eating a steak\
    than you would by not showering for one month?🤔</h1>",
    unsafe_allow_html=True)
if uploadFile is not None:

    img = load_resize_image(uploadFile)
    response_reshape = resize(img,[224, 224])

    #--------------------------------------------
    # V. MODEL PREDICTION
    #--------------------------------------------
    # Getting the output
    probabilities=model.predict(np.array([response_reshape/255]))

    ## output = 100 probabilities for each class = [0.45,0.56,0.44 etc.]
    index=np.argmax(probabilities)

    ## Recipe result = the most probable output
    recipe = load_classes(classes_path,index)

    #--------------------------------------------
    # VI. FRONT END DESIGN OF THE LOADING
    #--------------------------------------------
    #Print image
    #st.image(img)
    col3, col4 = st.columns(2)
    col3.image(img, width=400)
    col4.markdown("<h1 style='font-family: Trebuchet MS;font-size:20px; text-align: center; color: #2E3333;\
    '>📸 Image Uploaded Successfully!</h1>",
    unsafe_allow_html=True)
    #st.write("🧠Wait a minute, FRITZ is identifying the recipe")

    recipe = recipe.replace("_", " ")
    #col4.write(f"FRITZ thinks the recipe is a **{recipe}**")
    col4.markdown(f"<h1 style='font-family: Trebuchet MS;font-size:20px; text-align: center; color: #2E3333;\
    '>FRITZ thinks the recipe is...</h1>", unsafe_allow_html=True)
    col4.markdown(f"<h1 style='font-family: Trebuchet MS;font-size:25px; text-align: center; color: #5ea69f;\
    '>{recipe}</h1>", unsafe_allow_html=True)

    #st.write("🦑FRITZ is finding the ingredients")

    #--------------------------------------------
    # VII. DATA ENGINEERING
    #--------------------------------------------
    ## Filling the NaNs
    output_dict=getingredients(recipe)
    output_df=fill_empties(output_dict)
    #st.write(fill_empties(output_dict))

    ## Matching the ingredients with final_ingredients_emissions.csv
    final_df, missing_ingredients=match_ingredients(output_df)
    #st.write(final_df)
    #st.write(missing_ingredients)
    #st.write(final_df, missing_ingredients)


    ## Computing the final emissions
    #st.write(convert(final_df))
    final_result=round(convert(final_df)["calculated gCO2e"].sum())
    #col4.write(f"1 portion of this {recipe} emits {final_result} grams of C02")
    col4.markdown(f"<h1 style='font-family: Trebuchet MS;font-size:30px; text-align: center; color: #2E3333;\
    '>1 portion of this {recipe} emits {final_result} grams of C02</h1>", unsafe_allow_html=True)

    ## Equivalents
    miles_per_Kg = round(final_result*0.001*(296/116),2)
    heating_per_Kg = round(final_result*0.001*(29/116),2)
    showers_per_Kg = round((final_result*0.001*(18/116)),2)
    stream_hrs_kg= round(final_result*0.001*(1/float(55/1000)),2)
    # Columns
    col5, col6, col7,col8 = st.columns(4)
    col5.metric("Miles driven 🚗", miles_per_Kg, "-$1.25")
    col6.metric("Heating 🔥", heating_per_Kg, "0.46%")
    col7.metric("Showers 🛁 ", showers_per_Kg, "+4.87%")
    col8.metric("Netflix 📺 ", stream_hrs_kg, "+4.87%")

# If the image does not work
else:
    st.write("Make sure you image is in JPEG/JPG/PNG Format.")
