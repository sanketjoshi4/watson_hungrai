import json, os
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from flask import Flask, render_template, request, jsonify

uploads_dir = './uploads/'

info = {
    'iam_auth': 'Wx-EWLZ954sS2vz0Tb9x2YZldRNX3E-uKqa4wNTrSlIa',
    'api_version': '2020-04-01',
    'service_url': 'https://api.us-south.assistant.watson.cloud.ibm.com/instances/148f5128-447c-4fa3-a050-26e716eeca8b',
    'assistant_id': '726e5374-be8e-4026-bc53-69f40e2c72e1',
    'workspace_id': '87651692-6bd8-420c-922f-47547ffe6e7b'
}

authenticator = IAMAuthenticator(info['iam_auth'])
assistant = AssistantV2(version=info['api_version'], authenticator=authenticator)
assistant.set_service_url(info['service_url'])
assistant_id = info['assistant_id']
info['session_id'] = assistant.create_session(assistant_id=assistant_id).get_result()['session_id']

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    data = json.loads(request.data)
    bot_response = assistant.message(
        assistant_id=info['assistant_id'],
        session_id=info['session_id'],
        workspace_id=info['workspace_id'],
        input={'message_type': 'text', 'text': data['msg']}
    ).get_result()
    try:
        return jsonify(bot_response)
    except:
        return None


if __name__ == "__main__":
    app.run(debug=True)
