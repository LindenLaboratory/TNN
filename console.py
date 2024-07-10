#IMPORTS
from lmcl import init,func
import requests
import time
import json
from flask import Flask
import threading
import uuid
import os
import shutil

#SETUP
app = Flask(__name__)
init("openai_api_key")
TOKEN = '6677071432:AAEwnrbm1XTGWDvHimNSMIS5OsMHn751_ws'
COMMANDS={"echo":"Returns your string","help":"Gives a list of commands and what they do","idlst":"Gives a list of the Nodes connected to the network and their TNN IDs","payload": "Gives a list of commands for editing the payload","c":"Edits command in your payload","p":"Edits parameter(s) in your payload","label":"Adds a label to a specific ID","run":"Runs payload on specified ID","result":"Gets the result from a specified ID","res":"See *result*","clear":"Removes all offline nodes","clr":"See *clear*","ai":"Asks your question to TNN AI, and returns the result","log":"Logs the most recent bot message to a specified branch in the TNN database","fetch":"Gets all logs from a specified branch in the TNN database","rm":"Removes a branch from the TNN database","edit":"Open an Ebony Notepad to edit a log","new":"Add a new file to a TNN log branch with Ebony Notepad"}
ERRORS={"404":"Command not found","300":"Syntax Error: . needed at the start of command","303":"Syntax Error: Command not typed correctly","505":"API Error","600":"File not found","605":"Folder not found","606":"Message not found","707":"Node not found","808":"Directory is empty"}
idsdict={}
payload=["scripts","test","Hello World","KEY:6772"]

#FUNCTIONS
def getResult(nodenum):
    try:
        response = requests.get(f"https://host.isaacrichardson.repl.co/result/{nodenum}".strip())
        print(response.json())
        result = response.json()
        r = result['result']
        r = r['result']
        return r
    except Exception as e:
        print(e)
        return "No result found"

@func
def query(question):
    return f"""
instruction {{
Answer "{question}" briefly as TNN, an AI assistant
}}
format {{
TNN: [answer]
}}
rules {{
INCLUDE: =['Correct answers','Wit']
}}
llm {{
LLM: ['gpt-3.5-turbo']
TEMPERATURE: [0.9]
}}
"""

def runPayload(url):
    payloadDict = {
        'module_name': payload[0],
        'function_name': payload[1],
        'arguments': payload[2],
        'key': payload[3]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payloadDict), headers=headers)
    if response.status_code == 200:
        result = response.json()['result']
        print(result)
        return result
    else:
        print('API Error')
        return "Error 505"
        
