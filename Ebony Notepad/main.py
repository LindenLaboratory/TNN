#FUNCTIONS
from flask import Flask, render_template, request, jsonify
import requests

#SETUP
app = Flask(__name__)
log,title,text = "","",""
#FUNCTIONS
@app.route("/")
def home():
    return "Ebony Notepad Online"
@app.route('/<string:log_>&<string:title_>&<string:text_>')
def edit(log_,title_,text_):
    global log,title,text
    log,title,text = log_,title_,text_
    print(log,title,text)
    return render_template('index.html',text=text,title=title)
@app.route('/new/<string:log_>')
def new(log_):
    global log
    log = log_
    print(f"%*{log}*%")
    return render_template('index.html',text="",title="")

@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    print(f"Title:{title}\nContent:{content}")
    result = requests.get(f"https://console.isaacrichardson.repl.co/ebony/{title}&{content}&{log}")
    print(result)
    response = {"message": "Data received successfully"}
    return jsonify(response), 200

#RUN
app.run("0.0.0.0")
