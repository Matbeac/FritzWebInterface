from PIL import Image
from pytesseract import pytesseract
def get_text(img):
    path_to_tesseract = r”/usr/local/Cellar/tesseract/4.1.3/bin/tesseract”
    img = Image.open(img)
    pytesseract.tesseract_cmd = path_to_tesseract
    text = pytesseract.image_to_string(img)
    return text[:-1]


text="STRING TO IMPORT"

## Splitting every line
string_list=[x for x in text.split("\n") if len(x)!=0]

## Gettin
ingredient_file_path='../Emission_computing/final_ingredients_emissions.csv'
df=pd.read_csv(ingredient_file_path,error_bad_lines=False)