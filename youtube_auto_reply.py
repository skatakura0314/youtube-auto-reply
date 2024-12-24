import os
import logging
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 動画IDと条件
VIDEO_ID = "p7jBg6oSUJk"
USERNAME = "@MEPI486"
REPLY_TEXT = "効いてて草"

# 環境変数からサービスアカウントJSONをロード
SERVICE_ACCOUNT_FILE = "service_account.json"

def authenticate_youtube_api():
    """
    Googleサービスアカウントを使用してYouTube APIに認証します。
    """
    try:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
        )
        youtube = build("youtube", "v3", credentials=credentials)
        logging.info("YouTube API 認証に成功しました。")
        return youtube
    except Exception as e:
        logging.error("YouTube API 認証に失敗しました: %s", str(e))
        raise

def get_all_comments(youtube, video_id):
    """
    指定した動画の全コメントを取得します。
    """
    comments = []
    try:
        next_page_token = None
        while True:
            comments_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            )
            comments_response = comments_request.execute()
            comments.extend(comments_response.get("items", []))
            next_page_token = comments_response.get("nextPageToken")
            if not next_page_token:
                break
        logging.info("全コメントを取得しました。合計: %d 件", len(comments))
    except Exception as e:
        logging.error("コメントの取得に失敗しました: %s", str(e))
    return comments

def filter_comments(comments, username):
    """
    特定のユーザー名を含むコメントで、返信がない最新のものを取得します。
    """
    target_comment = None
    for comment in comments:
        try:
            snippet = comment["snippet"]["topLevelComment"]["snippet"]
            text = snippet["textOriginal"]
            reply_count = comment["snippet"].get("totalReplyCount", 0)
            if username in text and reply_count == 0:
                # 最新のものを選ぶため、既存のものより更新日時が新しい場合に上書き
                if not target_comment or snippet["updatedAt"] > target_comment["updatedAt"]:
                    target_comment = snippet
        except KeyError as e:
            logging.warning("コメントのデータが不完全です: %s", str(e))
    return target_comment

def reply_to_comment(youtube, comment_id):
    """
    指定されたコメントに返信を投稿します。
    """
    try:
        youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": REPLY_TEXT
                }
            }
        ).execute()
        logging.info(f"コメントID {comment_id} に返信しました。")
    except Exception as e:
        logging.error(f"コメントID {comment_id} に返信できませんでした: %s", str(e))

def main():
    """
    メインの処理。
    """
    youtube = authenticate_youtube_api()
    comments = get_all_comments(youtube, VIDEO_ID)
    if not comments:
        logging.warning("動画にコメントが見つかりませんでした。")
        return
    target_comment = filter_comments(comments, USERNAME)
    if target_comment:
        logging.info("返信対象のコメントが見つかりました。")
        reply_to_comment(youtube, target_comment["id"])
    else:
        logging.info("返信対象のコメントはありません。")

if __name__ == "__main__":
    main()
