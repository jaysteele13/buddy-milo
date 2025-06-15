# Load in GGUF Model (Find a System to cache this so it isn't done every time)
from llama_cpp import Llama
import re
import random


# Only load once
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path="SarcasMLL-1B.Q4_K_M.gguf",
            n_ctx=2048,
            n_threads=8,
            verbose=False
        )
    return _llm

def filter_response(response):
        """
        Keeps everything in the response up to and including the last sentence-ending punctuation (.?!).
        Removes any text that follows the last sentence.
        """
        match = re.search(r'^(.*?[.?!])[^.?!]*$', response, re.DOTALL)
        if match:
            return match.group(1)
        return response
# Use the model
def get_response(sentence):
    llm = get_llm()
    output = llm(f"Q: {sentence}\nA:", max_tokens=60, stop=["Q:", "\n"])

    response = output["choices"][0]["text"]

    if not response.strip():
        phrases = ['famalam',
               'brethern', 'milk drinker',
               'little barnacle', 'brotha', 'coke whore',
               'little worm', 'queen', 'golden boy']
        random_idx = random.randrange(0, len(phrases)-1)
         
        return f"Milo is confused and doesn't know what to say my {phrases[random_idx]}."
    else: 
        return filter_response(response)
    



