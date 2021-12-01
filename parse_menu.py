from PIL import Image
from pytesseract import pytesseract
import pandas as pd
import re

def get_text(img):
    path_to_tesseract = r"tesseract"
    img = Image.open(img)
    pytesseract.tesseract_cmd = path_to_tesseract
    text = pytesseract.image_to_string(img)
    return text[:-1]


text="STRING TO IMPORT"

## Getting the whole dataframe
ingredient_file_path='Emission_computing/final_ingredients_emissions.csv'
df=pd.read_csv(ingredient_file_path,error_bad_lines=False)

def parse_menu(text):
    
## Splitting every line
    string_list=[x for x in text.split("\n") if len(x)!=0]
    
    final_dict={'ingredient_parsed':[],"ingredient_from_df":[], 'emission':[]}
    
    for line in string_list:
        ## Removing the metacharacters and the names
        line=line.lower()
        line=re.sub('[^A-Za-z0-9]+', ' ', line)
        line=re.sub(r'[0-9]+', '', line)
        ingredient_words=re.split('\s+', line)
        for ingredient in ingredient_words:
            if df[df['ingredient'].str.match(r''+str(ingredient)+'$')==True].ingredient.values.size>0:
                final_dict['ingredient_from_df'].append(df[df['ingredient'].str.match(r''+str(ingredient)+'$')== True].ingredient.iloc[0])
                final_dict['emission'].append(df[df['ingredient'].str.match(r''+str(ingredient)+'$')== True].emissions.iloc[0])
                final_dict["ingredient_parsed"].append(line)

    final_df=pd.DataFrame(final_dict)
    final_df['ingredient_parsed']=final_df['ingredient_parsed'].astype(str)
    result=final_df.groupby('ingredient_parsed').sum().sort_values(by="emission",ascending=True)
    return result

if __name__=="__main__":
    img = r"MS-Online-Menu-Mains-January.jpg"
    text=get_text(img)
    result=parse_menu(text)
    emission=result[result['emission']==result['emission'].min()].iloc[0,0]
    result=result[result['emission']==result['emission'].min()].index[0]
    print(f'The most ecological recipe is {result}, with a carbon footprint of {emission} g/C02 emitted per kg')
    print(parse_menu(text))
    