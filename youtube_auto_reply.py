from googleapiclient.discovery import build
import os

# 環境変数からAPIキーを取得
API_KEY = os.getenv('API_KEY')  # GitHub Secretsや環境変数に設定されているAPIキーを使用
if not API_KEY:
    raise ValueError("API_KEY is not set. Please set it as an environment variable.")

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

def get_replies_with_mention_and_post(youtube, video_id, username, reply_text):
    """特定のユーザー名を含むリプライを検出し、自動で返信を投稿"""
    try:
        print(f"Fetching comments for video_id: {video_id}")
        # コメントスレッドを取得
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        
        print("Response received from API:")
        print(response)  # デバッグ用：レスポンスを確認
        
        for item in response.get('items', []):
            if 'replies' in item:  # 返信がある場合
                for reply in item['replies']['comments']:
                    reply_text_display = reply['snippet']['textDisplay']
                    comment_id = reply['id']
                    if username in reply_text_display:  # リプライに特定のユーザー名が含まれるか
                        print(f"Reply mentioning {username} found: {reply_text_display}")
                        # 自動で返信を投稿
                        post_reply(youtube, comment_id, reply_text)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # YouTube Data APIクライアントを初期化
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 動画ID、検索するユーザー名、返信内容を指定
    video_id = "p7jBg6oSUJk"  # 動画IDを指定
    username = "@MEPI486"       # 検索対象のユーザー名
    reply_text = "効いてて草"  # 自動返信する内容
    
    # 指定したユーザー名を含むリプライを検出し、返信を投稿
    get_replies_with_mention_and_post(youtube, video_id, username, reply_text)

if __name__ == "__main__":
    main()
