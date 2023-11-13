from flask import Flask, request, jsonify, render_template_string
import boto3
import io
from dotenv import load_dotenv
import os
import requests
import redis

load_dotenv()

app = Flask(__name__)


BUCKET_NAME = os.environ.get("BUCKET_NAME")

ACCOUNT_ID = os.environ.get("ACCOUNT_ID")

WORKER_URL = os.environ.get("WORKER_URL")

ENDPOINT_URL = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"
# R = redis.Redis(host='localhost', port=6379, decode_responses=True)

REDIS_URL = os.getenv("REDIS_URL")
R: redis.Redis = redis.from_url(REDIS_URL, decode_responses=True)

print(ENDPOINT_URL)


s3 = boto3.client(
    service_name="s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),  # "<access_key_id>",
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name="auto"
)
os.getenv("ENDPOINT_URL"),

# utilities functions


def generate_signed_url(filename):
    # Generate a presigned URL for the S3 object
    try:
        headers = {
            'X-Custom-Auth-Key':  'TEST-AUTH-KEY'
        }
        url = f"{WORKER_URL}/{filename}"
        data = requests.post(
            url,
            headers=headers
        )
        print(data.json())
        return data.json()
    except Exception as e:

        app.logger.error(f"=====> Error  {e} while getting   signed  url")
        return None


def get_file(filename):
    # Get object information
    object_information = s3.head_object(Bucket=BUCKET_NAME, Key=filename)
    return object_information


def download_file(filename):
    # Get object from S3 Object Storage
    object = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    # Read data from the S3 object
    object_data = object['Body'].read()

    # If the filename has a path, create the path
    if '/' in filename:
        # Extract the directory path from the filename
        directory = os.path.dirname(filename)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Write the data to a file
    with open(filename, 'wb') as file:
        file.write(object_data)

    return f"File downloaded successfully: {filename}"


def delete_file(filename):
    # Delete object
    s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    return f"File deleted successfully: {filename}"

# flask endpoints


@app.route("/signed-url/<path:filename>", methods=["GET", "POST"])
def signed_url(filename):
    data = generate_signed_url(filename)
    if not data:
        return jsonify({"error": "Something   went   wrong  please try again"}), 400

    url = data.get("signed_url")
    filename = data.get("filename")
    R.set(filename, url)  # we will get it later  in the callback
    return jsonify({
        "upload_url": url,
        "filename": filename
    }), 200


@app.post("/callback",)
def callback():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json(force=True)
            print(data)
            filename = data.get("filename")
            if not filename:
                return jsonify({"error": "Filename  is required"}), 400
            # lets check if the  key exists  in the redis  store
            url = R.get(filename)
            if not url:
                return jsonify({"error": "Filename   not found in redis cache"}), 400
            # lets download   file from  r2 bucket an delete it
            object_information = get_file(filename)
            if not object_information:
                return jsonify({"error": "File  not found in R2b ucket"}), 400
            print(object_information)

            # lets download  the file
            download_msg = download_file(filename)

            # lets delete  the file
            delete_msg = delete_file(filename)

            # let remove filename from cache
            R.unlink(filename)

            return jsonify({
                "message": download_msg,
                "filename": filename,

            }), 200
        else:
            return jsonify({"error": "Invalid   data json data required"}), 400


@app.route('/', methods=['GET', 'POST'])
def index():
    # print(request.headers)
    R.set("foo", "bare4546 65y45htr")
    R.set("new-foo", "new  foo")
    # R.unlink("foo")
    print(R.get("foo"))
    if request.is_json:
        print(request.get_json(force=True))
        return jsonify({'message': 'JSON received!'}), 200
    return 'Hello World!'


# error handling

@app.errorhandler(404)
def not_found_error(error):
    return render_template_string("ERROR 404 Page Doesn't Exist")


@app.errorhandler(405)
def method_not_found_error(error):
    return render_template_string("ERROR 405 Method Not Allowed")


@app.errorhandler(500)
def internal_server_error(error):
    return render_template_string("ERROR 500 Internal Server Error")


if __name__ == '__main__':
    app.run(debug=True)
