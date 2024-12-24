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

def get_comments(youtube, video_id):
    """指定された動画のすべてのコメントを取得"""
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # 1回のリクエストで最大100件
            pageToken=next_page_token  # 次のページのトークンを指定
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id": item["id"],  # コメントのID
                "text": comment["textDisplay"],  # コメント本文
                "author": comment["authorDisplayName"]  # コメント投稿者名
            })

        # 次のページトークンがある場合、次のリクエストを実行
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments

def post_reply(youtube, comment_id, reply_text):
    """指定されたコメントIDに対して返信を投稿"""
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
    print(f"Replied to comment {comment_id}: {reply_text}")

def main():
    youtube = authenticate()
    video_id = "p7jBg6oSUJk"  # 対象の動画ID
    username = "@MEPI486"  # 検出する文字列
    reply_text = "効いてて草"  # 返信内容

    # コメントを取得
    comments = get_comments(youtube, video_id)
    print(f"Retrieved {len(comments)} comments.")

    # 条件に合うコメントに返信
    for comment in comments:
        if username in comment["text"]:  # username がコメントに含まれる場合のみ
            print(f"Replying to: {comment['text']} by {comment['author']}")
            post_reply(youtube, comment["comment_id"], reply_text)

if __name__ == "__main__":
    main()
