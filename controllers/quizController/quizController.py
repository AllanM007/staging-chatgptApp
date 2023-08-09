# from models.userChats import user_chats
from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import random
import openai
import uuid
import os
import re


@app.route("/backOfficeInput/addQuizType", methods=["POST"])
@cross_origin()
def addQuizType():
    if request.method == "POST":
        fmtData = json.loads(request.data)

        quiz_type = {
            "staffId": fmtData["staffId"],
            "staffName": fmtData["staffName"],
            "quiz_type": fmtData["quizType"],
            "createdOn": datetime.datetime.now(),
        }

        db.UserQuizTypes.replace_one(
            {"quiz_type": fmtData["quizType"]}, quiz_type, upsert=True
        )
        return jsonify(
            {"status": "success", "message": "Quiz type added succesfully!!"}
        )
    else:
        return jsonify({"status": "fail", "message": "Invalid method"})


@app.route("/backOfficeInput/getQuizeTypes", methods=["GET"])
@cross_origin()
def getUserQuizTypes():
    userQuizTypes = db.UserQuizTypes.find()

    data_list = []

    for idx, item in enumerate(userQuizTypes):
        data_list.append(
            {
                "id": idx + 1,
                "quizType": item["quiz_type"],
                "createdOn": item["createdOn"],
            }
        )

    return jsonify({"status": "success", "payload": data_list})


@app.route("/backOfficeInput/deleteQuizType/<id>", methods=["DELETE"])
@cross_origin()
def deleteUserQuizTypes(id):
    query = {"quiz_type": id}

    db.UserQuizTypes.delete_one(query)

    return jsonify({"status": "success", "message": "Quiz Type deleted succesfully!!"})


