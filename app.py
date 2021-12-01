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
image = Image.open('Recipe_API/fritz.png')

col1,col2 = st.columns([1,3])
col1.image(image,width=250)
selection = st.radio('Choose', ('Dish', 'Menu'))


#--------------------------------------------
# IV. IMAGE UPLOAD
#--------------------------------------------
if selection == 'Dish':
    with col1:
        portion = st.slider('Select number of portions', 1, 8, 1)
    with col2:

        # st.markdown("""
        #     <h1 style='font-family: Trebuchet MS; font-size: 15px;
        #     text-align: center; color: #2E3333; padding-left: 200px;
        #     padding-right: 200px;padding-bottom: 40px;
        #     '>Did you know that you save more water by not eating a steak
        #     than you would by not showering for one month?🤔</h1>
        #     """,
        #     unsafe_allow_html=True)

        uploadFile = col2.file_uploader(label="Upload image 🌭 ⬇️ ", type=['JPEG', 'PNG','JPG'])
        st.markdown(
                f"""
                    <style>
                        .sidebar .sidebar-content {{
                            width: 375px;
                        }}
                    </style>
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
        col3, col4 = st.columns([0.5,2])
        with col3:
            st.image(img, use_column_width=True)
            st.markdown("""<h1 style='font-family: Trebuchet MS;font-size:20px;
                        text-align: center; color: #2E3333;
                        '>📸 Image Uploaded Successfully!</h1>""",
                        unsafe_allow_html=True)

        recipe = recipe.replace("_", " ")

        with col4:
            st.markdown(f"""<h1 style='font-family: Trebuchet MS;
                        font-size:20px;
                        text-align: center; color:#2E3333;
        '               >FRITZ thinks the recipe is...</h1>""",
                        unsafe_allow_html=True)
            st.markdown(f"""
                        <h1 style='font-family: Trebuchet MS;font-size:25px;
                        text-align: center; color:#5ea69f;
                        '>{recipe}</h1>
                        """,
                        unsafe_allow_html=True)

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
        final_result=round(convert(final_df)["calculated gCO2e"].sum())*(1/1000)
        #col4.write(f"1 portion of this {recipe} emits {final_result} grams of C02")
        with col4:
            components.html(
                f"""
                <p style="font-weight:bold;
                text-align: center;
                font-family: Trebuchet MS;
                font-size:25px; color:#2E3333;">
                {portion} portion(s) of this {recipe} emits
                <span style="color: #5ea69f; font-size:30px">{final_result*portion}</span>
                Kg/C02
                </p>"""
            )

        ## Equivalents

        miles_per_Kg = round(final_result*(296/116)*portion,2)
        heating_per_Kg = round(final_result*(29/116)*portion,2)
        showers_per_Kg = round((final_result*(18/116)*portion),2)
        stream_hrs_kg= round(final_result*(1/float(55/1000))*portion,2)

        # Columns
        st.write(" ")
        col5 = st.columns(5)
        col5[1].metric("Miles driven 🚗", miles_per_Kg)
        col5[2].metric("House heating 🔥", heating_per_Kg)
        col5[3].metric("Long Showers 🛁 ", showers_per_Kg)
        col5[4].metric("Hours streaming Netflix 📺 ", stream_hrs_kg)


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
            # if col8[1].button('🍽 Do you want to know how cut the carbon footprint of your meal?'):
                st.markdown(f"""
                #### 🍃 Moving to a meat substitute could cut the emissions of your meal by up to 90%!
                """)

        if output_df[output_df['foodCategory']=="Poultry"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)
            st.markdown(f"""<div style="text-align: center"> 🍃 Moving to a meat substitute could cut the emissions of your meal by up to 60%! </div>,
                        unsafe_allow_html=True""")
        if output_df[output_df['ingredient']=="cream"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)
            st.markdown(f"""
            ## 🐮 Moving to an oat milk from cow's milk could cut it's emission contribution by up to 80%!
            """)
        if output_df[output_df['ingredient']=="butter"].size>0:
            st.markdown(x,
            unsafe_allow_html=True)
            st.markdown(f"""
            ## 🐄 Moving to a plant based spread from butter could cut it's emission contribution by 2/3!
            """)

        # wrong prediction?
        st.write(" ")
        col6 = st.columns(5)
        if col6[2].button('wrong dish?'):
            extra_recipes = [load_classes(classes_path, i) for i in reversed(np.argsort(probabilities)[::-1][:2][0][-3:-1])]
            recipes = []
            for _ in range(len(extra_recipes)):
                recipes.append(extra_recipes[_].replace("_", " "))
            output_dict_recipe_2=getingredients(recipes[0])
            output_dict_recipe_3=getingredients(recipes[1])
            output_df_2=pd.DataFrame(output_dict_recipe_2)
            output_df_3=pd.DataFrame(output_dict_recipe_3)
            final_df_2, missing_ingredients_2=match_ingredients(output_df_2)
            final_df_3, missing_ingredients_2=match_ingredients(output_df_3)
            final_result_2=round(convert(final_df_2)["calculated gCO2e"].sum()*0.001)
            final_result_3=round(convert(final_df_3)["calculated gCO2e"].sum()*0.001)
            miles_per_Kg_2 = round(final_result_2*portion*(296/116),2)
            heating_per_Kg_2 = round(final_result_2*portion*(29/116),2)
            showers_per_Kg_3 = round((final_result_3*portion*(18/116)),2)
            stream_hrs_kg_3= round(final_result_3*portion*(1/float(55/1000)),2)

            col7 = st.columns(2)
            col7[0].markdown(
                f"""
                {portion} portion(s) of this {recipes[0]} emits {final_result_2} Kg/CO2
            """
            )
            col7[0].markdown(f"Miles driven 🚗 {miles_per_Kg_2}km")
            col7[0].metric("House heating 🔥", heating_per_Kg_2)
            col7[1].markdown(
                f"""
                {portion} portion of this {recipes[1]} emits {final_result_3} Kg/CO2
            """
            )
            col7[1].metric("Long Showers 🛁 ", showers_per_Kg_3)
            col7[1].metric("Hours streaming Netflix 📺 ", stream_hrs_kg_3)

    else:
        #st.write("Make sure you image is in JPEG/JPG/PNG Format.")
        st.write(" ")


 #-------------------------------------------#
 #  MENU OPTION                              #
 #-------------------------------------------#

