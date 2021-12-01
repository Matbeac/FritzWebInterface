from PIL import Image
from pytesseract import pytesseract
import pandas as pd
import re

def get_text(img):
    path_to_tesseract = r"/usr/local/Cellar/tesseract/4.1.3/bin/tesseract"
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
    return final_df.groupby('ingredient_parsed').sum()

text="""LONDON
HOUSE

A LA CARTE MENU

Marinated Nocellara olives 5
Harissa spiced nuts 3.5

Bread basket, olive oil & aged balsamic 4.5

STARTERS

Burrata, heirloom tomato, basil & toasted sourdough 11.5
Chicken Caesar salad, anchovies, croutons 1217.5
Hiramasa kingfish crudo, avocado, chili & ginger dressing 13.5

Chicken & duck liver parfait, brioche & grape chutney L6

MAINS
Harissa roasted cauliflower, warm chickpea salad, chimichurri 20.5
Grilled hake, romesco sauce, fennel & piquillo pepper 24
Parsley & basil chicken Kiev, creamed potatoes, salsa verde 18
Steak frites, roasted beef tomato, watercress 27
BBQ lamb, labneh, fennel and chili slaw 26.5

Fish & chips, tartare sauce, curry sauce, mushy peas 19.5

SIDES

Koffmann's fries 5.5

Heirloom tomato & basil salad 5.5

Seasonal greens & sage dressing 5.5

SWEETS
Chocolate brownic, dulce de leche, caramel sundae 9
Cinnamon doughnuts, passion [ruit curd 7
Sticky toffee pudding & vanilla ice cream 9

Mango sorbet, marinated berries 7.5

 

If you have a food allergy, intolerance or sensitivity, please speak lo your sereer

about ingredients in our dishes before you order your meal.

   

An optional 15% charge will be added to your All prices are inclusive of VAT."""

if __name__=="__main__":
    print(parse_menu(text))