def send(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode':"markdown"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print("Failed to send message")
        
def evaluate(str_,ID):
    try:
        if "." in str_:
            str_ = str_.split(".")[1]
            if "run" in str_.split('"')[0]:
                print(str_)
                strlst=str_.split('"')
                node=strlst[1].replace('"','')
                send(TOKEN,ID,"Payload sent")
                res_=runPayload(f"https://host.isaacrichardson.repl.co/payload/{node}")
                return res_
            elif "echo" in str_.split('"')[0]:
                result = str_.split('"')[1].replace('"',"")
                return result
            elif "log" in str_.split('"')[0]:
                text = None
                title = str_.split(' ')[1].replace('"',"")
                title_ = str(uuid.uuid4())
                if os.path.exists(f"{ID}.txt"):
                    with open(f"{ID}.txt","r") as f:
                        text = f.read()
                if text:
                    if os.path.exists(title):
                        with open(f"{title}/{title_}.txt","w") as f:
                            f.write(text)
                    else:
                        os.makedirs(title)
                        with open(f"{title}/{title_}.txt","w") as f:
                            f.write(text)
                    return f"Information has been logged in branch *{title}*"
                else:
                    return "Error 606"
            elif "fetch" in str_.split('"')[0]:
                dirpath = str_.split(' ')[1].replace('"',"")
                msglst = []
                num = 0
                if os.path.exists(dirpath):
                    for filename in os.listdir(dirpath):
                        num = num + 1
                        if os.path.isfile(f"{dirpath}/{filename}"):
                            with open(f"{dirpath}/{filename}","r") as f:
                                log_ = f.read()
                                filename = filename.replace(".txt","")
                                msglst.append(f"{num}. *{filename}*\n{log_}")
                else:
                    return "Error 605"
                if len(msglst) > 0:
                    return msglst
                else:
                    return "Error 808"
            elif "rm" in str_.split('"')[0]:
                dir = str_.split('"')[1].replace('"',"")
                shutil.rmtree(dir)
                return f"Log *{dir}* removed"
            elif "ai" in str_.split('"')[0]:
                question = str_.split('"')[1].replace('"',"")
                send(TOKEN,ID,"TNN is thinking...")
                return query(question).result.replace("```","*")
            elif "clr" in str_.split('"')[0] or "clear" in str_.split('"')[0]:
                response = requests.get("https://host.isaacrichardson.repl.co/ip/get")
                addresses = response.json()
                addresslist = addresses['result']
                for address in addresslist:
                    requests.get(f"https://host.isaacrichardson.repl.co/close/{address}".strip())
                if len(addresslist) > 0:
                    return "Offline Nodes shutdown"
                else:
                    return "Error 707"
            elif "label" in str_.split('"')[0]:
                cmd,id,space,label,space2=str_.split('"')
                idsdict[id] = label
                return f"ID {id} set to label {label}"
            elif "res" in str_.split('"')[0]:
                strlst = str_.split('"')
                node = strlst[1].replace('"','')
                res =getResult(node)
                return f"*Result:*\n{res}"
            elif "payload" in str_.split('"')[0]:
                return 'Set Command with *.c "{command}"* or set Parameters with *.p "{parameter1},{parameter2}"*'
            elif str_.split('"')[0].strip() == "c":
                cmd = str_.split('"')[1].replace('"',"")
                payload[1] = cmd
                print(f"Current payload:\n{payload}")
                return f"Command set to *{cmd}*"
            elif str_.split('"')[0].strip() == "p":
                params = str_.split('"')[1].replace('"',"")
                payload[2] = params.split(",")
                print(f"Current payload:\n{payload}")
                return f"Parameters set to *{params}*"
            elif "idlst" in str_.split('"')[0]:
                result = "IDs:\n"
                response = requests.get("https://host.isaacrichardson.repl.co/ip/get")
                addresses = response.json()
                addresslist = addresses['result']
                if len(addresslist) > 0:
                    for id in addresslist:
                        if str(id) in idsdict:
                            lbl = idsdict[str(id)]
                            result = result + f"{id} | {lbl}"
                        else:
                            result = result + f"{id}"
                else:
                    result = ["No IDs found","No nodes online"]
                return result
            elif "edit" in str_.split('"')[0]:
                strlst = str_.split('"')
                logfolder_,logtitle_=strlst[1],strlst[3]
                logtxt_="^&^"
                if os.path.exists(logfolder_):
                    for filename in os.listdir(logfolder_):
                        print(filename,logtitle_)
                        if filename.replace(".txt","") == logtitle_:
                            with open(f"{logfolder_}/{logtitle_}.txt","r") as f:
                                logtxt_ = f.read()
                else:
                    return "Error 605"
                if logtxt_ == "^&^":
                    return "Error 600"
                else:
                    lnk=f"https://ebony.isaacrichardson.repl.co/{logfolder_}&{logtitle_}&{logtxt_}"
                    return f"Click [here]({lnk}) to edit the log in Ebony Notepad"
            elif "new" in str_.split('"')[0]:
                str__ = str_.split('"')[1]
                lnk=f"https://ebony.isaacrichardson.repl.co/new/{str__}"
                return f"Click [here]({lnk}) to create and edit a log in Ebony Notepad"
            elif "help" in str_.split('"')[0]:
                result = "*Commands*:\n"
                for command,explaination in COMMANDS.items():
                    result = result + f"_{command}_: {explaination}\n"
                result_ = "*Error Codes:*\n"
                for error,explaination in ERRORS.items():
                    result_ = result_ + f"_{error}_: {explaination}\n"
                return [result,result_]
            else:
                return "Error 404"
        elif str_ == "/start":
            return ["TNN Console Online","Use *.help* to get commands and error messages and *.idlst* to get a list of online nodes"]
        else:
            return "Error 300"
    except Exception as e:
        print(f"Error: {e}")
        return "Error 303"
