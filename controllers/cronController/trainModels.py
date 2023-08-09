from datetime import datetime

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import requests
import json
import os

from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import JSONLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import pinecone

import pinecone


load_dotenv()

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

openAillm = ChatOpenAI(
    temperature=0.5, model="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_API_KEY"]
)

# Pinecone credentials
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="asia-southeast1-gcp-free",
    index_name="mombo-stadi",
)


def llmTrainingFunction():
    faqResponse = requests.get(
        "https://mombo.digital/api/v1/backoffice/masters/general/faqs"
    )

    faqs = faqResponse.json()

    with open("home/allan/chatgptApp/tuning_data.json", "w") as outfile:
        outfile.write(json.dumps(faqResponse.json()))

        outfile.close()

    loader = JSONLoader(
        file_path="./tuning_data.json",
        jq_schema=".payload[].faqs[].answer",
    )

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )

    docs_chunks = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()

    docsearch = Pinecone.from_documents(
        docs_chunks, embeddings, index_name="mombo-stadi"
    )

    print(docsearch)

    succesful_cron_action = {
        "time": datetime.now(),
        "activity": "Log Time Every Five Seconds",
    }

    db.StadiCronEvents.insert_one(succesful_cron_action)

    return {"status": "SUCCESS"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["pdf"]


def llmTrainingDocs():
    directory = "home/allan/chatgptApp/content/"

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f) and allowed_file(f):
            print(f)
            loader = PyPDFLoader(
                file_path=f,
            )

            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                length_function=len,
            )

            docs_chunks = text_splitter.split_documents(docs)

            embeddings = OpenAIEmbeddings()

            docsearch = Pinecone.from_documents(
                docs_chunks, embeddings, index_name="mombo-stadi"
            )

            print(docsearch)

            newFileStr = f.replace("home/allan/chatgptApp/content/", "")

            succesful_cron_action = {
                "time": datetime.now(),
                "log": f"File {newFileStr} succesfully uploaded to training model",
                "activity": "Document Training",
            }

            db.StadiCronEvents.insert_one(succesful_cron_action)

    return {"status": "SUCCESS"}


# llmTrainingFunction()
llmTrainingDocs()
