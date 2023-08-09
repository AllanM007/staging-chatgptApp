from langchain import OpenAI, ConversationChain, SerpAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import (
    AgentType,
    initialize_agent,
    create_json_agent,
    load_tools,
    Tool,
    AgentExecutor,
)
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.chains import LLMChain, RetrievalQA, ConversationalRetrievalChain
from langchain.llms.openai import OpenAI
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)


from langchain.requests import TextRequestsWrapper
from langchain.tools.json.tool import JsonSpec

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.memory import ConversationBufferMemory
from langchain.utilities import SerpAPIWrapper

from langchain.schema import AIMessage, HumanMessage, SystemMessage

from langchain.document_loaders import (
    JSONLoader,
    TextLoader,
    UnstructuredURLLoader,
    SeleniumURLLoader,
)


from app import app, request, db, ALLOWED_EXTENSIONS, TRAINING_DOCS_UPLOAD_FOLDER
from flask import Flask, flash, request, redirect, url_for, json, jsonify
from werkzeug.utils import secure_filename

from datetime import datetime
from flask_cors import cross_origin
import requests
import openai
import os
import re

from pydantic import BaseModel, Field


import json
from pathlib import Path
from pprint import pprint

import pinecone

from langchain.document_loaders.sitemap import SitemapLoader

from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
embeddings = OpenAIEmbeddings()


search = SerpAPIWrapper()
tools = [
    Tool(
        name="Current Search",
        func=search.run,
        description="useful for when you need to answer questions about current events or the current state of the world",
    ),
]

# tools.append(
#     Tool.from_function(
#         func=llm_math_chain.run,
#         name="Calculator",
#         description="useful for when you need to answer questions about math",
#         args_schema=CalculatorInput
#         # coroutine= ... <- you can specify an async method if desired as well
#     )
# )

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

openAillm = ChatOpenAI(
    temperature=0.5, model="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_API_KEY"]
)

# Pinecone credentials
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment="asia-southeast1-gcp-free",
    index_name="mombo-stadi",
)


def send_email():
    return


@app.route("/llm/v1/Input", methods=["POST"])
@cross_origin()
def getLLMCompletion():
    chat = ChatOpenAI(temperature=0)
    chatResponse = chat.predict_messages(
        [
            HumanMessage(
                content="Translate this sentence from English to French. I love programming."
            )
        ]
    )

    print(chatResponse.content)

    return jsonify(
        {
            "status": "SUCCESS",
            "payload": {"response": chatResponse.content},
        }
    )


@app.route("/llm/v1/searchAgent", methods=["POST"])
@cross_origin()
def llmSearchAgent():
    template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer. 
    Only do external searches when completely necessary.
    {context}
    Question: {context}
    Helpful Answer:"""

    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context"],
        template=template,
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=openAillm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )

    searchResponse = qa_chain({"query": request.form["userPrompt"]})

    searchResponse["result"]

    print(request.form["userPrompt"])
    # The tools we'll give the Agent access to. Note that the 'llm-math' tool uses an LLM, so we need to pass that in.
    # tools = load_tools(["serpapi", "llm-math"], llm=llm)

    # Finally, let's initialize an agent with the tools, the language model, and the type of agent we want to use.
    # agent = initialize_agent(
    #     tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    # )

    # agent_chain = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    #     verbose=True,
    #     memory=memory,
    # )

    # Let's test it out!
    # searchResponse = agent_chain.run(request.form["userPrompt"])
    # searchResponse = result["result"]

    return jsonify({"status": "SUCCESS", "response": searchResponse})


@app.route("/llm/v1/userPrompt", methods=["POST"])
@cross_origin()
def userPrompt():
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
    {context}
    Question: {context}
    Helpful Answer:"""

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

    query = request.form["userPrompt"]
    result = qa_with_sources({"query": query})

    print(result)
    return jsonify({"status": "SUCCESS", "response": result["result"]})


