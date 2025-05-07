# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List


from rasa_sdk import (Action, Tracker)
from rasa_sdk.executor import CollectingDispatcher

import re
import os
import glob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from googletrans import Translator

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


class ActionFetchInfo(Action):
    def name(self):
        return "action_fetch_info"

    def run(self, dispatcher, tracker, domain):
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('punkt_tab')

        dct = {}


        def extract_keywords(sentence):
            sentence = sentence.lower()
            sentence = re.sub(r'[^\w\s]', '', sentence)
            tokens = word_tokenize(sentence)
            stop_words = set(stopwords.words('english'))
            tokens = [word for word in tokens if word not in stop_words]
            # cleaned_text = ' '.join(tokens)

            return tokens

        def search_keyword_in_files(keyword, directory, file_extension="*.txt"):
            matching_files = []

            files = glob.glob(os.path.join(directory, file_extension))

            for file in files:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, start=1):
                            if keyword.lower() in line.lower():
                                matching_files.append((file, i, line.strip()))
                except Exception as e:
                    print(f"Error reading {file}: {e}")

            if matching_files:
                for i in matching_files:
                    if i[2] not in dct.keys():
                        dct[i[2]] = 0
                    else:
                        dct[i[2]] += 1

            else:
                print(f"Keyword '{keyword}' not found in any file.")

        def detect_language(text):
            translator = Translator()
            detected = translator.detect(text)
            return detected.lang

        def translate_text(text, target_language="en"):  # Change "hi" for Hindi or any other language
            translator = Translator()
            translation = translator.translate(text, dest=target_language)
            return translation.text

        search_directory = "actions/resources"
        user_query = tracker.latest_message.get("text")
        # user_query= "tell me about birds"
        detected_lang = detect_language(user_query)
        translated_query = translate_text(user_query)

        keyword_to_search = extract_keywords(translated_query)
        print(keyword_to_search)

        for keyword in keyword_to_search:
            search_keyword_in_files(keyword, search_directory)
            print("\n")

        max_val = 0
        reply = list(dct.keys())[0]

        for k, v in dct.items():
            if v > max_val:
                max_val = v
                reply = k
        # dispatcher.utter_message(text=f"{dct}")
        print(dct)
        # print(reply)


        translated_reply = translate_text(reply, detected_lang)
        dispatcher.utter_message(text=f"{translated_reply}")

        return []


