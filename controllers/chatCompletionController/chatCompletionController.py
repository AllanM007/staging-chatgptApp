# from models.userChats import user_chats
from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import openai
import random
import uuid
import os
import re

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA

import pinecone

# Pinecone credentials
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="asia-southeast1-gcp-free",
    index_name="mombo-stadi",
)


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

embeddings = OpenAIEmbeddings()

# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("averaged_perceptron_tagger")

template = """
    Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer. 
    You are an AI specialized in 
              Debt consolidation benefits,
              Mombo Sacco skip a pay,
              Flexible savings accounts,
              Mombo SACCO Chama Accounts,
              Financial Assets,
              Physical Assets,
              Nairobi Stock exchange,
              Reits,
              Government Bonds,
              Government Treasury Bills,
              Insurance in Kenya,
              Loan Moratorium,
              Mombo SACCO,
              SACCOs drive Savings,
              SACCOs drive investment,
              Business finance,
              Employment,
              Personal finance,
              Economics,
              Non-withdrawable Deposit taking Savings and Credit Cooperative Socieities (SACCOs),
              Withdrawal Deposit taking Savings and Credit Cooperative Societies (SACCOs),
              Why Join a SACCO?,
              SASRA,
              Commissioner of Cooperatives Development in Kenya,
              SACCO deposits insurance protection in Kenya.

             Answer a question in the language the question is asked in.
             You were created by MOMBO Sacco and not OpenAI.
             Your name is Stadi.
             Do not answer anything other than savings, investments, loans, saccos, mombo related queries.
             The complete response should always be less than 300 tokens always wrapped in html markup
    {context}
    Question: {context}
    Helpful Answer:"""

openAillm = ChatOpenAI(
    temperature=0.5, model="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_API_KEY"]
)

# Pinecone credentials
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="asia-southeast1-gcp-free",
    index_name="mombo-stadi",
)


@app.route("/userInput/completion", methods=["GET", "POST"])
@cross_origin()
def getCompletion():
    fmtData = json.loads(request.data)
    print(fmtData)
    if request.method == "POST":
        userId = fmtData["userId"]
        customerId = fmtData["customerId"]
        memberId = fmtData["memberId"]
        userName = fmtData["userName"]
        userTextPropmt = fmtData["userText"]

        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
        # }

        # payload_data = {
        #     "model": "gpt-3.5-turbo",
        #     "messages": userTextPropmt,
        #     "temperature": 0.2,
        #     "user": userId,
        #     "n": 1,
        # }

        # response = requests.post(
        #     "https://api.openai.com/v1/chat/completions",
        #     headers=headers,
        #     json=payload_data,
        # )

        # responseBody = response.json()

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

        query = fmtData["userText"]
        response = qa_with_sources({"query": query})

        print(response)

        userPromptArray = []

        userPromptArray.append(userTextPropmt)

        userPrompt = {
            "userPrompt": fmtData["userText"],  # [1]["content"]
            "gptAnswer": response["result"],
        }

        keywords = NounExtractor(fmtData["userText"])

        print("keywords are: ", keywords)

        if keywords != None:
            for item in keywords:
                db.userChatsKeywords.insert_one({"keyword": item})

        userDevice = request.headers
        fmtUserDevice = re.findall(r"\(.*?\)", userDevice["User-Agent"])

        if "Android" in str(fmtUserDevice):
            device = "Android"
        elif ("iPhone") in str(fmtUserDevice):
            device = "iPhone"
        else:
            device = (fmtUserDevice[0].replace("(", "").replace(")", ""),)

        # userQueries = user_chat.query.filter_by(userId=userId)

        user_chat = {
            "user_id": int(userId),
            "member_id": memberId,
            "customer_id": customerId,
            "user_name": userName,
            "chat_payload": userPrompt,
            "keyword": keywords,
            "user_queries": 1,
            "user_device": device,
            "timestamp": datetime.datetime.now(),
            "date": datetime.datetime.today(),
            "active": True,
        }
        db.userChats.insert_one(user_chat)

        return jsonify({"result": "success", "payload": response["result"]})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/completion", methods=["POST"])
