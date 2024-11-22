from grouping_algorithm import *
import pandas as pd
import json
from pandas import *
from dotenv import load_dotenv
import google.generativeai as genai
import os

def check_excel_format(df):
  
  try:
    required_columns = ['Pin Designator', 'Pin Display Name', 'Electrical Type', 'Pin Alternate Name', 'Grouping']

    if set(required_columns) == set(df.columns):
      return True, df
    elif set(required_columns[:-1]) == set(df.columns):  # Check for missing 'Grouping' column
      df['Grouping'] = ' '
      #df.to_excel(excel_path, index=False)
      return True, df
    else:
      print("Incorrect extraction format.")
      return False, df
  except Exception as e:
    print(f"Error reading Excel file: {e}")
    return False, df 
  

def assigning_grouping_as_per_database(old_df, json_path):
  df = old_df.copy()
  try:
    with open(json_path, 'r') as f:
      label_map = json.load(f) 

    def get_label(name):
        name = name.strip()
        for label, names in label_map.items():
            if name in [item.strip() for item in names]:
                return label
        print(f"Warning: Could not find a matching label for {name}. Assigning 'Unknown'.")    
        return None

    df['Grouping'] = df['Pin Display Name'].apply(get_label)
    print("Labels assigned to Grouping column successfully.")

  except Exception as e:
    print(f"Error processing files: {e}")    
  return df  

def assigning_grouping_as_per_LLM(pin_table):

    load_dotenv()
    model = genai.GenerativeModel("gemini-pro")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)

    # Prompt to LLM
    input = f"Guess what category this device can be just by referring to the pin table. Here is your pin table {pin_table}"
    response = model.generate_content(input)
    print(response.text)
    pin_grouping_table = pin_table

    # Return the response and an empty DataFrame (uniform with other functions)
    return response, pin_table  

def assigning_grouping_as_per_algorithm(df):
    df['Grouping'] = df['Pin Display Name'].apply(group_port_pins)
    #df['Grouping'] = df.apply(group_power_pin, axis=1)
    mask = df['Grouping'].isna()  # Create a mask for NaN values in 'Grouping'
    df.loc[mask, 'Grouping'] = df[mask].apply(group_other_io_pins, axis=1)
    mask = df['Grouping'].isna()  # Create a mask for NaN values in 'Grouping'
    df.loc[mask, 'Grouping'] = df[mask].apply(group_power_pins, axis=1)  # Apply group_power_pin only to NaN rows
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_output_pins, axis=1)
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_input_pins, axis=1)
    mask = df['Grouping'].isna()
    df.loc[mask, 'Grouping'] = df[mask].apply(group_passsive_pins, axis=1)    

    return df


def check_empty_groupings(df):
    empty_groupings = df[df['Grouping'].isna()]
    return empty_groupings

   