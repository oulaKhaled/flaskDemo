import pathlib
from flask import Flask, session, render_template, request, redirect, abort
import pyrebase
import settings
from Oauth import Oauth
import os
from firestore2 import firestore2, home

app = Flask(__name__)

app.register_blueprint(Oauth, url_prefix="")
app.register_blueprint(firestore2, url_prefix="")


firebaseConfig = settings.firebaseConfig
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
## when we want to access a session id we need to use an ecryption key which is signed as secret key
app.secret_key = "secret"


##Email and password Authentication
@app.route("/login", methods=["POST", "GET"])
def index():
    error_message = ""
    title = "login"
    if "user" in session:
        return home()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = email
            return home()
        except:
            error_message = "something went wrong"
    return render_template(
        "loginpage.html", title=title, route="index", error_message=error_message
    )


@app.route("/register", methods=["POST", "GET"])
def register():
    error_message = ""
    title = "register"
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirmpassword")
        try:
            if password != confirmpassword:
                error_message = "Passwords do not Match , Please try agine"
            user = auth.create_user_with_email_and_password(email, password)
            session["user"] = email
            return home()

        except ValueError as ve:
            error_message = "the password should contain at least 6 characters"

    return render_template(
        "loginpage.html", title=title, route="register", error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
