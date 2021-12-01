from PIL import Image
import pytesseract
import pandas as pd
import numpy as np
import re

def get_text(img):
    # path_to_tesseract = r"tesseract"
    img = Image.open(img)
    # pytesseract.tesseract_cmd = path_to_tesseract
    text = pytesseract.image_to_string(img)
    return text[:-1]


## Getting the whole dataframe
ingredient_file_path='Emission_computing/final_ingredients_emissions.csv'
df=pd.read_csv(ingredient_file_path,error_bad_lines=False)

def parse_menu(text):
    
## Splitting every line
    string_list=[x for x in text.split("\n") if len(x)!=0]
    
    final_dict={'Dish':[],"ingredient_from_df":[], 'g/CO2 emitted/kg':[]}
    
    for line in string_list:
        ## Removing the metacharacters and the names
        line=line.lower()
        line=re.sub('[^A-Za-z0-9]+', ' ', line)
        line=re.sub(r'[0-9]+', '', line)
        ingredient_words=re.split('\s+', line)
        for ingredient in ingredient_words:
            if df[df['ingredient'].str.match(r''+str(ingredient)+'$')==True].ingredient.values.size>0:
                final_dict['ingredient_from_df'].append(df[df['ingredient'].str.match(r''+str(ingredient)+'$')== True].ingredient.iloc[0])
                final_dict['g/CO2 emitted/kg'].append(df[df['ingredient'].str.match(r''+str(ingredient)+'$')== True].emissions.iloc[0])
                final_dict["Dish"].append(line)

    final_df=pd.DataFrame(final_dict)
    final_df['Dish']=final_df['Dish'].astype(str)
    final_df['Dish']=final_df['Dish'].str.capitalize()
    result=final_df.groupby('Dish', as_index=False).sum().sort_values(by="g/CO2 emitted/kg",ascending=True)
    result=result.reset_index()
    result=result.drop(columns=['index'])
    result["g/CO2 emitted/kg"]=np.floor(result["g/CO2 emitted/kg"])
    
    return result

