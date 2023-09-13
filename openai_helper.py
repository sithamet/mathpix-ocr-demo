import openai


def send_to_openai_api(text):
    wrapped_text = (f"I've scanned the following question using OCR technology. Please help me find the correct "
                    f"answers. Note that the OCR process might have introduced some inaccuracies or approximations in "
                    f"the text such as incorrect letters, missing words, or jumbled sentences. If anything seems "
                    f"weird, please deduce the most probable input. If the question is too distorted or unclear for "
                    f"you to provide an accurate answer, ask me to double-check and provide clarification.\n\nYour "
                    f"responses should be in clear, correct language, despite any inaccuracies in the original OCR "
                    f"text. Here is the input:\n\n{text}")

    system_prompt = ("You are an AI input validator. You read the input and tell  if it's valid. Describe the input "
                     "you see, including math. Comment on math format. Don't do any math, work or anything requested "
                     "in input")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": wrapped_text},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.3,
    )
    return response.choices[0].message['content'].strip()

