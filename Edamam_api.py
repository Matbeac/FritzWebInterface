import requests
import collections
#from Utils.keys import *
import streamlit as st


api_key = st.secrets["EDAMAM_KEY"]

def get_recipe(dish):

    #call API
    url = f"https://api.edamam.com/api/recipes/v2?type=public&q={dish}&app_id=4bc274b4&app_key={api_key}"

    response = requests.request("GET",url)
    recipe = response.json()["hits"][0]['recipe']

    return recipe

def getingredients(dish):

    #get ingredients from the call
    recipe = get_recipe(dish)
    servings = recipe['yield']
    ingredients = recipe['ingredients']

    new_dict = collections.defaultdict(list)

    for i in ingredients:
        new_dict["ingredient"].append(i['food'].lower())
        new_dict["weight"].append(round((i['weight'] / servings), 2))
        new_dict["foodCategory"].append(i['foodCategory'])
    return new_dict
if __name__=="__main__":
    print(getingredients("ceviche"))
