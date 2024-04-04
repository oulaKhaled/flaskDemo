from flask import Flask, Blueprint
import pyrebase
import os
from google_auth_oauthlib.flow import Flow
import requests
import google.auth.transport.requests
from flask import Flask, session, render_template, request, redirect, abort
import pathlib
from cachecontrol import CacheControl
from google.oauth2 import id_token
from google.auth.transport import requests
import requests
import settings

Oauth = Blueprint("Oauth", __name__, template_folder="Templates")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# protect application from unauthorized users
def login_required(function):
    def wrapper(*arg, **kwargs):
        if "user" not in session:
            return abort(401)
        else:
            return function()

    return wrapper


@Oauth.route("/logout")
def logout():
    session.clear()

    return redirect("/")


#################Google Authentication###############

client_secrets_files = os.path.join(pathlib.Path(__file__).parent, "client.json")
# initialized with parameters, These parameters define how the OAuth flow will be conducted.
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_files,
    scopes=settings.scopes,
    redirect_uri=settings.redirect_uri,
)


# it initiates the Google OAuth
@Oauth.route("/logingoogle")
def login_google():
    # generates an authorization URL using the flow
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


# After the user authenticates via Google , Google redirects the user back to this endpoint with an authorization code.
@Oauth.route("/callback", methods=["GET"])
def callback():
    # extracts the authorization code,exchanges it for an access token
    flow.fetch_token(authorization_response=request.url)
    # to prevent CSRF attacks
    if session["state"] != request.args["state"]:
        abort(500)
    # after tokens are retrieved, they are stored
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    # method to verify the ID token received from Google.
    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=settings.GOOGLE_CLIENT_ID,
    )
    ##extracts user information from the ID token, such as the user's unique identifier (sub) and name (name).
    ##It stores this information in the user's session for future use.
    session["user"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    print(f"session {session}")
    return redirect("/")
