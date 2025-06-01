import re
from surf_logic import surf_forecast, BEACH_NAMES
from weather_logic import weather_forecast
import random


def milk_is_what():
    phrases = ['my milk is delecious',
               'milk is awesome', 'give me the milk',
               'i have a gun, hand over the milk', 'please for the love of god give me milk',
               'ok i have had enough of your bullshit. Give papa some milkies',
               'MILK']
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
    else:
        return 'lama_llm(sentence)'
    

if __name__ == "__main__":

    milk_sentence = 'uh so u like milk milo?'
    weather_sentence = 'weather like?'
    surf_sentence = 'i needa serf at east  strand today right now'

    sentence = weather_sentence
    print(f"Given Prompt:\n{sentence}\n\nResponse:\n{check_for_main_prompt(sentence)}")


