from os import name
import pandas as pd
import numpy as np

ingredient_file_path='Emission_computing/final_ingredients_emissions.csv'
conversion_file_path='Emission_computing/conversion.csv'

df=pd.read_csv(ingredient_file_path)
conv_df=pd.read_csv(conversion_file_path)

missing_values = ["<unit>", 'None']

# 1. Filling the empty strings

def fill_empties(output_dict):
    output_df=pd.DataFrame(output_dict)
    output_df.metric=output_df.metric.astype(str)
    for item in missing_values:
        output_df.metric.replace(item, "g", inplace=True)
    return output_df
print('OK Step 1')

# 2. Name matching using regex for all ingredients
def match_ingredients(output_df):
    final_dict={'ingredient':[], 'emission':[]}
    missing_ingredients={'missing_ingredients':[]}
    for ingredient in output_df['ingredient']:
        try:
            final_dict['ingredient'].append(df[df['ingredient'].str.match(r'.*'+str(ingredient)+'.*')== True].ingredient.values[0])
            final_dict['emission'].append(df[df['ingredient'].str.match(r'.*'+str(ingredient)+'.*')== True].emissions.values[0])
        except IndexError:
            missing_ingredients['missing_ingredients'].append(ingredient)
    final_df=pd.DataFrame(final_dict)
    
    # Adding the columns "value" and metric from output_dict
    final_df['value']=output_df['value']
    final_df['metric']=output_df['metric']
    return final_df,missing_ingredients
print('OK step 2')

# 3. Convert the values
def convert(final_df):
    output_df=final_df.merge(conv_df, on='metric')
    output_df["calculated gCO2e"]=output_df["emission"]*output_df["value"].astype('int64')*output_df["to_Kg_multiplier"]    
    return output_df
print('OK step 3')

if __name__=='__main__':
    output_dict= {'ingredient':['beef','shrimp','rer'],'value':['300','200','20'], 'metric':[None,'piece','clove']}
    output_df=fill_empties(output_dict)
    print('OK fill empty')
    final_df, missing_ingredients=match_ingredients(output_df)
    print(convert(final_df))
    
    