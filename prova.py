import nltk
import random
import json
import sys

nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer

with open('house_data.json') as f:
  data = json.load(f)


def print_question(prompt, possible_options = []):
    print(prompt)  # El chatbot imprimeix la pregunta 
    if not len(possible_options) == 0:  # En cas que la llista d'opcions NO estigui buida -> ha d'oferir opcions
      print("Options:", ", ".join(possible_options)) # Ofereix a l'usuari les possibles respostes 

def initialize_available_options(house_data, available_options): # available_options és un dict 
    for house in house_data['houses']: 
        for key, value in house.items():  # Per cada característica de cada casa
            available_options.setdefault(key, set()).add(value)  # Guarda un set per cada característica amb totes les opcions que hi ha per cada una (un set per no tenir repetits)

def preprocess_answer(answer): # Tokenitza la resposta del usuari
    answer = nltk.word_tokenize(answer)
    return answer 

def get_numerical_value(tok_answer): # Extreu valors numèrics de la resposta tokenitzada amb la funció anterior
    for token in tok_answer:
        if token.isnumeric() or token[:-1].isnumeric(): # Mira si el token és numèric o si sense l'ultim char ho és (per treure 'k' de 35k)
            return token 
    return '' # Només retorna un valor numèric si el troba, sinó retorna '' osigui res


class QuitException(Exception):
    """Excepció personalitzada per quan l'usuari vol sortir de la conversa"""
    pass

def process_numerical_question(question):
    print_question(question['question']) 
    while True:
        answer = input(question['prompt'])  
        print('                            ',answer)
        if str(answer).lower() == 'quit':
            raise QuitException(random.choice(data['end_messages']))
        elif answer.lower() == 'any':  
            return 'any'
        tok_answer = preprocess_answer(answer)
        value = get_numerical_value(tok_answer)
        if value != '': 
            return value

def process_multichoice_question(question, options):
    print_question(question['question'], options)  
    while True:
        answer = input(question['prompt']).lower()
        print('                            ',answer)
        if str(answer).lower() == 'quit':
            raise QuitException(random.choice(data['end_messages']))
        elif answer.lower() == 'any':  
            return 'any'
        if answer in options: 
            return answer
        
def convert_k_to_number(value):
    if isinstance(value, str) and 'k' in value.lower():
        return int(value.lower().replace('k', '000'))
    elif isinstance(value, str) and value.isdigit():
        return int(value)
    return value  

def get_salary_for_rent():
    while True:
        try:
            salary = float(input("What is your monthly salary in euros?\n "))
            return salary
        except ValueError:
            print("Please enter a valid number for your salary.")
            
def filter_houses_based_on_rent(houses, salary):
    max_rent = salary * 0.35
    affordable_houses = [house for house in houses if house['type'] == 'rent' and float(house['price']) <= max_rent]
    return affordable_houses
        
def find_suitable_houses(data, user_preferences):
    suitable_houses = []

    filters = {
        'bedrooms': lambda answer, house: int(house) >= int(answer) if answer != 'any' else True,
        'bathrooms': lambda answer, house: int(house) >= int(answer) if answer != 'any' else True,
        'price': lambda answer, house: convert_k_to_number(house) <= convert_k_to_number(answer) if answer != 'any' else True,
        'square_meters': lambda answer, house: int(house) >= int(answer) if answer != 'any' else True,
        'location': lambda answer, house: house == answer if answer != 'any' else True,
        'type': lambda answer, house: house == answer if answer != 'any' else True,
        'floor': lambda answer, house: int(house) >= int(answer) if answer != 'any' else True,
        'terrace': lambda answer, house: house == 'Yes' if answer == 'Yes' else True,  
        'elevator': lambda answer, house: house == 'Yes' if answer == 'Yes' else True,  
        'commercial_use': lambda answer, house: house == 'Yes' if answer == 'Yes' else True  
        }
    

    for house in data['houses']:
        is_suitable = True
        for key, filter_func in filters.items():
            if key in user_preferences:
                if not filter_func(user_preferences[key], house[key]):
                    is_suitable = False
                    break
        if is_suitable:
            suitable_houses.append(house)
    
    return suitable_houses

try:  
  start_message = random.choice(data['start_messages'])
  print("\n##################################################")
  print("#                                                #")
  print("#     WELCOME TO THE HOUSE FINDING ASSISTANT     #")
  print("#                                                #")
  print("##################################################\n")
  print(start_message)
  print("In order to help you find your dream house, I'm going to ask you to answer some questions for me.\n\n")
  print("If you feel indiferent about a question, just type 'any'.\n")
  print("If at any time you want to stop the conversation, just type 'quit'.\n\n")
  print("Lets roll!\n")


  user_preferences, available_options = {}, {} 

  initialize_available_options(data, available_options) 

  for question in data['questions']:
    answer_key = question['answer_key'] 
    possible_options = [option.lower() for option in available_options.get(answer_key, [])]
    
    if question['type'] == 'numerical':
      answer = process_numerical_question(question)
    else:
      answer = process_multichoice_question(question, possible_options) 

    user_preferences[answer_key] = answer 

    if answer_key == 'type' and (answer == 'rent' or answer == 'any'):
        salary = get_salary_for_rent()  # Cridem a la funció per obtenir el salari del client
        user_preferences['salary'] = salary  # Guardem el salari a les preferències del client


  def print_suitable_houses(suitable_houses):
    if suitable_houses:
      print("\nAlright! Based on your preferences, the most suitable houses are:\n\n")
      for house in suitable_houses:
        print(f"House with ID", house['id'], "is currently for", house['type'],". It has", house['bedrooms'], "bedrooms and", house['bathrooms'], "bathrooms.")
        print("Its price is of exactly", house['price'], "euros and it has", house['square_meters'], "m^2.")
        print("It is located in", house['location'],'.\n')
    else:
      print("\nSorry, I have found no suitable houses that match your preferences. \n")


# Filtratge d'habitatges segons les preferències de l'usuari:
  if 'salary' in user_preferences:
      suitable_houses = filter_houses_based_on_rent(data['houses'], user_preferences['salary'])
  else:
      suitable_houses = find_suitable_houses(data, user_preferences)
  
  print_suitable_houses(suitable_houses)

  end_message = random.choice(data['end_messages'])
  print(end_message, '\n\n')

except QuitException as e:
    print(e) 
    exit() 