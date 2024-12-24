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

            print(f"取得したコメント: {comment_text} by {comment_author}")

            # 条件: `@MEPI486` を含み、返信が存在しない
            if username in comment_text:
                if "replies" not in item or len(item["replies"]["comments"]) == 0:
                    print(f"返信がないコメント候補: {comment_text} by {comment_author}")
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
