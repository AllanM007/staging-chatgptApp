from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import uuid
import os
import re


@app.route("/backOfficeInput/addBackOfficeTone", methods=["POST"])
@cross_origin()
def addBackOfficeTone():
    if request.method == "POST":
        fmtData = request.form.to_dict(flat=False)

        user_quiz_categories = {
            "tone": fmtData["tone"][0],
            "timestamp": datetime.datetime.now(),
        }
        db.BackOfficeTones.insert_one(user_quiz_categories)
        return jsonify({"result": "success", "message": "Tone Set Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getBackOfficeTones", methods=["GET"])
@cross_origin()
def getBackOfficeTones():
    if request.method == "GET":
        backOfficeTones = db.BackOfficeTones.find()

        data_list = []

        for idx, item in enumerate(backOfficeTones):
            data_list.append(
                {
                    "id": idx + 1,
                    "tone": item["tone"],
                    "created_on": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/deleteBackOfficeTone", methods=["DELETE"])
@cross_origin()
def deleteBackOfficeTone():
    if request.method == "DELETE":
        fmtData = request.form.to_dict(flat=False)

        query = {"tone": fmtData["tone"][0]}
        backOfficeTone = db.BackOfficeTones.delete_one(query)

        return jsonify({"result": "success", "message": "Tone Deleted Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/phraseText", methods=["POST"])
@cross_origin()
def generateBackOfficePhrase():
    gptInstruction = ""
    userInstruction = ""

    fmtData = request.form.to_dict(flat=False)
    print(fmtData)
    soundLike = "normal"
    synonymRange = 0
    increaseTextRange = 0
    decreaseTextRange = 0

    if request.method == "POST":
        tone = fmtData["tone"][0]
        text = fmtData["text"][0]
        user = fmtData["user"][0]
        increaseTextRange = request.form["increaseTextRange"]
        decreaseTextRange = request.form["decreaseTextRange"]
        synonymRange = request.form["synonymRange"]
        soundLike = request.form["soundLike"]

        if int(increaseTextRange) > 0:
            gptInstruction = f"Provide a paraphrased responses in a {tone} way with appropriate punctuation marks. Make the response text longer by {increaseTextRange}% than the user prompt. Make your response sound {soundLike} with {synonymRange}% more synonyms. Your responses should always be in html markup. Never mention your html markup instructions in the response"
            userInstruction = f"Format the response for me in html markup with {synonymRange}% more synonyms which are wrapped in bold html markup tags in a {tone} tone. Make the response sound {soundLike} and increase the text count by {increaseTextRange}%"
        elif int(decreaseTextRange) > 0:
            gptInstruction = f"Provide a paraphrased responses in a {tone} way with appropriate punctuation marks. Make the response text shorter by {decreaseTextRange}% than the user prompt. Make your response sound {soundLike} with {synonymRange}% more synonyms. Your responses should always be in html markup. Never mention your html markup instructions in the response"
            userInstruction = f"Format the response for me in html markup with {synonymRange}% more synonyms which are wrapped in bold html markup tags in a {tone} tone. Make the response sound {soundLike} and decrease the text count by {decreaseTextRange}%"

        print(gptInstruction)

        gptMessageObject = [
            {"role": "system", "content": gptInstruction},
            {
                "role": "user",
                "content": text + userInstruction,
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
            "top_p": 1,
            "n": 1,
            "presence_penalty": 2,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload_data,
        )

        responseBody = response.json()

        print(responseBody["choices"][0]["message"]["content"])

        backoffice_phrasing_completions = {
            "completion_id": responseBody["id"],
            "user": user,
            "tone": tone,
            "user_text": text,
            "phrased_text": responseBody["choices"][0]["message"]["content"],
            "timestamp": datetime.datetime.now(),
        }
        db.BackOfficePhrasing.insert_one(backoffice_phrasing_completions)

        return jsonify(
            {
                "result": "success",
                "payload": responseBody["choices"][0]["message"]["content"],
            }
        )
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getBackOfficePhrases", methods=["GET"])
@cross_origin()
def getBackOfficePhrases():
    if request.method == "GET":
        backOfficeTones = db.BackOfficePhrasing.find()

        data_list = []

        for idx, item in enumerate(backOfficeTones):
            data_list.append(
                {
                    "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user": item["user"],
                    "user_text": item["user_text"],
                    "phrased_text": item["phrased_text"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getBackOfficePhrasesByTone", methods=["GET"])
@cross_origin()
def getBackOfficePhrasesByTone():
    if request.method == "GET":
        fmtData = request.form.to_dict(flat=False)

        query = {"tone": fmtData["tone"][0]}
        backOfficeTones = db.BackOfficePhrasing.find(query)

        data_list = []

        for idx, item in enumerate(backOfficeTones):
            data_list.append(
                {
                    "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user": item["user"],
                    "user_text": item["user_text"],
                    "tone": item["tone"],
                    "phrased_text": item["phrased_text"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getBackOfficePhrasesByDate", methods=["GET"])
@cross_origin()
def getBackOfficePhrasesByDate():
    dateFrom = datetime.datetime.strptime(request.form["dateFrom"], "%Y-%m-%d")
    dateTo = datetime.datetime.strptime(request.form["dateTo"], "%Y-%m-%d")

    if request.method == "GET":
        query = {
            "timestamp": {"$gte": dateFrom, "$lte": dateTo},
        }
        backOfficePhrases = db.BackOfficePhrasing.find(query)

        data_list = []

        for idx, item in enumerate(backOfficePhrases):
            data_list.append(
                {
                    "id": idx + 1,
                    "completion_id": item["completion_id"],
                    "user": item["user"],
                    "user_text": item["user_text"],
                    "tone": item["tone"],
                    "phrased_text": item["phrased_text"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})
