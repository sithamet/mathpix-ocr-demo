import os
import json
import requests
import csv
from dotenv import load_dotenv
import openai_helper

# Load environment variables
load_dotenv()

# Set test mode to True to limit the number of images processed
test_mode = True
limit = 10
counter = 0  # Moved the counter initialization outside of the loop

app_id = os.environ["MATHPIX_APP_ID"]
app_key = os.environ["MATHPIX_APP_KEY"]

headers = {
    "app_id": app_id,
    "app_key": app_key,
    "Content-type": "application/json"
}

url = "https://api.mathpix.com/v3/text"

# Read URLs from CSV
csv_path = 'input/chats.csv'
csv_output_path = 'output/chats.csv'

# Define the columns to be included in the output CSV
output_columns = ['user_id', 'chat_id', 'chat_created_at', 'prompt_attachment', 'OCR_result', 'OCR_confidence',
                  'OCR_confidence_rate', 'is_handwritten', 'is_printed', 'subject', 'nature', 'nature_detailed']

with open(csv_path, mode='r', encoding='utf-8') as infile, open(csv_output_path, mode='w', newline='',
                                                                encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=output_columns)
    writer.writeheader()

    for row in reader:
        if test_mode and counter >= limit:
            print("Test mode limit reached. Stopping.")
            break

        image_url = row['prompt_attachment']

        if not image_url:  # Skip empty or None URLs
            print("Skipping empty URL")
            continue

        print(f"Processing image URL: {image_url}")

        # Prepare payload for API request
        payload = {
            "src": image_url,
            "formats": ["text"],
            "confidence_threshold": 0,
            "confidence_rate_threshold": 0,
            "data_options": {
                "include_latex": True
            }
        }

        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        ocr = response.json()

        # Analyze the OCR result
        result = ocr.get('text', '')
        system_prompt = """You are an intelligent academic analysis system. Your work with OCR results and deduce the 
        subject and nature of the picture.
        
        In response to a student's question, you must answer with a pseudo-JSON formatted response with ALL parameters from 
        the list below. 
        
        ## Nature detailed 
            What can this picture display? Is it a book of a page, a handwritten equation, or a quiz photo? Reason it out, 
            use chain of thought method to deduce. 
            
        ## Nature short 
            Select the one and only one most-suiting nature of this chat log. Possible values are, but not limited too: 
            book page, website, newsletter, quiz photo. Choose yourself if you think there is another option. 
        
        ## Subject
            Select the one and only one most-suiting subject of this chat log from the list: Economics, Finance, Accounting and Banking, 
            Chemistry, English, Statistics, Engineering, Maths, Physics, Computer Science, Philosophy, IT (coding), Culture, 
            Business and Management, Marketing and PR, Law and International Law, Other, Religion, History and Anthropology, 
            Biology and Life Sciences, Environmental Science, Psychology, Education, Linguistics, Healthcare and Nursing, 
            Political Science, Sociology, Art, Literature, Music, Design and Architecture, HRM.
            
            Avoid using "Other" if possible. Try to deduce: e.g. if the chat is about a book, it's literature, and if it's about 
            a country, it's History and Anthropology. If it's about a person, it's Psychology. 
        
        Format all parameters you choose as a pseudo-JSON array. Reply only with that array.
        
        ## Example
        ```
          {
            "nature_detailed": "The picture displays a set of pre-laboratory questions, likely from a quiz or an assignment. The content is typed, not handwritten, and contains chemical formulas, suggesting it's from a scientific subject.",
            "nature_short": "quiz photo",
            "subject": "Chemistry"
          }
        ```
        """
        user_input = result
        user_prompt = """I've scanned the following question for the quiz using OCR technology. Please help me deduce 
        the subject and nature of the question."""

        retries = 5
        success = False

        while retries > 0 and not success:
            try:
                analysis = openai_helper.make_ai_request(system_prompt=system_prompt, user_input=user_input, user_prompt=user_prompt, model="gpt-4")

                # Pre-process to remove array brackets if necessary
                if analysis.startswith('[') and analysis.endswith(']'):
                    analysis = analysis[1:-1].strip()

                # Try to parse the JSON
                data = json.loads(analysis, object_hook=dict)

                # Validate the schema of the JSON
                required_keys = ['nature_detailed', 'nature_short', 'subject']
                if all(key in data for key in required_keys):
                    print("Analysis result is valid")
                else:
                    print("Analysis result is invalid")
                    retries -= 1
                    continue

                # Create a new dictionary with only the fields we care about
                output_row = {key: row[key] for key in output_columns if key in row}

                # Save relevant details in the CSV
                output_row['OCR_result'] = ocr.get('text', '')
                output_row['OCR_confidence'] = ocr.get('confidence', '')
                output_row['OCR_confidence_rate'] = ocr.get('confidence_rate', '')
                output_row['is_handwritten'] = ocr.get('is_handwritten', '')
                output_row['is_printed'] = ocr.get('is_printed', '')
                output_row['subject'] = data.get('subject', '')
                output_row['nature'] = data.get('nature_short', '')
                output_row['nature_detailed'] = data.get('nature_detailed', '')

                writer.writerow(output_row)
                success = True  # Mark the operation as successful to break the loop
                break

            except Exception as e:
                print(f"An error occurred: {e}")
                retries -= 1  # Decrease the retry counter

                print("Skipping this image.")
                continue

        if not success:
            print("Maximum retries reached. Skipping this image.")

        counter += 1  # Increment the counter after each processed image

print("Done processing images!")

# Log token usage
openai_helper.log_token_usage()