elif selection == 'Menu':

    with col2:

        st.markdown("""
            <h1 style='font-family: Trebuchet MS; font-size: 15px;
            text-align: center; color: #2E3333; padding-left: 200px;
            padding-right: 200px;padding-bottom: 40px;
            '>Did you know that you save more water by not eating a steak
            than you would by not showering for one month?🤔</h1>
            """,
            unsafe_allow_html=True)

        uploadFile = col2.file_uploader(label="Upload image 🌭 ⬇️ ", type=['JPEG', 'PNG','JPG'])

    if uploadFile is not None:
        menu_image=uploadFile
        menu_text=get_text(menu_image)
        #--------------------------------------------
        # VI. DISPLAY THE MOST ECOLOGICAL RECIPE
        #--------------------------------------------
        df_result=parse_menu(menu_text)
        try:
            emission=df_result[df_result['g/CO2 emitted/kg']==df_result['g/CO2 emitted/kg'].min()].iloc[0,1]
            recipe_result=df_result[df_result['g/CO2 emitted/kg']==df_result['g/CO2 emitted/kg'].min()].iloc[0,0].capitalize()
        # st.write(f'The most ecological recipe is {recipe_result}, with a carbon footprint of {emission} g/C02 emitted per kg')

            #--------------------------------------------
            # VI. FRONT END DESIGN OF THE LOADING
            #--------------------------------------------
            #Print image
            col3, col4 = st.columns([0.5,2])
            with col3:
                st.image(menu_image, use_column_width=True)

                st.markdown("<h1 style='font-family: Trebuchet MS;font-size:20px; text-align: center; color: #2E3333;\
                            '>📸 Menu Uploaded Successfully!</h1>",
                            unsafe_allow_html=True)

            with col4:

                st.markdown(f"""<h1 style='font-family: Trebuchet MS;font-size:20px;
                            text-align: center; color:#2E3333;
            '               >FRITZ thinks the most ecological recipe of this restaurant is...</h1>""",
                            unsafe_allow_html=True)
                st.markdown(f"""
                            <h1 style='font-family: Trebuchet MS;font-size:25px;
                            text-align: center; color:#5ea69f;
                            '>{recipe_result}</h1>
                            """,
                            unsafe_allow_html=True)
                components.html(
                    f"""
                    <p style="font-weight:bold;
                    text-align: center;
                    font-family: Trebuchet MS;
                    font-size:25px; color:#2E3333;">
                    with a carbon footprint of
                    <span style="color: #5ea69f; font-size:30px">{emission}</span>
                    g/C02 emitted per kg
                    </p>"""
                )
                st.markdown(""" Ranking of the most ecological recipes of the restaurant:""")
                
                # st.bar_chart(df_result.set_index('Dish'))
                # st.bar_chart(df_result['g/CO2 emitted/kg'])
                st.dataframe(df_result.transpose())
        except:
            st.write('NOT UNDERSTOOD')
