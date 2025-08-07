from flask import Flask, request
import requests
import dropbox
import os
import hashlib
from linebot import LineBotApi
from linebot.models import TextSendMessage
import openai

# --- 環境変数 ---
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PARTNER_UPDATE_URL = os.getenv("PARTNER_UPDATE_URL")

# --- 初期化 ---
app = Flask(__name__)
dbx = dropbox.Dropbox(
    oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    app_key=DROPBOX_APP_KEY,
    app_secret=DROPBOX_APP_SECRET
)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai.api_key = OPENAI_API_KEY

# --- Dropboxファイル操作 ---
def list_files(folder_path="/Apps/slot-data-analyzer"):
    result = dbx.files_list_folder(folder_path)
    return result.entries

def download_file(path):
    _, res = dbx.files_download(path)
    return res.content

def file_hash(content):
    return hashlib.sha256(content).hexdigest()

# --- GPT要約処理 ---
def summarize_text(text):
    try:
        response =