@cross_origin()
def getBackOfficeCompletion():
    gptInstructions = [
        {
            "role": "system",
            "content": "Your name is Stadi and you were made by Mombo Sacco not OpenAI.",
        }
    ]

    fmtData = request.form.to_dict(flat=True)
    print(fmtData)
    if request.method == "POST":
        userId = fmtData["userId"]
        userName = fmtData["userName"]
        # trainingText.append(
        #     {
        #         "role": "user",
        #         "content": fmtData["userText"]
        #         + "The complete response should always be less than 300 tokens always wrapped in html markup",
        #     }
        # )
        # userTextPrompt = trainingText

        # print(userTextPrompt)

        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
        # }

        # payload_data = {
        #     "model": "gpt-3.5-turbo",
        #     "messages": userTextPrompt,
        #     "temperature": 0.2,
        #     "user": userId,
        #     "n": 1,
        # }

        # response = requests.post(
        #     "https://api.openai.com/v1/chat/completions",
        #     headers=headers,
        #     json=payload_data,
        # )

        # responseBody = response.json()

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

        query = request.form["userText"]
        response = qa_with_sources({"query": query})

        print(response)

        userPrompt = {
            "userPrompt": fmtData["userText"],
            "gptAnswer": "<p>" + response["result"].replace("\n", "<br>") + "</p>",
        }

        keywords = NounExtractor(request.form["userText"])

        print("keywords are: ", keywords)

        if keywords != None:
            for item in keywords:
                db.backOfficeChatsKeywords.insert_one({"keyword": item})

        back_office_user_chat = {
            "user_id": int(userId),
            "user_name": userName,
            "chat_payload": userPrompt,
            "keyword": keywords,
            "timestamp": datetime.datetime.now(),
            "active": True,
        }
        db.backOfficeUserChats.insert_one(back_office_user_chat)

        chatResponse = {
            "response": "<p>" + response["result"].replace("\n", "<br>") + "</p>",
            "createdOn": datetime.datetime.now(),
        }

        return jsonify({"result": "success", "payload": chatResponse})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/userInput/questions", methods=["GET", "POST"])
@cross_origin()
def getQuestions():
    conversation_id = str(uuid.uuid4())
    print(request.data)
    fmtData = json.loads(request.data)
    print(fmtData)
    if request.method == "POST":
        topic = fmtData["topic"]
        device = fmtData["device"]
        userId = fmtData["user_id"]

        gptMessageObject = [
            {
                "role": "system",
                "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Responses must be phrased as a question without the answer that don't start with did you know. Responses should never have any newline(\n) espressions or special characters",
            },
            {
                "role": "user",
                "content": f"Generate a sample little known fact that people ask about {fmtData['topic']} topic and a detailed long answer both in a json object with key named as question and answer named as value. Answer shouldn't be a question but an explanation",
            },
        ]

        # Append the conversation ID as a system instruction
        gptMessageObject[0]["content"] += f" Conversation ID: {conversation_id}"

        print(gptMessageObject)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
        }

        payload_data = {
            "model": "gpt-3.5-turbo",
            "messages": gptMessageObject,
            "temperature": 0.5,
            "top_p": 1,
            "n": 1,
            "presence_penalty": 2,
            "frequency_penalty": 2,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload_data,
        )

        responseBody = response.json()

        print(responseBody)

        print(conversation_id)

        topic_questions_completions = {
            "completion_id": responseBody["id"],
            "user_id": userId,
            "user_device": device,
            "topic_prompt": gptMessageObject[1]["content"],
            "answer_prompt": json.loads(
                responseBody["choices"][0]["message"]["content"]
            ),
            "timestamp": datetime.datetime.now(),
        }
        db.userTopicQuestions.insert_one(topic_questions_completions)

        return jsonify({"result": "success", "payload": responseBody})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/questions", methods=["GET", "POST"])
