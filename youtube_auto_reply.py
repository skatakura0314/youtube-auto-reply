from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# スコープ設定（YouTubeの操作に必要）
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    """OAuth 2.0認証を行い、認証済みサービスを返す"""
    creds = None
    # トークンファイルが存在する場合、再利用
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # トークンが存在しない場合、新たに認証を実行
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES  # ここでOAuthクライアント情報を指定
            )
            creds = flow.run_local_server(port=0)
        # トークンを保存
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def post_reply(youtube, comment_id, reply_text):
    """指定されたコメントIDに対して返信を投稿"""
    try:
        request = youtube.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,  # 返信先のコメントID
                    "textOriginal": reply_text  # 投稿する返信内容
                }
            }
        )
        response = request.execute()
        print(f"Replied to comment: {response['snippet']['textDisplay']}")
    except Exception as e:
        print(f"An error occurred while posting the reply: {e}")

def main():
    youtube = authenticate()
    
    # 動画IDとリプライ内容
    video_id = "p7jBg6oSUJk"
    username = "@MEPI486"
    reply_text = "効いてて草"

    # コメントスレッドを取得してリプライを検索
    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    for item in response.get("items", []):
        if "replies" in item:
            for reply in item["replies"]["comments"]:
                reply_text_display = reply["snippet"]["textDisplay"]
                comment_id = reply["id"]
                if username in reply_text_display:
                    print(f"Reply mentioning {username} found: {reply_text_display}")
                    post_reply(youtube, comment_id, reply_text)

if __name__ == "__main__":
    main()
