import requests
import pandas as pd
import collections
from keys import get_api_key

# key API
api_key = get_api_key()

def recipes_call(dish, food_type, results_number=20):

    # first call --> getting the recipes for a dish
    get_id_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/search"
    id_querystring = {f"query":{dish},"number":{results_number}, "type":{food_type}}
    id_headers = {
        "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key
        }
    get_id_response = requests.request("GET", get_id_url, headers=id_headers, params=id_querystring)

    recipes = get_id_response.json()["results"]

    return recipes

def get_id(dish, food_type, results_number=20):

    recipes = recipes_call(dish, food_type, results_number)
    # recipes' titles
    titles = [[i][0]["title"] for i in recipes]

    # choosing just one recipe
    for title in titles:
        if dish in title.lower() and len(title) < len(dish)+15:
            break

    # recipe index
    index = titles.index(title)
    #number of serving to calculate a portion
    servings = recipes[index]["servings"]
    # recipe id for second call
    recipe_id = recipes[index]["id"]

    return servings, recipe_id

def id_call(dish, food_type, results_number=20):

    servings, recipe_id = get_id(dish, food_type, results_number)
    # second call --> getting the ingredintes of a recipe
    get_recipe_url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{recipe_id}/ingredientWidget.json"
    recipe_headers = {
        "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        "x-rapidapi-key": api_key
        }
    get_recipe_response = requests.request("GET", get_recipe_url, headers=recipe_headers)

    ingredients = get_recipe_response.json()["ingredients"]

    return servings, ingredients

def create_ingredients_dict(dish, food_type, results_number = 20):

    servings, ingredients = id_call(dish, food_type, results_number)

    # creating the dictionary with all the ingredients/metrics/values
    keys = ["name", "amount"]
    ingredients_dict = collections.defaultdict(list)

    for i in ingredients:
        new_dic = {k: i[k] for k in i.keys() & keys}
        metrics = new_dic["amount"]["metric"]["unit"]
        values = new_dic["amount"]["metric"]["value"]
        ingredients_dict["ingredient"].append(i["name"])
        ingredients_dict["value"].append(round(values / servings, 2))
        ingredients_dict["metric"].append(metrics)

    return ingredients_dict
