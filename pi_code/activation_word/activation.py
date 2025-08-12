import re
import phonetics
from rapidfuzz import fuzz

def hasMilo(sentence: str, target_word: str = "milo", threshold: int = 80):

    spaced_pattern = r"\b(?:mi\s+low|my\s+low|me\s+low|my\s+little)\b"
    spaced_matches = list(re.finditer(spaced_pattern, sentence, re.IGNORECASE))

    if spaced_matches:
        last_match = spaced_matches[-1]
        matched_phrase = last_match.group(0)
        sentence_after = sentence[last_match.end():].strip()
        return True, matched_phrase, sentence_after

    # --- Phonetic + fuzzy check for single words ---
    words = re.findall(r"\b\w+\b", sentence)
    target_meta = phonetics.metaphone(target_word)

    matched_word = None
    last_index = None
    char_last_index = None

    for match in re.finditer(r"\b\w+\b", sentence):
        word = match.group(0)
        word_meta = phonetics.metaphone(word)
        if word_meta == target_meta or fuzz.ratio(word.lower(), target_word.lower()) >= threshold:
            matched_word = word
            last_index = match.start()
            char_last_index = match.end()

    if matched_word is None:
        return False, None, sentence

    sentence_after = sentence[char_last_index:].strip()
    return True, matched_word, sentence_after





if __name__ == "__main__":

    print(hasMilo("I saw Milo at the park yesterday."))
    print(hasMilo("We met my low and later saw mi low on the poster."))
    print(hasMilo("I love mangoes."))
