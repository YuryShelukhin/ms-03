import os
import uuid
import io
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error

app = Flask(__name__)

MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'images')

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

@app.route('/v1/upload', methods=['POST'])
def upload():
    file_data = request.get_data()
    if not file_data:
        return jsonify({'error': 'no file'}), 400

    filename = f"{uuid.uuid4()}.jpg"
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
        client.put_object(
            MINIO_BUCKET,
            filename,
            data=io.BytesIO(file_data),
            length=len(file_data),
            content_type='image/jpeg'
        )
    except S3Error as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'filename': filename}), 200

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