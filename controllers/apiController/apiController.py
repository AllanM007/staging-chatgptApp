from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import dateutil.parser as parser
import requests
import os


@app.route("/api/v1/allChats", methods=["GET", "POST"])
@cross_origin()
def getAllChats():
    if request.method == "GET":
        userChats = db.userChats.find()

        data_list = []

        for idx, item in enumerate(userChats):
            # print(item["_id"])
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "memberId": int(item["member_id"]),
                    "customerId": int(item["customer_id"]),
                    "userName": item["user_name"],
                    "chatPayload": item["chat_payload"],
                    "keywords": item["keyword"],
                    "device": item["user_device"],
                    "timestamp": item["timestamp"],
                    "date": item["date"],
                    "active": item["active"],
                }
            )
            # print(data_list)

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/allBackOfficeChats", methods=["GET"])
@cross_origin()
def getAllBackOfficeChats():
    if request.method == "GET":
        userChats = db.backOfficeUserChats.find()

        data_list = []
        chatCount = 0

        for idx, item in enumerate(userChats):
            chatCount += 1

            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "userName": item["user_name"],
                    "chatPayload": item["chat_payload"],
                    "keywords": item["keyword"],
                    "timestamp": item["timestamp"],
                    "active": item["active"],
                }
            )

        return {"result": "SUCCESS", "payload": data_list, "noOfQueries": chatCount}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/allBackOfficeChatsById/<id>", methods=["GET"])
@cross_origin()
def getAllBackOfficeChatsById(id):
    if request.method == "GET":
        query = {"user_id": int(id)}
        backOfficeUserChats = db.backOfficeUserChats.find(query)

        data_list = []

        for idx, item in enumerate(backOfficeUserChats):
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "userName": item["user_name"],
                    "chatPayload": item["chat_payload"],
                    "keywords": item["keyword"],
                    "timestamp": item["timestamp"],
                    "active": item["active"],
                }
            )

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/allBackOfficeChatsByDate", methods=["GET"])
@cross_origin()
def getBackOfficeChatsByDate():
    print(request.form)
    dateFrom = datetime.strptime(request.form["dateFrom"], "%Y-%m-%d")
    dateTo = datetime.strptime(request.form["dateTo"], "%Y-%m-%d")
    if request.method == "GET":
        query = {"timestamp": {"$gte": dateFrom, "$lte": dateTo}}
        backOfficeUserChats = db.backOfficeUserChats.find(query)

        data_list = []

        for idx, item in enumerate(backOfficeUserChats):
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "userName": item["user_name"],
                    "chatPayload": item["chat_payload"],
                    "keywords": item["keyword"],
                    "timestamp": item["timestamp"],
                    "active": item["active"],
                }
            )

        return jsonify({"status": "SUCCESS", "payload": data_list})
    else:
        return jsonify({"status": "FAIL", "message": "INVALID_METHOD"})


@app.route("/api/v1/allUserLocations", methods=["GET", "POST"])
@cross_origin()
def getAllUserLocations():
    if request.method == "GET":
        userLocations = db.userLocation.find()

        data_list = []

        for idx, item in enumerate(userLocations):
            # print(item["_id"])
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": item["user_id"],
                    "memberId": item["member_id"],
                    "customerId": item["customer_id"],
                    "userName": item["user_name"],
                    "ipAddress": item["ipAddress"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "device": item["user_device"],
                    "timestamp": item["timestamp"],
                }
            )
            # print(data_list)

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/userLocations/<id>", methods=["GET", "POST"])
@cross_origin()
def getAllUserLocationsById(id):
    if request.method == "GET":
        query = {"user_id": int(id)}
        userLocations = db.userLocation.find(query)

        data_list = []

        for idx, item in enumerate(userLocations):
            # print(item["_id"])
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "memberId": int(item["member_id"]),
                    "customerId": int(item["customer_id"]),
                    "userName": item["user_name"],
                    "ipAddress": item["ipAddress"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "device": item["user_device"],
                    "timestamp": item["timestamp"],
                }
            )
            # print(data_list)

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/keywords", methods=["GET", "POST"])
@cross_origin()
def getAllChatsKeywords():
    if request.method == "GET":
        userChats = db.userChatsKeywords.find()

        data_list = []

        for idx, item in enumerate(userChats):
            # print(item["_id"])
            data_list.append(
                {
                    "id": idx + 1,
                    "keyword": item["keyword"],
                }
            )
            # print(data_list)

        return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/chats/<id>", methods=["GET", "POST"])
