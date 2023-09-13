import os
import json
import requests
import base64
import openai
from dotenv import load_dotenv

from openai_helper import send_to_openai_api

openai_test_mode = True

# Load environment variables
load_dotenv()

app_id = os.environ["MATHPIX_APP_ID"]
app_key = os.environ["MATHPIX_APP_KEY"]
openai.api_key = os.environ["OPENAI_API_KEY"]

current_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(current_dir, "input")
output_dir = os.path.join(current_dir, "output")
answers_dir = os.path.join(current_dir, "answers")

# Create /answers directory if it doesn't exist
if not os.path.exists(answers_dir):
    os.makedirs(answers_dir)

headers = {
    "app_id": app_id,
    "app_key": app_key,
    "Content-type": "application/json"
}

url = "https://api.mathpix.com/v3/text"

print("Number of images in input directory:", len(os.listdir(input_dir)))

for image_name in os.listdir(input_dir):
    image_path = os.path.join(input_dir, image_name)
    print("Processing image:", image_name)

    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    payload = {
        "src": f"data:image/jpeg;base64,{image_base64}",
        "formats": ["text", "html"],
        "ocr": ["math", "text"],
        "skip_recrop": True,
        "data_options": {
            "include_latex": True
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    ocr = response.json()

    output_json_file = os.path.join(output_dir, f"{image_name}_response.json")
    with open(output_json_file, "w") as json_file:
        json.dump(ocr, json_file, indent=2)

    if openai_test_mode is True:
        ocr_text = ocr.get("text", "")
        openai_response = send_to_openai_api(ocr_text)

        # Save OpenAI API response to /answers directory
        answer_file_path = os.path.join(answers_dir, f"{image_name}_answer.json")
        with open(answer_file_path, "w") as answer_file:
            json.dump(openai_response, answer_file, indent=2)

        print("OpenAI API response:", openai_response)

print("Done processing images!")
