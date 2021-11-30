from os import name
import pandas as pd
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer 
import re
nltk.download('wordnet')

ingredient_file_path='Emission_computing/final_ingredients_emissions.csv'
conversion_file_path='Emission_computing/conversion.csv'

df=pd.read_csv(ingredient_file_path, error_bad_lines=False)
conv_df=pd.read_csv(conversion_file_path, error_bad_lines=False)

# I. Name matching using regex for all ingredients
def match_ingredients(output_df):
    final_dict={'ingredient':[], 'emission':[],'weight':[]}
    missing_ingredients={'missing_ingredients':[]}
    
    for ingredient in output_df['ingredient']:
        
        # 1. Lemmatize 
        ingredient_words=re.split('\s+', ingredient)
        lemmatizer = WordNetLemmatizer()
        lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in ingredient_words])
        ingredient_words=re.split('\s+', lemmatized_output)
        
        # 2. Try the whole lemmatized sentence
        if df[df['ingredient'].str.match(r'.*'+str(lemmatized_output)+'.*')== True].ingredient.values.size>0:
                final_dict['ingredient'].append(df[df['ingredient'].str.match(r'.*'+str(lemmatized_output)+'.*')== True].ingredient.values[0])
                final_dict['emission'].append(df[df['ingredient'].str.match(r'.*'+str(lemmatized_output)+'.*')== True].emissions.values[0])
                final_dict['weight'].append(output_df[output_df["ingredient"]==ingredient].weight.iloc[0])
                
#                 final_dict['value'].append(output_df[output_df["ingredient"]==ingredient].value.iloc[0])
#                 final_dict['metric'].append(output_df[output_df["ingredient"]==ingredient].metric.iloc[0])
        # False
        
        # 3. If the lemmatized output does not work, try the words
        else:
            for word in ingredient_words:
                # "ground" 
                # "beef"
                try:
                    final_dict['ingredient'].append(df[df['ingredient'].str.match(r'.*'+str(word)+'.*')== True].ingredient.values[0])
                    final_dict['emission'].append(df[df['ingredient'].str.match(r'.*'+str(word)+'.*')== True].emissions.values[0])
                    final_dict['weight'].append(output_df[output_df["ingredient"]==ingredient].weight.iloc[0])

#                     final_dict['value'].append(output_df[output_df["ingredient"]==ingredient].value.iloc[0])
#                     final_dict['metric'].append(output_df[output_df["ingredient"]==ingredient].metric.iloc[0])                    
                except IndexError:
                    missing_ingredients['missing_ingredients'].append(ingredient)
            
#     final_df=pd.DataFrame.from_dict(final_dict)
#     # Adding the columns "value" and metric from output_dict
#     final_df=final_df.merge(output_df,on="ingredient")
    final_df=pd.DataFrame(final_dict)

    return final_df,missing_ingredients

# II. Convert the values
def convert(final_df):
#     output_df=final_df.merge(conv_df, on='metric')
    final_df.emission=final_df.emission.round()
    final_df["calculated gCO2e"]=final_df["emission"]*final_df["weight"]*0.001# *output_df["to_Kg_multiplier"]
    return final_df
# print('OK step 3')
