import json
import os

from flask import Flask, request, jsonify
from pathlib import Path
import datetime
import uuid
from db import create_session

from model import Upload, User

UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"


app = Flask(__name__)
session = create_session()


@app.route("/upload", methods=["POST"])
def upload():
    """
    Endpoint for uploading a file.

    Returns:
        str: JSON response with the UID (unique identifier) of the uploaded file.
    """
    # Generate a unique identifier (UID)
    uid = str(uuid.uuid4())

    # Get the uploaded file
    uploaded_file = request.files["file"]

    # Create a filename with the original filename, timestamp, and UID
    filename = f"{uid}.pptx"
    print(filename)

    # Save the file in the uploads folder
    file_path = Path(UPLOADS_DIR) / filename
    uploaded_file.save(file_path)

    timestamp = datetime.datetime.now()

    email = request.form.get("email")
    user = None

    if email:
        # Query the User table for the user with the specified email
        user = session.query(User).filter_by(email=email).first()
        if not user:
            # User not found, create a new user
            user = User(email=email)
            session.add(user)
            session.commit()

    # Create an Upload object and commit it to the database
    uploadd = Upload(uid=uid, filename=filename, upload_time=timestamp, status="pending", user=user)
    session.add(uploadd)
    session.commit()

    # Return the UID as JSON response
    return jsonify({"uid": uid})


@app.route("/status", methods=["GET"])
def status():
    """
    Endpoint for checking the status of a file.

    Args:
        uid (str): The UID (unique identifier) of the file.

    Returns:
        str: JSON response with the status, filename, timestamp, hall name, and explanation.
    """
    uid = request.args.get('uid')
    filename = request.args.get('filename')
    email = request.args.get('email')
    upload = None

    if uid:
        upload = session.query(Upload).filter_by(uid=uid).first()
    elif filename and email:
        user = session.query(User).filter_by(email=email).first()
        upload = (
            session.query(Upload)
            .filter_by(filename=filename, user=user)
            .order_by(Upload.upload_time.desc())
            .first()
        )

    if not upload:
        return jsonify({"error": "Upload not found"}), 404    # Retrieve the status, filename, and timestamp

    status = upload.status
    filename = upload.filename
    timestamp = upload.upload_time
    # Check if the upload has finished processing
    # explanation = ""
    if status == "completed":
        explanation_file = os.path.join(OUTPUTS_DIR, f"{uid}.json")
        if os.path.exists(explanation_file):
            with open(explanation_file, "r") as f:
                explanation_data = json.load(f)

            explanations = []
            for slide_key in explanation_data:
                explanation = explanation_data[slide_key]
                explanations.append(explanation)

            explanation = "\n".join(explanations)
    elif status == "failed":
        explanation = "Processing failed"
    else:
        explanation = "Processing in progress"

    return jsonify({
        "status": status,
        "filename": filename,
        "timestamp": timestamp,
        "explanation": explanation
    }), 200


if __name__ == "__main__":
    # Create the uploads and outputs directories if they don't exist
    Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUTPUTS_DIR).mkdir(parents=True, exist_ok=True)

    # Run the Flask app
    app.run()
