from googleapiclient.discovery import build
import os

# 環境変数からAPIキーを取得
API_KEY = os.getenv('API_KEY')

def get_replies_to_my_comment(youtube, video_id, my_comment_text):
    """特定の動画内で、自分のコメントへの返信を取得"""
    try:
        # コメントスレッドを取得
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100  # 最大100件まで取得
        )
        response = request.execute()
        
        # 自分のコメントを探し、返信を取得
        for item in response['items']:
            top_comment = item['snippet']['topLevelComment']['snippet']
            if top_comment['textDisplay'] == my_comment_text:  # 自分のコメントを特定
                if 'replies' in item:  # 返信がある場合
                    for reply in item['replies']['comments']:
                        print(f"Reply from {reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # YouTube Data APIクライアントを初期化
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # 手動で指定する動画IDと自分のコメント内容
    video_id = "p7jBg6oSUJk"  # 対象の動画IDを指定
    my_comment_text = "効いてて草"  # 自分のコメント内容を正確に指定

    # 返信を取得
    get_replies_to_my_comment(youtube, video_id, my_comment_text)

if __name__ == "__main__":
    main()
