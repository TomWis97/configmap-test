from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    try:
        background_color = os.environ["APP_COLOR"]
    except:
        background_color = "#aaaaaa"
    return render_template("index.html", background_color=background_color)

@app.route("/update", methods=["POST"])
def update():
    new_color = request.form['color']
    regex = r"^#[0-z]{3,6}$"
    if not re.match(regex, new_color):
        abort(400)
    return "Updating value to: " + new_color
