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
    im = im.convert('RGB')
    image = np.array(im)
    return image


#--------------------------------------------
# III. FRONT END TITLE
#--------------------------------------------
st.markdown("""
    # 🥙 FRITZ

    ## The first Meal Carbon Footprint Calculator powered by Deep Learning
""")
# Anecdote 
st.markdown("""Did you know that you **save more water** by **not eating** a steak than you would by **not showering** for **one month** ?""")

#--------------------------------------------
# IV. IMAGE UPLOAD
#--------------------------------------------
uploadFile = st.file_uploader(label="🥘Upload image", type=['JPEG', 'PNG','JPG'])

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
    
    # Getting the class
    recipe = load_classes(classes_path,index)


    recipe = recipe.replace("_", " ")
    st.write(f"FRITZ thinks the recipe is a **{recipe}**")

    st.write("🦑FRITZ is finding the ingredients")

    #--------------------------------------------
    # VII. DATA ENGINEERING
    #--------------------------------------------
    ## Converting the output to a df 
    output_dict=getingredients(recipe)
    output_df=pd.DataFrame(output_dict)
    st.write(output_df)
    
    ## Matching the ingredients with final_ingredients_emissions.csv
    final_df, missing_ingredients=match_ingredients(output_df)
    st.write(final_df)
    st.write(missing_ingredients)
    # st.write(final_df, missing_ingredients)
    
    
    ## Computing the final emissions
    st.write(convert(final_df))
    final_result=round(convert(final_df)["calculated gCO2e"].sum())
    st.write(f"1 portion of this {recipe} emits {final_result} grams of C02")

    miles_per_Kg = round(final_result*0.001*(296/116),2)
    heating_per_Kg = round(final_result*0.001*(29/116),2)
    showers_per_Kg = round((final_result*0.001*(18/116)),2)
    stream_hrs_kg= round(final_result*0.001*(1/float(55/1000)),2)
    
    # Columns
    col1, col2, col3,col4 = st.columns(4)
    col1.metric("🚗Miles driven", miles_per_Kg, "-$1.25")
    col2.metric("Heating", heating_per_Kg, "0.46%")
    col3.metric("Showers", showers_per_Kg, "+4.87%")
    col4.metric("Netflix", stream_hrs_kg, "+4.87%")
    
    # SUGGESTIONS
    st.markdown(f"""
    ## 🍽 How to cut the carbon footprint of your {recipe} ?
    """)
    ## Veggie suggestion
    if output_df[output_df['foodCategory']=="meats"].size>0:
        # st.write("there is meat")
        st.markdown(f"""
        ## 🍃 Moving to a vegetarian {recipe}
        """)
        




else:
    st.write("Make sure you image is in JPEG/JPG/PNG Format.")
