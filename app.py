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


@st.cache(allow_output_mutation=True)
def get_model():
    model = keras.models.load_model('models/100_84_DN121_TL3_GAP.h5')
    return model

def load_classes(classes_path,index):
    classes=pd.read_csv(classes_path)
    return classes.iloc[index,0]


model_path="models/100_84_DN121_TL3_GAP.h5"
classes_path= 'models/100_84_DN121_TL3_GAP.csv'
model=get_model()


# Function to Read and Convert Images
def load_resize_image(img):
    im = Image.open(img)
    # image = im.resize((224,224)) 
    image = np.array(im)
    return image


# CACHE :Loading the model
# Title
st.markdown("""
    # 🥙 FRITZ

    ## The first Meal Carbon Footprint Calculator powered by Deep Learning
""")
st.markdown("""Did you know that you **save more water** by **not eating** a steak than you would by **not showering** for **one month** ?""")

# Uploading the Image to the Page
uploadFile = st.file_uploader(label="🥘Upload image", type=['JPEG', 'PNG','JPG'])

# Checking the Format of the page
if uploadFile is not None:
    img = load_resize_image(uploadFile)
    response_reshape = resize(img,[224, 224])
    
    # Getting the output    
    probabilities=model.predict(np.array([response_reshape/255]))
    #[0.45,0.56,0.44]
    index=np.argmax(probabilities)
    recipe = load_classes(classes_path,index)
    
    # # To send to API
    # img = load_resize_image(uploadFile)
    # image_coded = img.astype('uint8')
    # height, width, channel = img.shape 
    # img_reshape = image_coded.reshape(height*width*channel)
    # img_enc = base64.b64encode(img_reshape)
    
    #Print image
    st.image(img)

    # st.write(img)
    st.write("📸 Image Uploaded Successfully !")
    st.write("🧠Wait a minute, FRITZ is identifying the recipe")

    # Reshape the image
    # X = img.reshape(img.shape[0]*img.shape[1]*img.shape[2])
    # X=X.tolist()
    # X_json=json.dumps(X)
    
    # # Call the POST
    # data={"image_reshape":img_enc.decode('utf8').replace("'", '"'),
    #                  "height": height,
    #                  "width": width,
    #                  "color": channel}
    # headers = {'Content-type': 'application/json'}
    # response = requests.post(url,json.dumps(data),headers=headers).json()
    recipe = recipe.replace("_", " ")
    st.write(f"FRITZ thinks the recipe is a **{recipe}**")
    
    st.write("🦑FRITZ is finding the ingredients")
    # st.write(getingredients(response))


    # Try packaging
    output_dict=getingredients(recipe)
    output_df=fill_empties(output_dict)
    # st.write(fill_empties(output_dict))
    final_df, missing_ingredients=match_ingredients(output_df)
    # st.write(final_df, missing_ingredients)
    # st.write(convert(final_df))
    final_result=convert(final_df)["calculated gCO2e"].sum()
    st.write(f"1 portion of this {recipe} emits {final_result} grams of C02")

else:
    st.write("Make sure you image is in JPEG/JPG/PNG Format.")



