from flask import Flask, request, jsonify
from pathlib import Path
import datetime
import uuid

UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"


app = Flask(__name__)


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
    filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uid}_{uploaded_file.filename}"
    print(filename)

    # Save the file in the uploads folder
    file_path = Path(UPLOADS_DIR) / filename
    uploaded_file.save(file_path)

    # Return the UID as JSON response
    return jsonify({"uid": uid})


@app.route("/status/<uid>", methods=["GET"])
def status(uid):
    """
    Endpoint for checking the status of a file.

    Args:
        uid (str): The UID (unique identifier) of the file.

    Returns:
        str: JSON response with the status, filename, timestamp, hall name, and explanation.
    """
    # Check if the file exists in the uploads folder
    file_path = next(Path(UPLOADS_DIR).glob(f"*_{uid}_*"), None)
    print(file_path)
    if file_path is None:
        # File not found
        return jsonify({
            "status": "not found",
            "filename": None,
            "timestamp": None,
            "hall_name": None,
            "explanation": None
        }), 404
    else:
        # Extract the filename, timestamp, and generate the output file path
        filename_parts = file_path.stem.split("_")
        original_filename = "_".join(filename_parts[2:])
        timestamp = filename_parts[0]

        # Extract the hall name from the original filename
        hall_name = original_filename.split("_")[0]

        output_file_path = next(Path(OUTPUTS_DIR).glob(f"*_{uid}_*.json"), None)
        print(output_file_path)

        if output_file_path.exists():
            # File has been processed, read the explanations from the output file
            with open(output_file_path, "r") as file:
                explanations = file.read()

            return jsonify({
                "status": "done",
                "filename": original_filename,
                "timestamp": timestamp,
                "hall_name": hall_name,  # Include the hall name in the response
                "explanation": explanations
            })
        else:
            # File is still pending processing
            return jsonify({
                "status": "pending",
                "filename": original_filename,
                "timestamp": timestamp,
                "hall_name": hall_name,  # Include the hall name in the response
                "explanation": None
            })


if __name__ == "__main__":
    # Create the uploads and outputs directories if they don't exist
    Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)
    Path(OUTPUTS_DIR).mkdir(parents=True, exist_ok=True)

    # Run the Flask app
    app.run()
