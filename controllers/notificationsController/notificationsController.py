from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import uuid
import os
import re


@app.route("/appInput/addUserNotification", methods=["POST"])
@cross_origin()
def createUserNotifications():
    if request.method == "POST":
        fmtData = json.loads(request.data)

        userNotification = {
            "user_id": fmtData["user_id"],
            "notificationText": fmtData["text"],
            "delivered": False,
            "status": True,
            "seen": False,
            "expiry": fmtData["expiry"],
            "createdAt": datetime.datetime.now(),
        }

        db.UserNotifications.insert_one(userNotification)
        return jsonify(
            {"result": "success", "payload": "Notification added succesfully"}
        )
    else:
        return jsonify({"result": "fail", "message": "Invalid Method"})


@app.route("/appInput/postUserNotification/<id>", methods=["POST"])
@cross_origin()
def postUserNotifications(id):
    if request.method == "POST":
        fmtData = json.loads(request.data)
        print(fmtData)
        query = {"user_id": id}
        userNotifications = db.UserNotifications.find(query)

        if 1 == 1:
            data_list = []
            for idx, item in enumerate(userNotifications):
                data_list.append(
                    {
                        "user_id": item["user_id"],
                        "chat_id": item["chat_id"],
                        "status": item["status"],
                        "notificationText": item["text"],
                        "createdAt": item["createdAt"],
                    }
                )
                return jsonify({"result": "success", "payload": data_list})
        else:
            return jsonify({"result": "fail", "message": "invalid request method"})

    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/getUserNotification/<id>", methods=["POST"])
@cross_origin()
def getUserNotifications(id):
    if request.method == "POST":
        fmtData = json.loads(request.data)
        print(fmtData)
        query = {"user_id": id}
        userNotifications = db.UserNotifications.find(query)

        if 1 == 1:
            data_list = []
            for idx, item in enumerate(userNotifications):
                data_list.append(
                    {
                        "user_id": item["user_id"],
                        "chat_id": item["chat_id"],
                        "status": item["status"],
                        "notificationText": item["text"],
                        "createdAt": item["createdAt"],
                    }
                )
                return jsonify({"result": "success", "payload": data_list})
        else:
            return jsonify({"result": "fail", "message": "invalid request method"})

    else:
        return jsonify({"result": "fail", "message": "invalid request method"})
