from flask import Flask, Blueprint, redirect, request, render_template, session
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import logging
from Oauth import login_required


firestore2 = Blueprint("firestore", __name__, template_folder="Template")
# set up the necessary authentication and initialization steps to connect a Python application to Firebase Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


#############///GETTING / ADDING / REMOVING DATA/ UPDATING /#########
@firestore2.route("/task", methods=["POST", "GET"])
@login_required
def addTask():
    if request.method == "POST":
        task = request.form.get("task_input")
        data = {"task": task, "status": "TODO"}
        db.collection("tasks").add(data)
    return home()


@firestore2.route("/", methods=["GET", "POST"])
def home():
    if not "user" in session:
        return redirect("login")
    doc_list = []
    docs = db.collection("tasks").stream()
    doc_list = []
    try:
        for doc in docs:
            doc_list.append(doc.to_dict().get("task"))
    except:
        print("sorry we couldn't find your document")
    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            li = request.form.get("doc_id")
            query = db.collection("tasks").where("task", "==", li).stream()
            for doc in query:
                doc.reference.delete()
                return redirect("/")
        elif action == "update":
            # update data-unknown key
            li = request.form.get("doc_id")
            updated_input = request.form.get("update_input")
            new = db.collection("tasks").where("task", "==", li).stream()

            for doc in new:
                key = doc.id
                db.collection("tasks").document(key).update({"task": updated_input})

            print(f"update butoon is pressed li is {li}")

    return render_template("home.html", doc_list=doc_list)
