import praw

reddit = praw.Reddit(
    client_id='{APP_ID}',
    client_secret="{APP_SCRETER}",
    password="{ACCOUNT_PASSWORD}",
    user_agent="Server Utils discord bot",
    username="{ACCOUNT_USERNAME}"
)
