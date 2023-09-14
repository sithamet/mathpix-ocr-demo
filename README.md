# README

This repo contains code to extract math equations from images using Mathpix API and generate explanations for the steps using OpenAI API.

## Prerequisites

- Python 3.7+
- Pip
- Virtualenv (optional)

## Installation

1. Clone the repo:

```
git clone https://github.com/username/repo-name.git
```
2. (Optional) Create and activate a virtual environment:

```
virtualenv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate
````
3. Install the requirements
   
```
pip install -r requirements.txt
```

4. Create a .env file with your API keys:
```
MATHPIX_APP_ID=YOUR_APP_ID
MATHPIX_APP_KEY=YOUR_APP_KEY
```

If you want immediately test if GPT understands the output, add

```
OPENAI_API_KEY=YOUR_API_KEY
```

5. Run the code:
6. 
```
python main.py
```
This will process all images in the  `input`  folder and save the responses in the  `output`  and  `answers`  folders.

To test in OpenAI test mode, set  `openai_test_mode = True`  in  `main.py` . This will send requests to OpenAI's test API endpoint.

Let me know if you have any other questions!
