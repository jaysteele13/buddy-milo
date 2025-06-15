import re
from surf_logic import surf_forecast, BEACH_NAMES
from weather_logic import weather_forecast
from llm import get_response
import random


def milk_is_what():
    phrases = ['my milk is delecious',
               'milk is awesome', 'give me the milk',
               'i have a gun, hand over the milk', 'please for the love of god give me milk',
               'ok i have had enough of your bullshit. Give papa some milkies',
               'MILK']
    random_idx = random.randrange(0, len(phrases)-1)
    return phrases[random_idx]

def troggs_is_what():
    phrases = ['andy hill is top notch family',
               'dk but dorris is lit fam', 'give me the milk',
               'troggs is the pinncacle of north coast portrush',]
    random_idx = random.randrange(0, len(phrases)-1)
    return phrases[random_idx]


def check_for_main_prompt(sentence):
    sentence = sentence.lower()

    if re.search(r'\b(surf|serf)\b', sentence): 
        if re.search(r'\b(west)\b', sentence) and re.search(r'\b(today)\b',sentence): 
            return surf_forecast(beach=BEACH_NAMES.west_strand.value, today=True)
        elif re.search(r'\b(west)\b', sentence) and re.search(r'\b(tommorow)\b', sentence): 
            return surf_forecast(beach=BEACH_NAMES.west_strand.value, today=False)
        elif re.search(r'\b(west)\b', sentence):
            return surf_forecast(beach=BEACH_NAMES.west_strand.value, today=True)
        
        if re.search(r'\b(east)\b', sentence) and re.search(r'\b(today)\b', sentence): 
            return surf_forecast(beach=BEACH_NAMES.east_strand.value, today=True)
        elif re.search(r'\b(east)\b', sentence) and re.search(r'\b(tommorow)\b', sentence): 
            return surf_forecast(beach=BEACH_NAMES.east_strand.value, today=False)
        elif re.search(r'\b(east)\b', sentence):
            return surf_forecast(beach=BEACH_NAMES.east_strand.value, today=True)
        
        return surf_forecast()
    

    elif re.search(r'\bweather\b', sentence):
        return weather_forecast()
    elif re.search(r'\bmilk\b', sentence):
        return milk_is_what()
    elif re.search(r'\btrog\b', sentence) or re.search(r'\btroggs\b', sentence):
        return troggs_is_what()
    else:
        return get_response(sentence)
    

if __name__ == "__main__":

    milk_sentence = 'uh so u like milk milo?'
    weather_sentence = 'weather like?'
    surf_sentence = 'i needa serf at east  strand today right now'
    llm_sentence = 'jeez relax bro' # Could maybe upgrade GGUF model to be slightly bigger - for now this is fine

    sentence = llm_sentence
    print(f"Given Prompt:\n{sentence}\n\nResponse:\n{check_for_main_prompt(sentence)}")


