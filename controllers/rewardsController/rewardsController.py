# from models.userChats import user_chats
from app import app, request, db
from flask import json, jsonify
from datetime import datetime
from flask_cors import cross_origin
import datetime
import requests
import openai
import uuid
import os
import re


@app.route("/appInput/Quiz/userScore", methods=["POST"])
@cross_origin()
def userQuizScore():
    rewardPoints = 0
    if request.method == "POST":
        quizRewardSetting = db.userQuizRewardsSettings.find()

        for idx, item in enumerate(quizRewardSetting):
            rewardPoints = item["user_points"]

        userQuizRewards = int(request.form["score"]) * int(rewardPoints)

        print("user rewards are ", userQuizRewards)
        point_rewards = {
            "points": userQuizRewards,
            "user_id": request.form["userId"],
            "member_id": request.form["memberId"],
            "customer_id": request.form["customerId"],
            "user_name": request.form["userName"],
            "device": request.form["device"],
            "activity": request.form["activity"],
            "timestamp": datetime.datetime.now(),
        }
        db.userQuizRewards.insert_one(point_rewards)
        return jsonify({"result": "success", "message": "Points Rewarded Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/Roulette/userScore", methods=["POST"])
@cross_origin()
def userRouletteScore():
    rewardPoints = 0
    if request.method == "POST":
        rouletteRewardSetting = db.userRouletteRewardsSettings.find()

        for idx, item in enumerate(rouletteRewardSetting):
            rewardPoints = item["user_points"]

        userRouletteRewards = int(request.form["score"]) * int(rewardPoints)

        print("user rewards are ", userRouletteRewards)
        point_rewards = {
            "points": userRouletteRewards,
            "user_id": request.form["userId"],
            "member_id": request.form["memberId"],
            "customer_id": request.form["customerId"],
            "user_name": request.form["userName"],
            "device": request.form["device"],
            "activity": request.form["activity"],
            "timestamp": datetime.datetime.now(),
        }
        db.userRouletteRewards.insert_one(point_rewards)
        return jsonify({"result": "success", "message": "Points Rewarded Succesfully"})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})


@app.route("/appInput/getUserPoints/id", methods=["GET"])
@cross_origin()
def getUserPoints():
    if request.method == "POST":
        query = {"user_id": int(id)}
        userPoints = db.userPoints.find(query)

        data_list = []

        for idx, item in enumerate(userPoints):
            data_list.append(
                {
                    "id": idx + 1,
                    "activity": item["activity"],
                    "points": item["points"],
                    "user_id": item["user_id"],
                    "timestamp": item["timestamp"],
                }
            )
        return jsonify({"result": "success", "payload": data_list})
    else:
        return jsonify({"result": "fail", "message": "invalid request method"})
