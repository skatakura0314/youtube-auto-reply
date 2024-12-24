import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Google API 認証
def authenticate():
    try:
        logging.info("認証プロセスを開始します...")
        # GitHub Secrets 経由で認証情報を取得
        service_account_info = os.environ.get("SERVICE_ACCOUNT_JSON")
        if not service_account_info:
            logging.error("サービスアカウントの認証情報が見つかりません。")
            return None

        # 認証情報を用いて YouTube API クライアントを作成
        credentials = Credentials.from_service_account_info(
            eval(service_account_info),
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
        )
        youtube = build("youtube", "v3", credentials=credentials)
        logging.info("認証に成功しました。")
        return youtube
    except Exception as e:
        logging.error(f"認証中にエラーが発生しました: {e}")
        return None

# 未返信コメントを取得
def get_unreplied_comment(youtube, video_id, username):
    """返信がない最も新しいコメントを取得"""
    next_page_token = None
    latest_unreplied_comment = None

    logging.info("コメント取得を開始します...")

    while True:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        logging.info("コメント取得中...")

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comment_text = top_comment["textDisplay"]
            comment_id = item["id"]
            comment_author = top_comment["authorDisplayName"]

            logging.info(f"取得したコメント: {comment_text} by {comment_author}")

            # 条件: `@MEPI486` を含み、返信が存在しない
            if username in comment_text:
                logging.info(f"条件に一致: {comment_text} by {comment_author}")
                if "replies" not in item or len(item["replies"]["comments"]) == 0:
                    logging.info(f"返信がないコメント候補: {comment_text} by {comment_author}")
                    # 最初の候補、またはより新しいコメントがある場合
                    if (latest_unreplied_comment is None or
                        top_comment["publishedAt"] > latest_unreplied_comment["publishedAt"]):
                        latest_unreplied_comment = {
                            "comment_id": comment_id,
                            "text": comment_text,
                            "author": comment_author,
                            "publishedAt": top_comment["publishedAt"]
                        }

        # 次のページトークンがある場合、次のリクエストを実行
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            logging.info("すべてのコメントを取得しました。")
            break

    if latest_unreplied_comment:
        logging.info(f"最も新しい返信がないコメント: {latest_unreplied_comment['text']} by {latest_unreplied_comment['author']}")
    else:
        logging.info("返信がないコメントは見つかりませんでした。")

    return latest_unreplied_comment

# コメントに返信
def post_reply(youtube, comment_id, reply_text):
    """コメントに返信を投稿"""
    try:
        logging.info(f"コメントID {comment_id} に返信中...")
        youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": reply_text
                }
            }
        ).execute()
        logging.info("返信を投稿しました。")
    except HttpError as e:
        logging.error(f"コメントへの返信中にエラーが発生しました (コメントID: {comment_id}): {e}")
    except Exception as e:
        logging.error(f"予期しないエラーが発生しました (コメントID: {comment_id}): {e}")

# メイン関数
def main():
    logging.info("スクリプトを開始しました。")
    
    # 認証
    youtube = authenticate()
    if not youtube:
        logging.error("YouTube API の認証に失敗しました。")
        return

    logging.info("YouTube API に認証しました。")

    # コメントを取得して返信
    video_id = "p7jBg6oSUJk"
    username = "@MEPI486"
    reply_text = "効いてて草"

    logging.info(f"動画ID: {video_id}, ターゲットユーザー: {username}")

    try:
        unreplied_comment = get_unreplied_comment(youtube, video_id, username)
        if unreplied_comment:
            logging.info(f"返信対象コメント: {unreplied_comment['text']} by {unreplied_comment['author']}")
            post_reply(youtube, unreplied_comment["comment_id"], reply_text)
            logging.info(f"返信しました: {reply_text}")
        else:
            logging.info("返信がないコメントは見つかりませんでした。")
    except Exception as e:
        logging.error(f"スクリプトの実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
