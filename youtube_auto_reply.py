import os
import logging
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 動画ID、特定のユーザー名、返信内容
video_id = "p7jBg6oSUJk"
username = "@MEPI486"
reply_text = "効いてて草"

# 環境変数や設定を利用
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_JSON")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

if not SERVICE_ACCOUNT_FILE:
    logging.error("サービスアカウントJSONが見つかりません。")
    exit(1)

try:
    # 環境変数がJSON文字列の場合
    service_account_info = json.loads(SERVICE_ACCOUNT_FILE)
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    youtube = build("youtube", "v3", credentials=credentials)
    logging.info("YouTube API認証に成功しました。")
except Exception as e:
    logging.error("YouTube API認証に失敗しました: %s", e)
    exit(1)

def get_comments(video_id):
    """動画のコメントを取得"""
    try:
        comments = []
        next_page_token = None
        while True:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                order="time",
                pageToken=next_page_token
            )
            response = request.execute()
            comments.extend(response.get("items", []))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return comments
    except Exception as e:
        logging.error("コメント取得に失敗しました: %s", e)
        return []

def reply_to_comment(comment_id, text):
    """コメントに返信"""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": text
                }
            }
        )
        request.execute()
        logging.info("コメントに返信しました: %s", comment_id)
    except Exception as e:
        logging.error("コメントの返信に失敗しました: %s", e)

def main():
    logging.info("動画ID: %s に対してコメントを処理します。", video_id)
    comments = get_comments(video_id)
    if not comments:
        logging.info("返信するコメントがありません。")
        return

    for comment in comments:
        comment_id = comment["snippet"]["topLevelComment"]["id"]
        text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        
        # 特定のユーザー名が含まれるコメントに返信
        if username in text:
            logging.info("対象コメントを発見しました: %s", text)
            reply_to_comment(comment_id, reply_text)

if __name__ == "__main__":
    logging.info("スクリプトを開始しました。")
    main()
