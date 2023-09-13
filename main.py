import os
import json
import requests
import base64
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Set your Mathpix API credentials
app_id = os.environ["MATHPIX_APP_ID"]
app_key = os.environ["MATHPIX_APP_KEY"]

# Process images in the input directory
current_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(current_dir, "input")
output_dir = os.path.join(current_dir, "output")

headers = {
    "app_id": app_id,
    "app_key": app_key,
    "Content-type": "application/json"
}

url = "https://api.mathpix.com/v3/text"

#print number of images in input directory
print("Number of images in input directory: ", len(os.listdir(input_dir)))

for image_name in os.listdir(input_dir):
    image_path = os.path.join(input_dir, image_name)
    
    #print image name 
    print("Processing image: ", image_name)

    # Read the image and encode it in base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Send the image to Mathpix API for processing
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

    # Save the header and JSON response to separate files in the /output folder
    output_json_file = os.path.join(output_dir, f"{image_name}_response.json")

    with open(output_json_file, "w") as json_file:
        json.dump(ocr, json_file, indent=2)

print("Done processing images!")

print("  /\___/\ ")
print(" ( o   o )")
print(" (  =^=  )")
print(" (        )")
print(" (         )))))))))))")