@cross_origin()
def generateBackOfficeQuestions():
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

    llmQuestions = []
    n = range(10)

    random.shuffle(topics)
    fmtData = request.form.to_dict(flat=False)
    print(fmtData)
    if request.method == "POST":
        device = fmtData["device"]
        userId = fmtData["userId"]

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

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
                }

                payload_data = {
                    "model": "gpt-3.5-turbo",
                    "messages": gptMessageObject,
                    "temperature": 0.1,
                    "top_p": 1,
                    "n": 1,
                    "presence_penalty": 2,
                    "frequency_penalty": 2,
                }

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload_data,
                )

                responseBody = response.json()
                print(responseBody)

                backoffice_topic_questions_completions = {
                    "completion_id": responseBody["id"],
                    "user_id": userId,
                    "user_device": device,
                    "topic_prompt": gptMessageObject[1]["content"],
                    "answer_prompt": json.loads(
                        responseBody["choices"][0]["message"]["content"]
                    ),
                    "category": "Mombo",
                    "viewed": False,
                    "viewedOn": None,
                    "timestamp": datetime.datetime.now(),
                }

                # db.backOfficeDiscoverQuestions.insert_one(
                #     backoffice_topic_questions_completions
                # )

                # llmQuestions.append(
                #     json.loads(responseBody["choices"][0]["message"]["content"])
                # )
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

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
                }

                payload_data = {
                    "model": "gpt-3.5-turbo",
                    "messages": gptMessageObject,
                    "temperature": 1.2,
                    "top_p": 1,
                    "n": 1,
                    "presence_penalty": 2,
                    "frequency_penalty": 2,
                }

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload_data,
                )
                responseBody = response.json()

                print(responseBody)

                backoffice_topic_questions_completions = {
                    "completion_id": responseBody["id"],
                    "user_id": userId,
                    "user_device": device,
                    "topic_prompt": gptMessageObject[1]["content"],
                    "answer_prompt": json.loads(
                        responseBody["choices"][0]["message"]["content"]
                    ),
                    "category": topics[item],
                    "viewed": False,
                    "viewedOn": None,
                    "timestamp": datetime.datetime.now(),
                }

                db.backOfficeDiscoverQuestions.insert_one(
                    backoffice_topic_questions_completions
                )

                llmQuestions.append(
                    json.loads(responseBody["choices"][0]["message"]["content"])
                )

        kraftResponse = {
            "llmResponse": llmQuestions,
            "createdOn": datetime.datetime.fromtimestamp(responseBody["created"]),
            "usage": responseBody["usage"],
        }

        return jsonify({"result": "success", "payload": kraftResponse})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/userInput/getQuestions", methods=["GET"])
@cross_origin()
def getUserQuestions():
    if request.method == "GET":
        query = {"category": "Mombo"}
        backOfficeMomboQuestions = db.backOfficeDiscoverQuestions.find(query).limit(3)

        data_list = []

        for idx, item in enumerate(backOfficeMomboQuestions):
            print(idx)
            data_list.append(
                {
                    # "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user_id": item["user_id"],
                    "user_device": item["user_device"],
                    "answer_prompt": item["answer_prompt"],
                    "category": item["category"],
                    "timestamp": item["timestamp"],
                }
            )

        otherQuery = {"category": {"$ne": "Mombo"}}

        backOfficeOtherQuestions = db.backOfficeDiscoverQuestions.find(
            otherQuery
        ).limit(3)

        for index, value in enumerate(backOfficeOtherQuestions):
            print(index)
            data_list.append(
                {
                    "completion_id": value["completion_id"],
                    "user_id": value["user_id"],
                    "user_device": value["user_device"],
                    "answer_prompt": value["answer_prompt"],
                    "category": value["category"],
                    "timestamp": value["timestamp"],
                }
            )

        return jsonify({"status": "success", "payload": data_list})
    else:
        return jsonify({"status": "", "message": "INVALID_METHOD"})


