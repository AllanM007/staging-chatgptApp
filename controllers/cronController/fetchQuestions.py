import os
import json
import random

from app import db
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA

import pinecone

# Pinecone credentials
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="asia-southeast1-gcp-free",
    index_name="mombo-stadi",
)

openAillm = ChatOpenAI(
    temperature=0.5, model="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_API_KEY"]
)

embeddings = OpenAIEmbeddings()


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


def fetchDiscoverQuestions():
    topics = [
        "Family and Parenting",
        "Food, Drinks and Entertainment",
        "Wellbeing, Health and Sports",
        "Culture, Arts and Sports",
        "Work, Business, Money and Economics",
        "Style, Beauty and Fashion",
        "Environment and Natural Disasters",
        "Local, Foreign or International News",
        "Technology",
        "Real life, True Stories and Community",
        "Travel",
        "Savings, Investments, Loans and Debt",
    ]

    n = range(10)

    random.shuffle(topics)
    for item in range(len(topics)):
        print(item)
        if 3 >= item:
            gptMessageObject = [
                {
                    "role": "system",
                    "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Responses must be phrased as a question without the answer that don't start with did you know. Responses should never have any newline(\n) espressions or special characters",
                },
                {
                    "role": "user",
                    "content": f"Generate a sample little known fact that people ask about Mombo Sacco topic and a detailed long answer both in a json object with key named as question and answer named as value. Answer shouldn't be a question but an explanation",
                },
            ]

            QA_CHAIN_PROMPT = PromptTemplate(
                input_variables=["context"],
                template=template,
            )

            docsearch = Pinecone.from_existing_index("mombo-stadi", embeddings)

            qa_with_sources = RetrievalQA.from_chain_type(
                llm=openAillm,
                chain_type="stuff",
                retriever=docsearch.as_retriever(),
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                return_source_documents=True,
            )

            query = f"Generate a sample little known fact that people ask about Mombo Sacco topic and a detailed long answer both in a json object with key named as question and answer named as value. Answer shouldn't be a question but an explanation"
            response = qa_with_sources({"query": query})

            backoffice_topic_questions_completions = {
                "topic_prompt": query,
                "answer_prompt": json.loads(response["result"]),
                "category": "Mombo",
                "viewed": False,
                "viewedOn": None,
                "timestamp": datetime.datetime.now(),
            }

            db.backOfficeDiscoverQuestions.insert_one(
                backoffice_topic_questions_completions
            )

        elif 9 >= item:
            gptMessageObject = [
                {
                    "role": "system",
                    "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Responses must be phrased as a question without the answer that don't start with did you know. Responses should never have any newline(\n) espressions or special characters",
                },
                {
                    "role": "user",
                    "content": f"Generate a sample little known fact that people ask about {topics[item]} topic and a detailed long answer both in a json object with key named as question and answer named as value. Answer shouldn't be a question but an explanation",
                },
            ]

            QA_CHAIN_PROMPT = PromptTemplate(
                input_variables=["context"],
                template=template,
            )

            docsearch = Pinecone.from_existing_index("mombo-stadi", embeddings)

            qa_with_sources = RetrievalQA.from_chain_type(
                llm=openAillm,
                chain_type="stuff",
                retriever=docsearch.as_retriever(),
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                return_source_documents=True,
            )

            query = f"Generate a sample little known fact that people ask about {topics[item]} topic and a detailed long answer both in a json object with key named as question and answer named as value. Answer shouldn't be a question but an explanation"
            response = qa_with_sources({"query": query})

            backoffice_topic_questions_completions = {
                "topic_prompt": query,
                "answer_prompt": json.loads(response["result"]),
                "category": topics[item],
                "viewed": False,
                "viewedOn": None,
                "timestamp": datetime.datetime.now(),
            }

            db.backOfficeDiscoverQuestions.insert_one(
                backoffice_topic_questions_completions
            )

    return {"status": "SUCCESS"}


def fetchQuizes():
    return {"status": "SUCCESS"}