@app.route("/userInput/createNewQuiz", methods=["POST"])
@cross_origin()
def createNewQuiz():
    if request.method == "POST":
        quizes = []

        fmtData = json.loads(request.data)

        quizes = fmtData["quiz_object"]

        quizId = "".join(random.choice("0123456789ABCDEF") for i in range(8))

        userId = fmtData["userId"]
        quizName = fmtData["quizName"]
        quizTopic = fmtData["quizTopic"]
        setByAI = fmtData["setByAi"]
        quizPeriod = fmtData["quizPeriod"]
        quizType = fmtData["quizType"]
        quizObject = quizes
        noOfQuestions = fmtData["noOfQuestions"]
        noOfAttempts = fmtData["noOfAttempts"]
        timeLimits = fmtData["timeLimits"]
        breakPeriod = fmtData["breakPeriod"]

        if setByAI == True:
            gptMessageObject = [
                {
                    "role": "system",
                    "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Responses should never have any newline(\n) espressions or special characters",
                },
                {
                    "role": "user",
                    "content": f"Generate {noOfQuestions} sample {quizType} quizes about {quizTopic} with 4 options with the last key named answerIndex which has an array of objects containing the answer(s). All this should be in an array with json objects with key named as question which contains the question and answer options in a numbered nested object named as value. Answer shouldn't be short",
                },
            ]

            print(f"topic is {quizTopic}")
            print(f"no of questions are {noOfQuestions}")

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
            }

            payload_data = {
                "model": "gpt-3.5-turbo",
                "messages": gptMessageObject,
                "temperature": 1.0,
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

            user_new_quiz = {
                "completion_id": responseBody["id"],
                "user_id": userId,
                "quiz_id": quizId,
                "quizName": quizName,
                "quiz_topic": quizTopic,
                "setByAi": setByAI,
                "quizPeriod": quizPeriod,
                "quizType": quizType,
                "noOfQuestions": noOfQuestions,
                "noOfAttempts": noOfAttempts,
                "timeLimits": timeLimits,
                "breakPeriod": breakPeriod,
                "quiz_object": json.loads(
                    responseBody["choices"][0]["message"]["content"]
                ),
                "timestamp": datetime.datetime.now(),
            }
            db.UserGeneratedQuiz.replace_one(
                {"quiz_id": quizId}, user_new_quiz, upsert=True
            )  # .insert_one(user_new_quiz)

            return jsonify(
                {
                    "result": "success",
                    "message": "Quiz created succesfully",
                    "data": quizId,
                }
            )
        elif setByAI == False:
            if 0 > len(quizes):
                return jsonify({"status": "fail", "message": "Invalid quiz object"})
            else:
                print("set is false")
                user_new_quiz = {
                    "completion_id": "",
                    "user_id": userId,
                    "quiz_id": quizId,
                    "quizName": quizName,
                    "quiz_topic": quizTopic,
                    "setByAi": setByAI,
                    "quizPeriod": quizPeriod,
                    "quizType": quizType,
                    "noOfQuestions": noOfQuestions,
                    "noOfAttempts": noOfAttempts,
                    "timeLimits": timeLimits,
                    "breakPeriod": breakPeriod,
                    "quiz_object": quizObject,
                    "timestamp": datetime.datetime.now(),
                }
                db.UserGeneratedQuiz.replace_one(
                    {"quiz_id": quizId}, user_new_quiz, upsert=True
                )  # .insert_one(user_new_quiz)

                return jsonify(
                    {
                        "result": "success",
                        "message": "Quiz created succesfully",
                        "data": quizId,
                    }
                )
    else:
        return jsonify({"result": "fail", "message": "Invalid method"})


@app.route("/userInput/addQuizObjects", methods=["POST"])
@cross_origin()
def addUserQuizObjects():
    if request.method == "POST":
        data = request.data
        fmtData = json.loads(data)

        new_user_quiz = {
            "user_id": fmtData["userId"],
            "quiz_id": fmtData["quiz_id"],
            "quiz_object": fmtData["quizObject"],
        }

        db.UserGeneratedQuizes.insert_one(new_user_quiz)

        return jsonify(
            {"result": "SUCCESS", "message": "Quizes added succefully", "data": fmtData}
        )
    else:
        return jsonify({"result": "FAIL", "message": "Invalid method"})


@app.route("/userInput/getQuizById/<id>", methods=["GET"])
@cross_origin()
def getQuizById(id):
    if request.method == "GET":
        query = {"quiz_id": id}
        print(query)
        userQuizes = db.UserGeneratedQuiz.find(query)
        data_list = []

        for idx, item in enumerate(userQuizes):
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "quizId": item["quiz_id"],
                    "quizName": item["quizName"],
                    "quiTopic": item["quiz_topic"],
                    "quizPeriod": item["quizPeriod"],
                    "quizType": item["quizType"],
                    "noOfQuestions": item["noOfQuestions"],
                    "noOfAttempts": int(item["noOfAttempts"]),
                    "quizObject": item["quiz_object"],
                    "timeLimits": item["timeLimits"],
                    "breakPeriod": item["breakPeriod"],
                    "createdOn": item["timestamp"],
                }
            )

        return jsonify({"status": "SUCCESS", "data": data_list})
    else:
        return jsonify({"status": "FAIL", "message": "Invalid Method"})


@app.route("/userInput/getQuizByUserId/<id>", methods=["GET"])
@cross_origin()
def getQuizByUserId(id):
    if request.method == "GET":
        print(id)
        query = {"user_id": int(id)}
        userQuizes = db.UserGeneratedQuiz.find(query)
        data_list = []

        for idx, item in enumerate(userQuizes):
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "quizId": item["quiz_id"],
                    "quizName": item["quizName"],
                    "quiTopic": item["quiz_topic"],
                    "quizPeriod": item["quizPeriod"],
                    "quizType": item["quizType"],
                    "noOfQuestions": item["noOfQuestions"],
                    "noOfAttempts": int(item["noOfAttempts"]),
                    "quizObject": item["quiz_object"],
                    "timeLimits": item["timeLimits"],
                    "breakPeriod": item["breakPeriod"],
                    "createdOn": item["timestamp"],
                }
            )

        return jsonify({"status": "SUCCESS", "data": data_list})
    else:
        return jsonify({"status": "FAIL", "message": "Invalid Method"})


