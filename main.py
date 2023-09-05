import awsgi

from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)
base_url = "https://app.ylytic.com/ylytic/test"

@app.route('/', methods=['GET'])
def home():
    return {"success":True,"message":"Open /search"}

@app.route('/search', methods=['GET'])
def search_comments():
    search_author = request.args.get('search_author')
    at_from_str = request.args.get('at_from')
    at_to_str = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    try:
        response = requests.get(base_url)
        response.raise_for_status()

        data = response.json()
        comments = data.get('comments', [])

        filtered_comments = []

        for comment in comments:
            comment_at_str = comment.get('at')
            comment_at = datetime.strptime(comment_at_str, '%a, %d %b %Y %H:%M:%S %Z')

            if search_author and search_author.lower() not in comment.get('author', '').lower():
                continue
            if at_from_str:
                at_from = datetime.strptime(at_from_str, '%d-%m-%Y')
                if comment_at < at_from:
                    continue
            if at_to_str:
                at_to = datetime.strptime(at_to_str, '%d-%m-%Y')
                if comment_at > at_to:
                    continue
            if like_from is not None and comment.get('like', 0) < int(like_from):
                continue
            if like_to is not None and comment.get('like', float('inf')) > int(like_to):
                continue
            if reply_from is not None and comment.get('reply', 0) < int(reply_from):
                continue
            if reply_to is not None and comment.get('reply', float('inf')) > int(reply_to):
                continue
            if search_text and search_text.lower() not in comment.get('text', '').lower():
                continue

            filtered_comments.append(comment)

        return jsonify(filtered_comments)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to fetch comments from the external API'})

def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == '__main__':
    app.run(debug=True)
