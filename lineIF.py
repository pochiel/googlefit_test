
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

class lineIF:
    def __init__(self):
        #環境変数取得
        self.YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
        self.YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
        self.YOUR_USER_ID = os.environ["YOUR_USER_ID"]
        self.line_bot_api = LineBotApi(self.YOUR_CHANNEL_ACCESS_TOKEN)

    def send_message(self, message):
        self.line_bot_api.push_message(self.YOUR_USER_ID, messages=TextSendMessage(text=message))
