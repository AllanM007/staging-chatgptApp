#!/usr/bin/env python
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
    send_from_directory,
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import sentry_sdk
import openai
import os, time

from sentry_sdk.integrations.flask import FlaskIntegration
from prometheus_client import start_http_server, Summary


from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN_KEY"],
    integrations=[
        FlaskIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)


app = Flask(__name__)
app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
app.config["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY", "")

TRAINING_DOCS_UPLOAD_FOLDER = "./content/"
ALLOWED_EXTENSIONS = {"txt", "pdf"}

app.config["UPLOAD_FOLDER"] = TRAINING_DOCS_UPLOAD_FOLDER


os.environ["TZ"] = "Africa/Nairobi"  # set new timezone
time.tzset()

# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)

uri = os.environ["MONGO_CLIENT"]

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"), connect=False)

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.mombo_chat
userChats = db.userChats


@app.before_first_request
def setup_openai():
    openai.api_key = app.config["OPENAI_API_KEY"]


@app.route("/debug-sentry")
def trigger_error():
    division_by_zero = 1 / 0


app.route("/")

from controllers.chatCompletionController import chatCompletionController
from controllers.phraseController import phraseController
from controllers.rewardsController import rewardsController
from controllers.quizController import quizController
from controllers.apiController import apiController
from controllers.chatController import chatController
from controllers.llmController import llmController

# from controllers.cronController import trainModels


def index():
    return "Hello I am Chat GPT In action"


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5050, debug=True)
