import PIL
from PIL import Image
import numpy as np
import streamlit as st
import json
from Emission_computing.emission_preprocessing import *
from Edamam_api import *
import nltk
from nltk.stem import WordNetLemmatizer
import base64
from tensorflow import keras,image
from tensorflow.image import resize
import streamlit.components.v1 as components
from parse_menu import get_text,parse_menu

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
image = Image.open('Utils/fritz.png')

col1,col2 = st.columns([1,3])
col1.image(image,width=250)
selection = col1.radio("What image do you want to upload?", ("Food", "Restaurant menu"))

#--------------------------------------------
# IV. IMAGE UPLOAD
#--------------------------------------------
if selection == "Food":
    portion = col1.slider('Select number of portions', 1, 8, 1)
    uploadFile = col2.file_uploader(label="Upload image 🌭 ⬇️ ", type=['JPEG', 'PNG','JPG'])


    if uploadFile is not None:

        img = load_resize_image(uploadFile)
        col1.image(img, width=300)
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
        recipe = recipe.replace("_", " ")

        #--------------------------------------------
        # VII. DATA ENGINEERING & DISPLAY PREDICTION
        #--------------------------------------------
        ## Converting the output to a df

        output_dict=getingredients(recipe)
        output_df=pd.DataFrame(output_dict)
        final_df, missing_ingredients=match_ingredients(output_df)

        ## Computing the final emissions

        final_result=round(convert(final_df)["calculated gCO2e"].sum())*(1/1000)

        with col2:

            components.html(f"""
                <p style="line-height: 1.6; font-weight: normal;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                FRITZ thinks the recipe is...<br>
                <span style="color: #5ea69f; font-size:30px;">{recipe}<br></span>

                </p>
                """
            )
            components.html(f"""
                <p style="line-height: 1.6; font-weight: normal;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                {portion} portion of this {recipe} emits
                <span style="color: #5ea69f; font-size:30px;">{round(final_result*portion,1)}</span>
                kg of C02
                </p>
                """)

        ## Equivalents

        miles_per_Kg = round(final_result*(296/116)*portion,2)
        heating_per_Kg = round(final_result*(29/116)*portion,2)
        showers_per_Kg = round((final_result*(18/116)*portion),2)
        stream_hrs_kg= round(final_result*(1/float(55/1000))*portion,2)

        # Columns
        ##col5 = st.columns(6)
        with col2:
            st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:17px;
                        font-weight: normal;
                        text-align: center; color: #2E3333;
                        '>The CO2 emissions from your meal are equivalent to:
                        </h1>
                        """,
                        unsafe_allow_html=True)
            components.html(f"""
                <p style="line-height: 1.5; font-weight: normal;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:17px; color:#2E3333;">
                Driving a car for
                <span style="color: #5ea69f; font-size:23px;">{miles_per_Kg}</span>
                miles 🚗 <br>Heating a house for
                <span style="color: #5ea69f; font-size:23px;">{heating_per_Kg}</span>
                hours 🔥 <br>Showering for
                <span style="color: #5ea69f; font-size:23px;">{showers_per_Kg*8}</span>
                minutes 🛁 <br> Streaming Netflix
                <span style="color: #5ea69f; font-size:23px;">{stream_hrs_kg}</span>
                hours 📺
                </p>
                """
            )
            st.write(" ")


        # SUGGESTIONS
        ## Veggie suggestion
        x = (f"""
            <h1 style='font-family: Trebuchet MS;
            font-size:20px; text-align:
            center; color:#2E3333;
            '>🍽 How to cut the carbon footprint of your {recipe}?</h1>
            """)
        # col8 = st.columns(3)
        if output_df[output_df['foodCategory']=="meats"].size>0:

            st.markdown(x,
            unsafe_allow_html=True)
            components.html(
                """
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:20px; color:#2E3333;">
                🍃 Moving to a meat substitute could cut the emissions of your meal
                <span style="color: #5ea69f; font-size:20px">by up to 90%</span>
                </p>"""
            )
        if output_df[output_df['foodCategory']=="Poultry"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)
            components.html(
                """
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:20px; color:#2E3333;">
                🍃 Moving to a meat substitute could cut the emissions of your meal
                <span style="color: #5ea69f; font-size:20px">by up to 60%</span>
                </p>"""
            )

        if output_df[output_df['ingredient']=="cream"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)
            components.html(
                """
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:20px; color:#2E3333;">
                🐮 Moving to an oat milk from cow's milk could cut it's emission contribution
                <span style="color: #5ea69f; font-size:20px">by up to 80%</span>
                </p>"""
            )
        if output_df[output_df['ingredient']=="butter"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)

            components.html(
                """
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:20px; color:#2E3333;">
               🐄 Moving to a plant based spread from butter could cut it's on contribution
                <span style="color: #5ea69f; font-size:20px">by 2/3!%</span>
               </p>""")

    else:
        #st.write("Make sure you image is in JPEG/JPG/PNG Format.")
        st.write(" ")


 #-------------------------------------------#
 #  MENU OPTION                              #
 #-------------------------------------------#

elif selection == 'Restaurant menu':
    uploadFile = col2.file_uploader(label="Upload menu image 🧾 ⬇️ ", type=['JPEG', 'PNG','JPG'])
    if uploadFile is not None:
        menu_image=uploadFile
        col1.image(menu_image, width=400)
        menu_text=get_text(menu_image)
        #--------------------------------------------
        # VI. DISPLAY THE MOST ECOLOGICAL RECIPE
        #--------------------------------------------
        df_result=parse_menu(menu_text)
        try:
            emission=df_result[df_result['g/CO2 emitted/kg']==df_result['g/CO2 emitted/kg'].min()].iloc[0,1]
            recipe_result=df_result[df_result['g/CO2 emitted/kg']==df_result['g/CO2 emitted/kg'].min()].iloc[0,0].capitalize()
            with col2:
                components.html(f"""
                <p style="line-height: 1.6; font-weight: normal;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                FRITZ thinks the most ecological recipe of this restaurant is...<br>
                <span style="color: #5ea69f; font-size:30px;">{recipe_result}<br></span>
                </p>
                """
            )
                components.html(f"""
                <p style="line-height: 1.6; font-weight: normal;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                1 kg of this {recipe_result} emits
                <span style="color: #5ea69f; font-size:30px;">{round(emission/1000,2)}</span>
                kg of C02
                </p>
                """)
                st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:25px;
                        font-weight: normal;
                        text-align: center; color: #2E3333;
                        '>👍🏼 Recommended recipes
                        </h1>
                        """,
                        unsafe_allow_html=True)
                recipe_list=[recipe for recipe in df_result['Dish'].head(3)]
                st.markdown(f"""
                                <h1 style='font-family: Trebuchet MS;font-size:20px;
                                text-align: center; color:#5ea69f;
                                '>{recipe_list[0]}<br>{recipe_list[1]}<br>{recipe_list[2]}</h1>
                                """,
                                unsafe_allow_html=True)
                ## NON RECOMMANDED
                st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:25px;
                        font-weight: normal;
                        text-align: center; color: #2E3333;
                        '>👎🏼 Recipes to avoid
                        </h1>
                        """,
                        unsafe_allow_html=True)
                df_result=df_result.sort_values(by="g/CO2 emitted/kg",ascending=False)
                recipe_list=[recipe for recipe in df_result['Dish'].head(3)]
                st.markdown(f"""
                                <h1 style='font-family: Trebuchet MS;font-size:20px;
                                text-align: center; color:#5ea69f;
                                '>{recipe_list[0]}<br>{recipe_list[1]}<br>{recipe_list[2]}</h1>
                                """,
                                unsafe_allow_html=True)

            df_result['kg/CO2 emitted/kg'] = df_result['g/CO2 emitted/kg']/1000
            df_result.drop(columns="g/CO2 emitted/kg", inplace=True)
            df_result = df_result.sort_values(by="kg/CO2 emitted/kg", ascending=True)

            expander = st.expander("Menu breakdown")
            expander.dataframe(df_result)
        except:
            st.write('Are you sure this is a menu?')
