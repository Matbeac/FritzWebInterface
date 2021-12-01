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
import streamlit.components.v1 as components
# from parse_menu import get_text,parse_menu

nltk.download('wordnet')

st.set_page_config(
            page_title="FRITZ",
            page_icon="🥑",
            layout="wide")
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
    im = im.convert('RGB')
    image = np.array(im)
    return image


#--------------------------------------------
# III. FRONT END TITLE
#--------------------------------------------
image = Image.open('Recipe_API/fritz.png')

col1,col2 = st.columns([1,3])
col1.image(image,width=250)
selection = st.radio('Choose', ('Dish', 'Menu'))

#--------------------------------------------
# IV. IMAGE UPLOAD
#--------------------------------------------
if selection == 'Dish':
    uploadFile = col2.file_uploader(label="Upload image 🌭 ⬇️ ", type=['JPEG', 'PNG','JPG'])

    with col2:

        st.markdown("""
            <h1 style='font-family: Trebuchet MS; font-size:25px;
            text-align: center; color: #2E3333;
            '>Did you know that you save more water by not eating a steak
            than you would by not showering for one month?🤔</h1>
            """,
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
        col3, col4 = st.columns([1,2])
        with col3:
            st.image(img, use_column_width=True)

            st.markdown("<h1 style='font-family: Trebuchet MS;font-size:20px; text-align: center; color: #2E3333;\
                        '>📸 Image Uploaded Successfully!</h1>",
                        unsafe_allow_html=True)

        recipe = recipe.replace("_", " ")

        with col4:
            st.write(" ")
            st.write(" ")
            st.markdown(f"""<h1 style='font-family: Trebuchet MS;font-size:20px;
                        text-align: center; color:#2E3333;
        '               >FRITZ thinks the recipe is...</h1>""",
                        unsafe_allow_html=True)
            st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:25px;
                        text-align: center; color:#5ea69f;
                        '>{recipe}</h1>
                        """,
                        unsafe_allow_html=True)

        #st.write("🦑FRITZ is finding the ingredients")

        #--------------------------------------------
        # VII. DATA ENGINEERING
        #--------------------------------------------
        ## Converting the output to a df
        output_dict=getingredients(recipe)
        output_df=pd.DataFrame(output_dict)
        #st.write(output_df)
        ## Matching the ingredients with final_ingredients_emissions.csv
        final_df, missing_ingredients=match_ingredients(output_df)
        #st.write(final_df)
        #st.write(missing_ingredients)
        #st.write(final_df, missing_ingredients)


        ## Computing the final emissions
        #st.write(convert(final_df))
        final_result=round(convert(final_df)["calculated gCO2e"].sum())
        #col4.write(f"1 portion of this {recipe} emits {final_result} grams of C02")
        with col4:
            components.html(
                f"""
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                A portion of this {recipe} emits
                <span style="color: #5ea69f; font-size:30px">{final_result}</span>
                grams of C02
                </p>"""
            )

        ## Equivalents

        miles_per_Kg = round(final_result*0.001*(296/116),2)
        heating_per_Kg = round(final_result*0.001*(29/116),2)
        showers_per_Kg = round((final_result*0.001*(18/116)),2)
        stream_hrs_kg= round(final_result*0.001*(1/float(55/1000)),2)

        # Columns
        st.write(" ")
        col5 = st.columns(5)
        col5[1].metric("Miles driven 🚗", miles_per_Kg, "-1.25")
        col5[2].metric("Heating 🔥", heating_per_Kg, "0.46%")
        col5[3].metric("Showers 🛁 ", showers_per_Kg, "+4.87%")
        col5[4].metric("Netflix 📺 ", stream_hrs_kg, "+4.87%")


        # SUGGESTIONS
        st.markdown(f"""
            <h1 style='font-family: Trebuchet MS;
            font-size:20px; text-align:
            center; color:#2E3333;
            '>🍽 How to cut the carbon footprint of your {recipe}?</h1>
            """,
            unsafe_allow_html=True)

        ## Veggie suggestion
        if output_df[output_df['foodCategory']=="meats"].size>0:
            # st.write("there is meat")
            st.markdown(f"""
            ## 🍃 Moving to a meat substitute could cut the emissions of your meal by up to 90%!
            """)
        if output_df[output_df['ingredient']=="cream"].size>0:
            # st.write("there is milk")
            st.markdown(f"""
            ## 🐮 Moving to an oat milk from cow's milk could cut it's emission contribution by up to 80%!
            """)
        if output_df[output_df['ingredient']=="butter"].size>0:
            # st.write("there is milk")
            st.markdown(f"""
            ## 🐄 Moving to a plant based spread from butter could cut it's emission contribution by 2/3!
            """)



        # wrong prediction?
        st.write(" ")
        st.write(" ")
        col6 = st.columns(5)
        if col6[2].button('wrong dish?'):
            col6[2].write('Top 3 predictions')

    else:
        #st.write("Make sure you image is in JPEG/JPG/PNG Format.")
        st.write(" ")


 #-------------------------------------------#
 #  MENU OPTION                              #
 #-------------------------------------------#

elif selection == 'Menu':
    uploadFile = col2.file_uploader(label="Upload image 🌭 ⬇️ ", type=['JPEG', 'PNG','JPG'])

    with col2:

        st.markdown("""
            <h1 style='font-family: Trebuchet MS; font-size:25px;
            text-align: center; color: #2E3333;
            '>Did you know that you save more water by not eating a steak
            than you would by not showering for one month?🤔</h1>
            """,
            unsafe_allow_html=True)

    if uploadFile is not None:
        menu_image=uploadFile
        menu_text=get_text(menu_image)
        
        #--------------------------------------------
        # VI. DISPLAY THE MOST ECOLOGICAL RECIPE
        #--------------------------------------------
        df_result=parse_menu(menu_text)
        emission=df_result[df_result['emission']==df_result['emission'].min()].iloc[0,0]
        recipe_result=df_result[df_result['emission']==df_result['emission'].min()].index[0]
        # st.write(f'The most ecological recipe is {recipe_result}, with a carbon footprint of {emission} g/C02 emitted per kg')

        #--------------------------------------------
        # VI. FRONT END DESIGN OF THE LOADING
        #--------------------------------------------
        #Print image
        #st.image(img)
        col3, col4 = st.columns([1,2])
        with col3:
            st.image(menu_image, use_column_width=True)

            st.markdown("<h1 style='font-family: Trebuchet MS;font-size:20px; text-align: center; color: #2E3333;\
                        '>📸 Menu Uploaded Successfully!</h1>",
                        unsafe_allow_html=True)

        with col4:
            st.write(" ")
            st.write(" ")
            st.markdown(f"""<h1 style='font-family: Trebuchet MS;font-size:20px;
                        text-align: center; color:#2E3333;
        '               >FRITZ thinks the most ecological recipe of this restaurant is...</h1>""",
                        unsafe_allow_html=True)
            st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:25px;
                        text-align: center; color:#5ea69f;
                        '>{recipe_result}, with a carbon footprint of {emission} g/C02 emitted per kg')</h1>
                        """,
                        unsafe_allow_html=True)
            st.markdown(""" Ranking of the most ecological recipes of the restaurant:""")
            st.write(df_result.rename(columns={'emission': 'Emission (g/CO2 per kg)'}, index={'ingredient_parsed': 'Dish'}))






#else:
    #st.write("Make sure your image is in JPEG/JPG/PNG Format!!")
