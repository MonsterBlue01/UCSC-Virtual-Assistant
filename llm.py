
import openai
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


def handle_response(question, conversation_history, user_id):

    # Read search results from the JSON file and append each as a separate message
    json_name = f'scraped_data_{user_id}.json'
    formatted_history = [{"role": "system", "content": "Provide succinct, subjective advice for UCSC students based on the given question and information."},
                         {"role": "user", "content": question}]
    
    # Previous assistant messages
    for convo in conversation_history:
        formatted_history.append({"role": "assistant", "content": convo})

    try:
        with open(json_name, 'r') as file:
            search_results = json.load(file)
            for result in search_results:
                formatted_message = json.dumps(result, ensure_ascii=False, indent=4)
                formatted_history.append({"role": "assistant", "content": formatted_message})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error reading from {json_name}: {e}")

    # debugging
    with open('formatted_data.json', 'w', encoding='utf-8') as f:
        json.dump(formatted_history, f, ensure_ascii=False, indent=4)

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_history
        )
        return completion.choices[0].message.content if completion.choices else "No response generated from OpenAI."
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {e}")
        return "An error occurred while processing the request."


