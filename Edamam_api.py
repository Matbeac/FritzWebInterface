import requests
import collections
from Recipe_API.keys import *

api_key = get_edamam_key()

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
        new_dict["value"].append(round((i['quantity'] / servings), 2))
        new_dict["metric"].append(i['measure'])
        new_dict["foodCategory"].append(i['foodCategory'])
    return new_dict
if __name__=="__main__":
    print(getingredients("ceviche"))
