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

missing_values = ['None']

# 1. Filling the empty strings

def fill_empties(output_dict):
    output_df=pd.DataFrame(output_dict)
    output_df.metric=output_df.metric.astype(str)
    for item in missing_values:
        output_df.metric.replace(item, "gram", inplace=True)
    return output_df
print('OK Step 1')

# 2. Name matching using regex for all ingredients
def match_ingredients(output_df):
    final_dict={'ingredient':[], 'emission':[],'value':[],'metric':[]}
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
                final_dict['value'].append(output_df[output_df["ingredient"]==ingredient].value.iloc[0])
                final_dict['metric'].append(output_df[output_df["ingredient"]==ingredient].metric.iloc[0])
        # False
        
        # 3. If the lemmatized output does not work, try the words
        else:
            for word in ingredient_words:
                # "ground" 
                # "beef"
                try:
                    final_dict['ingredient'].append(df[df['ingredient'].str.match(r'.*'+str(word)+'.*')== True].ingredient.values[0])
                    final_dict['emission'].append(df[df['ingredient'].str.match(r'.*'+str(word)+'.*')== True].emissions.values[0])
                    final_dict['value'].append(output_df[output_df["ingredient"]==ingredient].value.iloc[0])
                    final_dict['metric'].append(output_df[output_df["ingredient"]==ingredient].metric.iloc[0])                    
                except IndexError:
                    missing_ingredients['missing_ingredients'].append(ingredient)
            
#     final_df=pd.DataFrame.from_dict(final_dict)
#     # Adding the columns "value" and metric from output_dict
#     final_df=final_df.merge(output_df,on="ingredient")
    final_df=pd.DataFrame(final_dict)

    return final_df,missing_ingredients
    
    
    # Adding the columns "value" and metric from output_dict
    final_df=final_df.merge(output_df,on="ingredient")

    return final_df,missing_ingredients
print('OK step 2')

# 3. Convert the values
def convert(final_df):
    output_df=final_df.merge(conv_df, on='metric')
    output_df.emission=output_df.emission.round()
    output_df["calculated gCO2e"]=output_df["emission"]*output_df["value"]*output_df["to_Kg_multiplier"]
    return output_df
print('OK step 3')

if __name__=='__main__':
    output_dict= {'ingredient':['beef','shrimp','rer'],'value':['300','200','20'], 'metric':[None,'g','clove']}
    output_df=fill_empties(output_dict)
    print('OK fill empty')
    final_df, missing_ingredients=match_ingredients(output_df)
    print(convert(final_df))    