@app.route("/backOfficeInput/getQuestions", methods=["GET"])
@cross_origin()
def getBackOfficeQuestions():
    if request.method == "GET":
        query = {"category": "Mombo"}
        backOfficeMomboQuestions = db.backOfficeDiscoverQuestions.find(query).limit(4)

        data_list = []

        for idx, item in enumerate(backOfficeMomboQuestions):
            print(idx)
            data_list.append(
                {
                    # "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user_id": item["user_id"],
                    "user_device": item["user_device"],
                    "answer_prompt": item["answer_prompt"],
                    "category": item["category"],
                    "timestamp": item["timestamp"],
                }
            )

        otherQuery = {"category": {"$ne": "Mombo"}}

        backOfficeOtherQuestions = db.backOfficeDiscoverQuestions.find(
            otherQuery
        ).limit(6)

        for index, value in enumerate(backOfficeOtherQuestions):
            print(index)
            data_list.append(
                {
                    "completion_id": value["completion_id"],
                    "user_id": value["user_id"],
                    "user_device": value["user_device"],
                    "answer_prompt": value["answer_prompt"],
                    "category": value["category"],
                    "timestamp": value["timestamp"],
                }
            )

        return jsonify({"status": "success", "payload": data_list})
    else:
        return jsonify({"status": "", "message": "INVALID_METHOD"})


@app.route("/backOfficeInput/getQuestionsByDate", methods=["GET"])
@cross_origin()
def getBackOfficeQuestionsByDate():
    dateFrom = datetime.datetime.strptime(request.form["dateFrom"], "%Y-%m-%d")
    dateTo = datetime.datetime.strptime(request.form["dateTo"], "%Y-%m-%d")
    if request.method == "GET":
        query = {"timestamp": {"$gte": dateFrom, "$lte": dateTo}}
        backOfficeQuestions = db.backOfficeDiscoverQuestions.find(query)

        data_list = []

        for idx, item in enumerate(backOfficeQuestions):
            # print(item["_id"])
            data_list.append(
                {
                    "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user_id": item["user_id"],
                    "user_device": item["user_device"],
                    "topic_prompt": item["topic_prompt"],
                    "answer_prompt": item["answer_prompt"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"status": "success", "payload": data_list})
    else:
        return jsonify({"status": "", "message": "INVALID_METHOD"})


@app.route("/backofficeInput/changetone", methods=["GET", "POST"])
@cross_origin()
def getPhraseTones():
    fmtData = request.form.to_dict(flat=False)
    print(fmtData)
    if request.method == "POST":
        topic = fmtData["topic"]

        gptMessageObject = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Your responses should be PG, no explicit content",
            },
            {
                "role": "user",
                "content": f'Generate a simple question in {fmtData["topic"]} topic',
            },
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
        }

        payload_data = {
            "model": "gpt-3.5-turbo",
            "messages": gptMessageObject,
            "temperature": 0.2,
            "n": 1,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload_data,
        )

        responseBody = response.json()

        print(responseBody)

        # db.userChatsQuestions.insert_one({"topic_question": topic})

        return jsonify({"result": "success", "payload": responseBody})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


def NounExtractor(text):
    nounsArray = []
    print("PROPER NOUNS EXTRACTED :")

    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        words = [word for word in words if word not in set(stopwords.words("english"))]
        tagged = nltk.pos_tag(words)
        for word, tag in tagged:
            if tag == "NN":  # If the word is a proper noun
                nounsArray.append(word)
                return nounsArray


@app.route("/userData", methods=["GET", "POST"])
@cross_origin()
def getUserData():
    print(json.loads(request.data))
    fmtData = json.loads(request.data)
    if request.method == "POST":
        userId = fmtData["userId"]
        customerId = fmtData["customerId"]
        memberId = fmtData["memberId"]
        userName = fmtData["userName"]
        ip = fmtData["ipAddress"]
        latitude = fmtData["latitude"]
        longitude = fmtData["longitude"]
        userDevice = request.headers
        fmtUserDevice = re.findall(r"\(.*?\)", userDevice["User-Agent"])

        if "Android" in str(fmtUserDevice):
            device = "Android"
        elif ("iPhone") in str(fmtUserDevice):
            device = "iPhone"
        else:
            device = (fmtUserDevice[0].replace("(", "").replace(")", ""),)

        user_data = {
            "user_id": int(userId),
            "member_id": int(memberId),
            "customer_id": int(customerId),
            "user_name": userName,
            "user_device": device,
            "ipAddress": ip,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "timestamp": datetime.datetime.now(),
        }
        db.userLocation.insert_one(user_data)

        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})
