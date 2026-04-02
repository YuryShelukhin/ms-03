import os
import jwt
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET_KEY = 'secret'
users = {}

@app.route('/v1/user', methods=['POST'])
def register():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')
    if not login or not password:
        return jsonify({'error': 'login and password required'}), 400
    if login in users:
        return jsonify({'error': 'user already exists'}), 409
    users[login] = password
    return jsonify({'message': 'user created'}), 201

@app.route('/v1/token', methods=['POST'])
def token():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')
    if login not in users or users[login] != password:
        return jsonify({'error': 'invalid credentials'}), 401
    token = jwt.encode({'sub': login}, SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token}), 200

@app.route('/v1/token/validation/', methods=['GET'])
def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return '', 401
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return '', 200
    except jwt.InvalidTokenError:
        return '', 401

@app.route('/v1/user', methods=['GET'])
def get_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'missing token'}), 401
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        login = decoded['sub']
        return jsonify({'login': login}), 200
    except jwt.InvalidTokenError:
        return jsonify({'error': 'invalid token'}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

import logging
import json
import sys

# Настройка JSON логгера
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "security",
            "message": record.getMessage(),
        }
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        return json.dumps(log_entry)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Использование в коде:
# logger.info("User registered", extra={'request_id': request_id})