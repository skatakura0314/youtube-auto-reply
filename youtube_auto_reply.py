from googleapiclient.discovery import build
import os

# 環境変数からAPIキーを取得
API_KEY = os.getenv('API_KEY')  # GitHub Secretsや環境変数に設定されているAPIキーを使用
if not API_KEY:
    raise ValueError("API_KEY is not set. Please set it as an environment variable.")

def get_replies_to_my_comment(youtube, video_id, my_comment_text):
    """自分のコメントへの返信を取得"""
    try:
        print(f"Fetching comments for video_id: {video_id}")
        # コメントスレッドを取得
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        
        # APIレスポンス全体をデバッグログとして出力
        print("Response received from API:")
        print(response)
        
        found = False
        for item in response.get('items', []):
            # 各トップレベルコメントの内容を取得
            top_comment = item['snippet']['topLevelComment']['snippet']
            print(f"Top-level comment: {top_comment['textDisplay']}")
            
            if top_comment['textDisplay'] == my_comment_text:  # 自分のコメントを特定
                print("Your comment was found.")
                found = True
                if 'replies' in item:  # 返信がある場合
                    print("Replies found:")
                    for reply in item['replies']['comments']:
                        print(f"Reply from {reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")
        if not found:
            print("No replies found for your comment.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # YouTube Data APIクライアントを初期化
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 動画IDと自分のコメント内容を指定
    video_id = "p7jBg6oSUJk"  # 自分がコメントを投稿した動画のIDを指定
    my_comment_text = "効いてて草"  # 自分が投稿したコメント内容を正確に記載
    
    # コメントへの返信を取得
    get_replies_to_my_comment(youtube, video_id, my_comment_text)

if __name__ == "__main__":
    main()
