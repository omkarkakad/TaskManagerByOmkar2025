from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Omkar:Omkar1234@cluster0.yvxxlve.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["taskdb"]
tasks_collection = db["tasks"]

# Helper function to serialize MongoDB documents
def serialize_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "status": task.get("status", "Pending"),
        "priority": task.get("priority", "Medium"),
        "created_date": task.get("created_date"),
        "updated_date": task.get("updated_date")
    }

# View Tasks
@app.route("/show", methods=["GET"])
def get_tasks():
    try:
        tasks = list(tasks_collection.find())
        return jsonify([serialize_task(task) for task in tasks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add Task
@app.route("/save", methods=["POST"])
def add_task():
    try:
        data = request.get_json()
        title = data.get("title")
        if not title:
            return jsonify({"error": "Title is required"}), 400

        status = data.get("status", "Pending")
        priority = data.get("priority", "Medium")
        created_date = updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        task = {
            "title": title,
            "status": status,
            "priority": priority,
            "created_date": created_date,
            "updated_date": updated_date
        }

        result = tasks_collection.insert_one(task)
        return jsonify({"message": "Task Added Successfully", "id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update Task
@app.route("/update/<string:id>", methods=["PUT"])
def update_task(id):
    try:
        data = request.get_json()
        new_title = data.get("title")
        if not new_title:
            return jsonify({"error": "Title is required"}), 400

        status = data.get("status", "Pending")
        priority = data.get("priority", "Medium")
        updated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing_task = tasks_collection.find_one({"_id": ObjectId(id)})
        if not existing_task:
            return jsonify({"error": "Task not found"}), 404

        tasks_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "title": new_title,
                "status": status,
                "priority": priority,
                "updated_date": updated_date
            }}
        )

        return jsonify({"message": "Task Updated Successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete Task
@app.route("/delete/<string:id>", methods=["DELETE"])
def delete_task(id):
    try:
        existing_task = tasks_collection.find_one({"_id": ObjectId(id)})
        if not existing_task:
            return jsonify({"error": "Task not found"}), 404

        tasks_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Task Deleted Successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Test API
@app.route("/")
def home():
    return jsonify({"message": "Task Manager API is Running Successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
