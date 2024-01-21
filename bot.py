import os
import discord
import websearch
import webscraping
import llm
from dotenv import load_dotenv
import json
import redditapi
import logging
import openai
import re

# Global dictionary to store conversation history for each user
conversation_history = {}

logging.basicConfig(level=logging.INFO)

async def scrape_links(links, max_links=7):
    scraped_data = []
    additional_links_index = 0
    try:
        while len(scraped_data) < max_links and additional_links_index < len(links):
            link = links[additional_links_index]
            try:
                data = webscraping.scrape(link)
                if data['text'] != 'No main content could be extracted.':
                    scraped_data.append(data)
            except Exception as e:
                logging.error(f"Error scraping link: {e}")
            additional_links_index += 1
    except Exception as e:
        logging.error(f"Error in scrape_links: {e}")
    return scraped_data

async def reply_message(message, openai_response):
    try:
        user_id = message.author.id
        conversation_history.setdefault(user_id, [])

        query = ' '.join([word for word in message.content.split() if not word.startswith('<@')])
        logging.info(f"Searching internet for: {query}")
        
        links = websearch.search_google(query)
        # reddit_results = await redditapi.search_reddit(query)

        # reddit_formatted_results = []
        # for post in reddit_results:
        #     reddit_formatted_results.append(f"Title: {post['title']}\nURL: {post['url']}\nText: {clean_text(post['text'][:500])}")
        # reddit_response = '\n'.join(reddit_formatted_results) if reddit_formatted_results else "No Reddit results."

        # google_response = "No Google results."
        scraped_content = []
        scraped_content = await scrape_links(links)
        # google_response = format_scraped_content(scraped_content)

        # combined_response = f"Google Results:\n{google_response}\n\nReddit Results:\n{reddit_response}"
        combined_content = scraped_content #+ reddit_response

        for item in combined_content:
            item['text'] = filter_text(item['text'])
            item['title'] = filter_text(item['title'])

        # Save the actual scraped content to file, not the combined response
        json_filename = f'scraped_data_{user_id}.json'
        save_to_json(combined_content, json_filename) 

        openai_response = llm.handle_response(query, conversation_history[user_id], user_id)
        openai_response = truncate_response(openai_response, 2000)

        conversation_history[user_id].append(openai_response)
        await message.channel.send(openai_response)

    except Exception as err:
        logging.error(f"Error replying to message: {err}")
        await message.channel.send("An error occurred while processing your request.")


def truncate_response(response, max_length):
    return response[:max_length - 5] + "\n..." if len(response) > max_length else response


def format_scraped_content(content, total_max_length=3000):
    formatted_content = []
    current_length = 0

    for item in content:
        text_snippet = item['text'][:500] + '...' if len(item['text']) > 500 else item['text']
        formatted_item = f"Title: {item['title']}\nURL: {item['url']}\nText: {text_snippet}"

        if current_length + len(formatted_item) > total_max_length:
            break  # Stop adding more items if the total limit is exceeded

        formatted_content.append(formatted_item)
        current_length += len(formatted_item)

    return '\n\n'.join(formatted_content) if formatted_content else "Scraping failed."



def save_to_json(scraped_data, filename):
    try:
        # Ensure the directory exists, create if not
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)

        # Debug print
        logging.info(f"Saving scraped data to {filename}")

        # Filtering out 'No main content could be extracted.'
        filtered_data = [item for item in scraped_data if item['text'] != 'No main content could be extracted.']

        # Writing to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Error in save_to_json: {e}")


def run_discord_bot(client):
    @client.event
    async def on_ready():
        print(f'{client.user} is now online!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        print(f"{message.author} in {message.channel}: {message.content}")
        # msg from server
        if client.user in message.mentions:
            async with message.channel.typing():
                response = "Search Failed."
                await reply_message(message, response)

        elif message.guild is None:
        # direct message
            async with message.channel.typing():
                response = "Search Failed."
                await reply_message(message, response)

def filter_text(text):
    # Remove language list
    text = re.sub(r'\d{2} languages[^\]]*\]', '', text, flags=re.DOTALL)
    # Remove coordinates
    text = re.sub(r'Coordinates:.*?\/\d+\.\d+;', '', text, flags=re.DOTALL)
    sections_to_remove = ['Edit links', 'ArticleTalk', 'ReadEditView history', 'Tools', 'General', 
                          'What links here', 'Related changes', 'Upload file', 'Special pages', 
                          'Permanent link', 'Page information', 'Cite this page', 'Get shortened URL', 
                          'Wikidata item', 'Print/export', 'Download as PDF', 'Printable version', 
                          'In other projects', 'Wikimedia Commons', 'New comments cannot be posted.',
                          ' - Dive into anything', 
                        ]
    for section in sections_to_remove:
        try:
            text = re.sub(rf'{section}.*?(?=\w+:|\Z)', '', text, flags=re.DOTALL)
        except re.error as e:
            logging.error(f"Regex error with pattern '{section}': {e}")
    
    text = truncate_response(text, 800)

    return text.strip()

# run the bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)
run_discord_bot(client)
load_dotenv()
client.run(os.getenv('TOKEN'))
openai.api_key = os.getenv('OPENAI_KEY')
