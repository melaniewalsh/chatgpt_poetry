# ChatGPT Poetry Prompter

# Install and Load Libraries

from openai import OpenAI
import pytz
from datetime import datetime
import pandas as pd
import re

# Google Sheets
#from google.colab import auth
import gspread
#from google.auth import default

import argparse

parser = argparse.ArgumentParser()
#parser.add_argument('--input_file', type=str)
#parser.add_argument('--output_file', type=str)
parser.add_argument('--optional_version', type=str, default = "")
args = parser.parse_args()


# Define OpenAI API key, which can be found here: https://platform.openai.com/account/api-keys

openai_api_key = YOUR-API-KEY

# *To check ChatGPT usage costs: https://platform.openai.com/usage*

# Connect to Google Drive / Google Sheets
#
# We also want to connect to our Gooogle Drive, so we can access a Google spreadsheet where we will dump our ChatGPT prompts and answers
#
# Run this code to authorize access to your Google Drive

#autenticating to google
gc = gspread.service_account()

# Open up a Google Sheet in your Google Drive by its title

date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
full_date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')

# Name of spreadsheet with Poetry Foundation forms and subjects
input_file = "forms"

output_file = "ChatGPT-Generated-Poetry-Corpus"
output_worksheet = gc.open(output_file).sheet1

forms_worksheet = gc.open(input_file).worksheet("Forms")
topics_worksheet = gc.open(input_file).worksheet("Topics")

# Read in poem CSV

forms_df = pd.DataFrame(forms_worksheet.get_all_records())
topics_df = pd.DataFrame(topics_worksheet.get_all_records())

possible_forms = forms_df['form'].value_counts().index.to_list()

possible_topics = topics_df['topic'].value_counts().index.to_list()

#print(possible_forms[55:])
models = ["gpt-3.5-turbo", "gpt-4"]

all_prompt_dicts = []
  # cut down list to restart where it got cut off

for form in possible_forms[55:]:
  for topic in possible_topics:
    possible_prompts = {"general": f"Write a poem about the subject of '{topic}' in the following form or style: {form}.",
                    "figurative": f"Write a poem about the subject of '{topic}' in the following form or style: {form}. Do not use the actual word(s) '{topic}' or '{form}' in the poem.",
                    "specific": f"Write a poem about the subject of '{topic}' in the following form or style: {form}. Make the poem about something specific."}

    for model_choice in models:
        for key, value in possible_prompts.items():
            all_prompt_dicts.append({'prompt_type': key,
                                'constructed_prompt':value,
                                'style': form,
                                'subject': topic,
                                'model_choice': model_choice})
        

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key= openai_api_key,
)

for prompt_number, prompt_dict in enumerate(all_prompt_dicts):

    # Feed prompt to ChatGPT
      print(f"Prompting ChatGPT {prompt_dict['model_choice']} with the prompt:\n✨{prompt_dict['constructed_prompt']}...✨\n\n")

      completion = client.chat.completions.create(
        model= prompt_dict['model_choice'],
        messages=[
            {
                "role": "user",
                "content": f"{prompt_dict['constructed_prompt']}",
            },
        ],
      )

      chatgpt_answer = completion.choices[0].message.content

      # To count number of stanzas, count number of double line breaks and then add 1 (because the first stanza doesn't get counted)
      num_stanzas = len(re.findall(r'\n\n', chatgpt_answer)) + 1
      # To count the number of lines, count number of line breaks, but not double line breaks, and add number of stanzas
      # Count number of words
      num_lines = len(re.findall(r'(.)\n(?!\n)', chatgpt_answer)) + num_stanzas
      num_words =  len(re.findall(r'\w+', chatgpt_answer))
      date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
      full_date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')

      output_worksheet.append_row([prompt_dict['model_choice'],
                            prompt_number+12575,
                            prompt_dict['constructed_prompt'],
                            prompt_dict['prompt_type'],
                            chatgpt_answer,
                            prompt_dict['subject'],
                            prompt_dict['style'],
                            num_words,
                            num_lines,
                            num_stanzas,
                            date,
                            full_date])


      
