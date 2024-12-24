from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    """サービスアカウントを使用して認証を行い、YouTube API クライアントを返す"""
    with open('service_account.json', 'r') as f:
        service_account_info = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return build("youtube", "v3", credentials=credentials)

def get_unreplied_comment(youtube, video_id, username):
    """返信がない最も新しいコメントを取得"""
    next_page_token = None
    latest_unreplied_comment = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,  # 最大100件を取得
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comment_text = top_comment["textDisplay"]
            comment_id = item["id"]
            comment_author = top_comment["authorDisplayName"]

            # 条件: `@MEPI486` を含み、返信が存在しない
            if username in comment_text:
                if "replies" not in item or len(item["replies"]["comments"]) == 0:
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
            break

    return latest_unreplied_comment

def post_reply(youtube, comment_id, reply_text):
    """指定されたコメントIDに対して返信を投稿"""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": reply_text
                }
            }
        )
        response = request.execute()
        print(f"返信しました: {reply_text} (対象コメントID: {comment_id})")
    except Exception as e:
        print(f"コメントへの返信中にエラーが発生しました (コメントID: {comment_id}): {e}")

def main():
    youtube = authenticate()
    video_id = "p7jBg6oSUJk"  # 対象の動画ID
    username = "@MEPI486"  # 条件とする文字列
    reply_text = "効いてて草"  # 返信内容

    # 返信がない最も新しいコメントを取得
    comment = get_unreplied_comment(youtube, video_id, username)

    if comment:
        print(f"返信対象コメント: {comment['text']} by {comment['author']}")
        post_reply(youtube, comment["comment_id"], reply_text)
    else:
        print("返信がないコメントは見つかりませんでした。")

if __name__ == "__main__":
    main()
