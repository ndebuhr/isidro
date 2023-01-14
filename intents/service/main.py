import json
import tensorflow_text

import tensorflow as tf
import tensorflow_hub as hub

from flask import Flask, request
from sklearn.preprocessing import LabelBinarizer

app = Flask(__name__)

binarizer = LabelBinarizer()
binarizer.fit_transform([
    'ReviewUsage',
    'ReviewSetup',
    'CreateCron',
    'ScaleServices',
    'TestUnit',
    'DestructSelf',
    'SubmitIssue',
    'DestroyCron'
])

classifier_model = tf.keras.models.load_model(
    'intents.keras',
    custom_objects={'KerasLayer': hub.KerasLayer}
)

@app.route("/v1/intents", methods=["POST"])
def repeat():
    print(request.get_json())
    results = tf.nn.softmax(classifier_model(tf.constant(request.get_json())))
    intents = binarizer.inverse_transform(results.numpy())
    return json.dumps(list(intents))


@app.route("/", methods=["GET"])
def health():
    return ""