@app.route("/llm/v1/startConversation", methods=["POST"])
@cross_origin()
def startLLMConversation():
    fmtData = request.form.to_dict(flat=True)

    conversation = ConversationChain(llm=openAillm, verbose=True)

    convoResponse = conversation.run(fmtData["userText"])

    return jsonify({"status": "SUCCESS", "payload": convoResponse})


@app.route("/llm/v1/newChat", methods=["GET"])
@cross_origin()
def llmNewChat():
    loader = JSONLoader(
        file_path="./tuning_data.json",
        jq_schema=".payload[].faqs[].answer",
        # json_lines=True,
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

    return jsonify({"status": "SUCCESS"})


@app.route("/llm/v1/findText", methods=["GET"])
@cross_origin()
def findSimilarText():
    docsearch = Pinecone.from_existing_index("mombo-stadi", embeddings)

    query = "What is M-Rewards?"

    docs = docsearch.similarity_search(query)
    print(len(docs))
    print(docs[0])
    return jsonify({"response": json.dumps(docs[0]), "docsLength": len(docs)})


@app.route("/llm/v1/startLLMChat", methods=["POST"])
@cross_origin()
def startLlmChat():
    docsearch = Pinecone.from_existing_index("mombo-stadi", embeddings)

    qa_with_sources = RetrievalQA.from_chain_type(
        llm=openAillm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        return_source_documents=True,
    )

    query = request.form["userText"]
    result = qa_with_sources({"query": query})

    print(result)

    return result["result"]


@app.route("/llm/v1/loadCustomData", methods=["GET"])
@cross_origin()
def loadCustomData():
    loader = JSONLoader(
        file_path="./tuning_data_prepared.jsonl",
        jq_schema=".prompt,.completion",
        json_lines=True,
    )

    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)

    # print(all_splits)

    vectorstore = Pinecone.from_documents(
        documents=all_splits, embedding=embeddings, index_name="mombo-stadi"
    )

    print(vectorstore)

    return jsonify({"status": "SUCCESS", "payload": json.dumps(data)})


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/v1/postTrainingFiles", methods=["POST"])
@cross_origin()
def upload_training_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "trainingFile" not in request.files:
            flash("No file part")
            return jsonify({"status": "FAILED", "message": "NO FILES ATTACHED"})
        file = request.files["trainingFile"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            # return redirect(request.url)
            return {"status": "FAILED", "message": "Invalid File"}
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(TRAINING_DOCS_UPLOAD_FOLDER, filename))
            return jsonify(
                {
                    "status": "SUCCESS",
                    "message": f"File {filename} uploaded succesfully",
                }
            )


@app.route("/llm/v1/getTrainingFiles", methods=["GET"])
@cross_origin()
def getTrainingFiles():
    directory = "./content/"

    fileNames = []

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f) and allowed_file(f):
            print(f)
            fileNames.append({"filename": filename})

    return jsonify(
        {
            "status": "SUCCESS",
            "payload": fileNames,
        }
    )


@app.route("/llm/v1/deleteTrainingFiles", methods=["DELETE"])
@cross_origin()
def deleteTrainingFiles():
    if request.method == "DELETE":
        if os.path.exists(f"./content/{request.form['file']}"):
            os.remove(f"./content/{request.form['file']}")

            return jsonify(
                {
                    "status": "SUCCESS",
                    "message": f"File {request.form['file']} deleted succesfully",
                }
            )
        else:
            return jsonify({"status": "FAIL", "message": "File does not exist!!"})
    else:
        return jsonify({"status": "FAIL", "message": "Invalid Method"})


@app.route("/llm/v1/getTrainingEvents", methods=["GET"])
@cross_origin()
def getTrainingEvents():
    if request.method == "GET":
        fileTrainingEvents = db.StadiCronEvents.find()

        data_list = []

        for idx, item in enumerate(fileTrainingEvents):
            data_list.append(
                {
                    "id": idx + 1,
                    "time": item["time"],
                    "log": item["log"],
                    "activity": item["activity"],
                }
            )

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})
