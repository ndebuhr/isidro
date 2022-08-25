import json
import os
import spacy
import time

import observability

from flask import Flask, abort, request

nlp = spacy.load("en_core_web_lg")

# https://universaldependencies.org/docs/u/pos/
POS_TAGS = ["PROPN", "NOUN", "VERB", "NUM", "SYM", "X"]

app = Flask(__name__)
observability.setup(
    flask_app=app
)

class Keywords:
    def __init__(self, request):
        self.text = request.get_json()["text"]

    def keywords(self):
        # Extract candidate words/phrases
        keywords = []
        for token in nlp(self.text):
            # Skip stop words
            if token.is_stop:
                continue
            # Collect lemma (lowercase) if there's a part of speech match
            if token.pos_ in POS_TAGS:
                keywords.append(token.lemma_.lower())
        # Deduplicate and publish results
        keywords = set(keywords)
        return json.dumps(list(keywords))


@app.route("/v1/keywords", methods=["POST"])
def keywords():
    keywords = Keywords(request)
    return keywords.keywords()


@app.route("/", methods=["GET"])
def health():
    return ""