@app.route("/userInput/generateSystemQuiz", methods=["POST"])
@cross_origin()
def generateSystemQuizes():
    allCategories = db.userQuizCategory.find()

    for index, item in enumerate(allCategories):
        print("quiz topic is ", item)
        quizId = "".join(random.choice("0123456789ABCDEF") for i in range(8))

        cat = item["category"]

        gptMessageObject = [
            {
                "role": "system",
                "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Responses should never have any newline(\n) espressions or special characters",
            },
            {
                "role": "user",
                "content": f"Generate 4 sample quizes about {cat} with 4 options with the last key named answerIndex which has an object of strings containing the answer(s). All this should be in an array with json objects with key named as question which contains the question and answer options in an array named as value. Answer shouldn't be short",
            },
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", ""),
        }

        payload_data = {
            "model": "gpt-3.5-turbo",
            "messages": gptMessageObject,
            "temperature": 1.0,
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

        user_new_quiz = {
            "completion_id": responseBody["id"],
            "user_id": 1,
            "quiz_id": quizId,
            "quizName": "Quiz",
            "quiz_topic": cat,
            "setByAi": True,
            "quizPeriod": 10,
            "quizType": "quizType",
            "noOfQuestions": 4,
            "noOfAttempts": 1,
            "breakPeriod": 5,
            "quiz_object": json.loads(responseBody["choices"][0]["message"]["content"]),
            "timestamp": datetime.datetime.now(),
        }
        db.SystemGeneratedQuiz.replace_one(
            {"quiz_id": quizId}, user_new_quiz, upsert=True
        )  # .insert_one(user_new_quiz)

    return jsonify(
        {
            "result": "success",
            "message": "Quiz generated succesfully",
        }
    )


@app.route("/userInput/getQuizByCategory/<id>", methods=["GET"])
@cross_origin()
def getQuizByCategory(id):
    if request.method == "GET":
        category = ""

        query = {"id": int(id)}

        quizCategory = db.userQuizCategory.find(query)

        for value in quizCategory:
            category = value["category"]

        query = {"quiz_topic": category}

        userQuizes = db.SystemGeneratedQuiz.find(query).limit(1)
        data_list = []

        for idx, item in enumerate(userQuizes):
            data_list.append(
                {
                    "id": idx + 1,
                    "ids": str(item["_id"]),
                    "userId": 1,
                    "quizId": item["quiz_id"],
                    "quizName": "Quiz",
                    "quizTopic": item["quiz_topic"],
                    "quizPeriod": 10,
                    "quizType": item["quizType"],
                    "noOfQuestions": len(item["quiz_object"]),
                    "noOfAttempts": 1,
                    "quizObject": item["quiz_object"],
                    "breakPeriod": 10,
                    "createdOn": item["timestamp"],
                }
            )

        return jsonify({"status": "SUCCESS", "data": data_list})
    else:
        return jsonify({"status": "FAIL", "message": "Invalid Method"})


@app.route("/backofficeInput/setQuizRewards", methods=["POST"])
@cross_origin()
def setQuizRewards():
    if request.method == "POST":
        quiz_rewards = {
            "user_points": int(request.form["user_points"]),
            "timestamp": datetime.datetime.now(),
        }

        db.userQuizRewardsSettings.replace_one({"_id": 1}, quiz_rewards, upsert=True)
        return jsonify({"result": "success", "message": "Quiz Reward Set Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backofficeInput/setRouletteRewards", methods=["POST"])
@cross_origin()
def setRouletteRewards():
    if request.method == "POST":
        quiz_rewards = {
            "user_points": int(request.form["user_points"]),
            "timestamp": datetime.datetime.now(),
        }
        db.userRouletteRewardsSettings.replace_one(
            {"_id": 1}, quiz_rewards, upsert=True
        )
        return jsonify(
            {"result": "success", "message": "Roulette Reward Set Succesfully"}
        )
    else:
        return jsonify({"result": "fail", "message": "Invalid Request Method"})


@app.route("/backOfficeInput/checkQuizRewards/<id>", methods=["GET"])
@cross_origin()
def checkQuizRewards(id):
    if request.method == "GET":
        totalQuizPoints = 0
        query = {"user_id": id}
        userRewards = db.userQuizRewards.find(query)

        data_list = []

        for idx, item in enumerate(userRewards):
            totalQuizPoints += item["points"]
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "memberId": int(item["member_id"]),
                    "customerId": int(item["customer_id"]),
                    "userName": item["user_name"],
                    "points": item["points"],
                    "device": item["device"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify(
            {
                "result": "success",
                "totalQuizPoints": totalQuizPoints,
                "payload": data_list,
            }
        )
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/checkRouletteRewards/<id>", methods=["GET"])
@cross_origin()
def checkRouletteRewards(id):
    if request.method == "GET":
        totalRoulettePoints = 0
        query = {"user_id": id}
        userRouletteRewards = db.userRouletteRewards.find(query)

        data_list = []

        for idx, item in enumerate(userRouletteRewards):
            totalRoulettePoints += item["points"]
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "memberId": int(item["member_id"]),
                    "customerId": int(item["customer_id"]),
                    "userName": item["user_name"],
                    "points": item["points"],
                    "device": item["device"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify(
            {
                "result": "success",
                "totalRoulettePoints": totalRoulettePoints,
                "payload": data_list,
            }
        )
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/setQuizRewardsXchange", methods=["POST"])
@cross_origin()
def setQuizRewardsXchangeRate():
    if request.method == "POST":
        user_quiz_rewards = {
            "activity": int(request.form["activity"]),
            "user_points": int(request.form["user_points"]),
            "user_amount": int(request.form["user_amount"]),
            "timestamp": datetime.datetime.now(),
        }
        db.userRewardsXchangeRate.replace_one(
            {"_id": 1}, user_quiz_rewards, upsert=True
        )
        return jsonify(
            {"result": "success", "message": "Exchange Rate Set Succesfully"}
        )
    else:
        return jsonify({"result": "fail", "message": "Invalid Request Method"})


@app.route("/backOfficeInput/getActivityXchangeRate/<id>", methods=["GET"])
@cross_origin()
def getActivityXchangeRate(id):
    if request.method == "GET":
        query = {"activity": int(id)}
        userXchangeRate = db.userRewardsXchangeRate.find(query)

        data_list = []

        for idx, item in enumerate(userXchangeRate):
            data_list.append(
                {
                    "id": idx + 1,
                    "activity": int(item["activity"]),
                    # "activityName": item["activity_name"],
                    "userPoints": int(item["user_points"]),
                    "userAmount": int(item["user_amount"]),
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/addActivity", methods=["POST"])
@cross_origin()
def addActivity():
    if request.method == "POST":
        user_reward_activity = {
            "activity": int(request.form["activity"]),
            "activityName": request.form["activityName"],
            "timestamp": datetime.datetime.now(),
        }
        db.userRewardsActivities.replace_one(
            {"_id": request.form["activity"]}, user_reward_activity, upsert=True
        )
        return jsonify({"result": "success", "message": "Activity Set Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getActivities", methods=["GET"])
@cross_origin()
def getActivities():
    if request.method == "GET":
        userRewardsActivities = db.userRewardsActivities.find()

        data_list = []

        for idx, item in enumerate(userRewardsActivities):
            data_list.append(
                {
                    "id": idx + 1,
                    "activity": int(item["activity"]),
                    "activityName": item["activityName"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


def get_next_sequence(name):
    ret = db.catCounter.find_one_and_update(
        {"_id": name}, {"$inc": {"seq": 1}}, return_document=True
    )

    print(ret)

    return ret["seq"]


@app.route("/backOfficeInput/addQuizCategory", methods=["POST"])
@cross_origin()
def addQuizCategory():
    if request.method == "POST":
        user_quiz_categories = {
            "id": get_next_sequence("catid"),
            "category": request.form["category"],
            "timestamp": datetime.datetime.now(),
        }
        db.userQuizCategory.replace_one(
            {"category": request.form["category"]}, user_quiz_categories, upsert=True
        )
        return jsonify(
            {"result": "success", "message": "Quiz Category Set Succesfully"}
        )
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getQuizCategories", methods=["GET"])
@cross_origin()
def getQuizCategories():
    if request.method == "GET":
        userCategories = db.userQuizCategory.find()

        data_list = []

        for idx, item in enumerate(userCategories):
            data_list.append(
                {
                    "id": idx + 1,
                    "category": item["category"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getAllUserRewards/<id>", methods=["GET"])
@cross_origin()
def getAllUserRewards(id):
    if request.method == "GET":
        totalUserPoints = 0
        query = {"user_id": id}
        userRouletteRewards = db.userRouletteRewards.find(query)
        userQuizRewards = db.userQuizRewards.find(query)

        data_list = []

        for idx, item in enumerate(userRouletteRewards):
            totalUserPoints += item["points"]

        for idx, item in enumerate(userQuizRewards):
            totalUserPoints += item["points"]

        data_list.append(
            {
                "id": id,
                "totalUserPoints": totalUserPoints,
                "timestamp": datetime.datetime.now(),
            }
        )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/getLeaderboard", methods=["GET"])
@cross_origin()
def getLeaderboard():
    if request.method == "GET":
        userPoints = 0
        userAmount = 0

        userQuizXchangeRate = db.userQuizRewardsXchangeRate.find()
        for index, val in enumerate(userQuizXchangeRate):
            userAmount = val["user_amount"]
            userPoints = val["user_points"]

        print(f"user points is {userPoints} and user amount is {userAmount}")

        allUsersRewards = db.userQuizRewards.find()

        data_list = []

        for idx, item in enumerate(allUsersRewards):
            data_list.append(
                {
                    "name": "User",
                    "userId": int(item["user_id"]),
                    "points": item["points"],
                    "timestamp": item["timestamp"],
                }
            )

        # Create a dictionary to store merged data
        merged_data = {}

        # Iterate through each entry in the data
        for entry in data_list:
            user_id = entry["userId"]
            if user_id not in merged_data:
                pointsValue = (entry["points"] * userAmount) / userPoints

                merged_data[user_id] = {
                    "name": entry["name"],
                    "points": entry["points"],
                    "value": pointsValue,
                    "timestamp": entry["timestamp"],
                    "userId": user_id,
                }
            else:
                merged_data[user_id]["points"] += entry["points"]

        # Convert the merged dictionary values back to a list
        merged_list = list(merged_data.values())
        print(merged_list)

        return jsonify({"result": "success", "payload": merged_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/backOfficeInput/deleteQuizCategory", methods=["DELETE"])
@cross_origin()
def deleteQuizCategory():
    if request.method == "DELETE":
        query = {"category": request.form["category"]}
        userQuizCategory = db.userQuizCategory.delete_one(query)

        return jsonify({"result": "success", "message": "Category Deleted Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/generateQuiz", methods=["GET", "POST"])
@cross_origin()
def generateQuiz():
    conversation_id = str(uuid.uuid4())
    print(request.data)
    fmtData = json.loads(request.data)  # form.to_dict(flat=False)
    print(fmtData)

    if request.method == "POST":
        device = fmtData["device"]
        topic = fmtData["topic"]
        level = fmtData["level"]
        userId = fmtData["userId"]
        number = fmtData["number"]

        gptMessageObject = [
            {
                "role": "system",
                "content": f"Your responses should not be explicit. Never, ever, ever repeat the response sent, response should always be different. Response must always be 7 tokens. Responses must be phrased as a question without the answer that don't start with did you know. Responses should never have any newline(\n) espressions or special characters",
            },
            {
                "role": "user",
                "content": f"Generate {number} {level} sample questions about {topic} each with four options with the first option in the values nested object being the correct answer both in a json object with key named as question which contains the question and answer options in a numbered nested object named as value. Answer shouldn't be a short",
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
            "temperature": 1.0,
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

        print(conversation_id)

        app_topic_quizs_completions = {
            "completion_id": responseBody["id"],
            "user_id": userId,
            "user_device": device,
            "quiz_object": json.loads(responseBody["choices"][0]["message"]["content"]),
            "timestamp": datetime.datetime.now(),
        }
        db.AppGeneratedQuiz.insert_one(app_topic_quizs_completions)

        return jsonify(
            {
                "result": "success",
                "payload": json.loads(responseBody["choices"][0]["message"]["content"]),
            }
        )
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/getQuizes", methods=["GET"])
@cross_origin()
def getQuiz():
    if request.method == "GET":
        userQuizes = db.AppGeneratedQuiz.find()

        data_list = []

        for idx, item in enumerate(userQuizes):
            data_list.append(
                {
                    "id": idx + 1,
                    "userId": int(item["user_id"]),
                    "quiz_object": item["quiz_object"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


# @app.route("/appInput/getLeaderboard<id>", methods=["GET"])
# @cross_origin()
# def getLeaderboard(id):
#     if request.method == "GET":
#         userQuizes = db.AppLeaderboard.find()

#         data_list = []

#         for idx, item in enumerate(userQuizes):
#             data_list.append(
#                 {
#                     "id": idx + 1,
#                     "userId": int(item["user_id"]),
#                     "quiz_object": item["quiz_object"],
#                     "timestamp": item["timestamp"],
#                 }
#             )
#         return jsonify({"result": "success", "payload": data_list})
#     else:
#         return jsonify({"result": "fail", "message": "invalid request method"})