@cross_origin()
def getUserIdChats(id):
    if request.method == "GET":
        query = {"user_id": int(id)}
        userChats = db.userChats.find(query)

        chatsCounts = 0

        if not userChats:
            return jsonify({"result": "FAIL", "message": "NOT FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                chatsCounts += 1

                timestamp_object = datetime.strptime(
                    str(item["timestamp"]), "%Y-%m-%d %H:%M:%S.%f"
                )

                date_object = datetime.strptime(
                    str(item["timestamp"]), "%Y-%m-%d %H:%M:%S.%f"
                )

                # Convert the datetime object to the desired output format
                fmtTimeStamp = timestamp_object.strftime("%d/%m/%Y %H:%M:%S")
                fmtDate = date_object.strftime("%d/%m/%Y %H:%M:%S")

                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": fmtTimeStamp,
                        "date": fmtDate,
                        "active": item["active"],
                    }
                )
                # print(data_list)
                # print(chatsCounts)

            return {
                "result": "SUCCESS",
                "payload": data_list,
                "noOfQueries": chatsCounts,
            }
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/datesChats", methods=["GET", "POST"])
@cross_origin()
def getUserIdDatesChats():
    dateFrom = datetime.strptime(request.form["dateFrom"], "%Y-%m-%d")
    dateTo = datetime.strptime(request.form["dateTo"], "%Y-%m-%d")

    if request.method == "GET":
        query = {"date": {"$gte": dateFrom, "$lte": dateTo}}
        userChats = db.userChats.find(query)

        if not userChats:
            return jsonify({"result": "fail", "payload": "NOT_FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                # print(item["_id"])
                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": item["timestamp"],
                        "date": item["date"],
                        "active": item["active"],
                    }
                )
                # print(data_list)

            return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/userDatesChats", methods=["GET", "POST"])
@cross_origin()
def getUserIdDateRangeChats():
    uniqueId = request.form["userId"]
    dateFrom = datetime.strptime(request.form["dateFrom"], "%Y-%m-%d")
    dateTo = datetime.strptime(request.form["dateTo"], "%Y-%m-%d")

    if request.method == "GET":
        query = {
            "date": {"$gte": dateFrom, "$lte": dateTo},
            "user_id": int(uniqueId),
        }
        # print(query)
        userChats = db.userChats.find(query)

        # userChats = (
        #     user_chats.query.filter_by(userId=uniqueId)
        #     .filter(
        #         user_chats.date >= fmtDateFrom,
        #         user_chats.date <= fmtDateTo,
        #     )
        #     .filter_by(active=True)
        #     .order_by(user_chats.id.desc())
        #     .all()
        # )

        if not userChats:
            return jsonify({"result": "FAIL", "message": "NOT_FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                # print(item["_id"])
                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": item["timestamp"],
                        "date": item["date"],
                        "active": item["active"],
                    }
                )
                # print(data_list)

            return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/chats/keyword", methods=["GET", "POST"])
@cross_origin()
def getKeywordChats():
    if request.method == "GET":
        keyword = request.form["keyword"]
        query = {"keyword": keyword}
        userChats = db.userChats.find(query)

        if not userChats:
            return jsonify({"result": "FAIL", "message": "NOT FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                # print(item["_id"])
                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": item["timestamp"],
                        "date": item["date"],
                        "active": item["active"],
                    }
                )
                # print(data_list)

            return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/chats/userName", methods=["GET", "POST"])
@cross_origin()
def getUserNameChats():
    if request.method == "GET":
        userName = request.form["userName"]
        query = {"user_name": userName}
        userChats = db.userChats.find(query)

        if not userChats:
            return jsonify({"result": "FAIL", "message": "NOT FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                # print(item["_id"])
                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": item["timestamp"],
                        "date": item["date"],
                        "active": item["active"],
                    }
                )
                # print(data_list)

            return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})


@app.route("/api/v1/chats/OperatingSystem", methods=["GET", "POST"])
@cross_origin()
def getOperatingSystemChats():
    if request.method == "GET":
        operatingSystem = request.form["operatingSystem"]
        query = {"user_device": operatingSystem}
        userChats = db.userChats.find(query)

        if not userChats:
            return jsonify({"result": "FAIL", "message": "NOT FOUND"})
        else:
            data_list = []

            for idx, item in enumerate(userChats):
                # print(item["_id"])
                data_list.append(
                    {
                        "id": idx + 1,
                        "userId": int(item["user_id"]),
                        "memberId": int(item["member_id"]),
                        "customerId": int(item["customer_id"]),
                        "userName": item["user_name"],
                        "chatPayload": item["chat_payload"],
                        "keywords": item["keyword"],
                        "device": item["user_device"],
                        "timestamp": item["timestamp"],
                        "date": item["date"],
                        "active": item["active"],
                    }
                )
                # print(data_list)

            return {"result": "SUCCESS", "payload": data_list}
    else:
        return jsonify({"result": "FAIL", "message": "INVALID METHOD"})
