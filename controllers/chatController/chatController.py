from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import uuid
import os
import re


@app.route("/callback")
@cross_origin()
def testCallback():
    print(request.data)
    return request.data


@app.route("/appInput/newChat", methods=["POST"])
@cross_origin()
def addNewGroupChat():
    print(request.data)
    # fmtData = request.form.to_dict(flat=False)
    fmtData = json.loads(request.data)
    print(fmtData)

    if request.method == "POST":
        # query = {"chat_id": fmtData["chat_id"], "group_id": fmtData["group_id"]}

        group_chat = {
            "author": {
                "firstName": fmtData["fName"],
                "id": fmtData["userId"],
                "imageUrl": "https://i.pravatar.cc/300?u=e52552f4-835d-4dbe-ba77-b076e659774d",
                "lastName": fmtData["lName"],
            },
            "createdAt": datetime.datetime.now(),
            "group_id": fmtData["groupId"],
            "chat_id": fmtData["chatId"],
            "status": "seen",
            "text": fmtData["message"],
            "type": "text",
        }

        db.GroupChat.insert_one(group_chat)
        return jsonify({"result": "success", "message": "Chat added succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/getUserChats", methods=["POST"])
@cross_origin()
def getUserChats():
    if request.method == "POST":
        # fmtData = request.form.to_dict(flat=False)
        fmtData = json.loads(request.data)
        print(fmtData)
        query = {"chat_id": fmtData["chatId"], "group_id": fmtData["groupId"]}
        userChats = db.GroupChat.find(query)

        data_list = []

        for idx, item in enumerate(userChats):
            data_list.append(
                {
                    "author": {
                        "firstName": item["author"]["firstName"],
                        "id": item["author"]["userId"],
                        "imageUrl": item["author"]["imageUrl"],
                        "lastName": item["author"]["lastName"],
                    },
                    "createdAt": item["createdAt"],
                    "group_id": item["group_id"],
                    "chat_id": item["chat_id"],
                    "status": item["status"],
                    "text": item["text"],
                    "type": item["type"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})
