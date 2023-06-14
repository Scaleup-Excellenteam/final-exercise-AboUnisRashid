import aiohttp
import asyncio

API_BASE_URL = "http://localhost:5000"  # Replace with the appropriate base URL


async def upload_file(file_path):
    """
    Asynchronously uploads a file to the server.

    Args:
        file_path (str): The path to the file to be uploaded.

    Returns:
        str: The UID (unique identifier) of the uploaded file.
    """
    upload_url = f"{API_BASE_URL}/upload"

    async with aiohttp.ClientSession() as session:
        # Open the file in binary mode and send it as multipart/form-data
        async with session.post(upload_url, data=aiohttp.FormData({"file": open(file_path, "rb")})) as response:
            if response.status == 200:
                data = await response.json()
                uid = data["uid"]
                print(f"File uploaded successfully. UID: {uid}")
                return uid
            else:
                print("Error uploading file.")
    return None


async def check_status(uid):
    """
    Asynchronously checks the status of a file until the explanation is ready.

    Args:
        uid (str): The UID (unique identifier) of the file.

    Returns:
        None
    """
    status_url = f"{API_BASE_URL}/status/{uid}"
    print(uid)
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(status_url) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data["status"]
                    if status == "done":
                        filename = data["filename"]
                        timestamp = data["timestamp"]
                        explanation = data["explanation"]
                        print("File processed:")
                        print(f"  Filename: {filename}")
                        print(f"  Timestamp: {timestamp}")
                        print(f"  Explanation: {explanation}")
                        break  # Exit the loop when the explanation is ready
                    elif status == "pending":
                        print("File is still being processed.")
                    elif status == "not found":
                        print("File not found.")
                else:
                    print("Error checking file status.")
                await asyncio.sleep(1)  # Wait for 1 second before checking again


async def main():
    """
    Asynchronous main function that uploads a file and checks its status.
    """
    file_path = "Presentation_path"

    # Upload the file asynchronously
    uid = await upload_file(file_path)

    # Check the status of the file asynchronously until the explanation is ready
    await check_status(uid)


if __name__ == "__main__":
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the main function asynchronously until completion
    loop.run_until_complete(main())
