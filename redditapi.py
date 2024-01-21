import asyncpraw
from decouple import config

async def get_reddit():
    return asyncpraw.Reddit(
        client_id=config('REDDIT_CLIENT_ID'),
        client_secret=config('REDDIT_CLIENT_SECRET'),
        user_agent=config('REDDIT_USER_AGENT')
    )

async def search_reddit(query):
    async with asyncpraw.Reddit(client_id=config('REDDIT_CLIENT_ID'),
                                client_secret=config('REDDIT_CLIENT_SECRET'),
                                user_agent=config('REDDIT_USER_AGENT')) as reddit:
        subreddit = await reddit.subreddit("UCSC")
        posts = []
        async for submission in subreddit.search(query, limit=10):
            posts.append({
                'title': submission.title,
                'url': submission.url,
                'text': submission.selftext
            })
    return posts