import json
import os
import requests

from crawler import summary_info
from crawler import hospital_info

CHATBOT_RESPONSE = {
    '확진환자수': '',
    '퇴원조치수': '',
    '발단': """2019년 12월, 중국 우한에서 처음 발생했습니다. 감염원은 동물로 추정되고 있으며, 동물에게서 사람으로 전파된 것으로 추정됩니다.""",
    '증상': """감염되면 최대 2주간의 잠복기를 거친 후, 발열/기침/호흡곤란을 비롯한 폐렴 증상이 주로 나타납니다. 다만, 증상이 나타나지 않는 무증상 감염 사례도 존재합니다.""",
    '전염경로': """코로나19는 사람 간 전파가 확인된 바이러스입니다. 주된 감염경로는 비말감염으로, 감염자의 침방울이 호흡기나 눈/코/입의 점막으로 침투될 때 전염됩니다.""",
    '예방법': """1. 우선, 비누와 물로 손을 자주 씻습니다. 손 소독제 사용도 좋은 대안입니다.
    \n2. 씻지 않은 손으로 눈이나 코, 입을 만지지 않습니다.
    \n3. 기침이나 재채기를 할 때 티슈나 소매로 입/코를 가립니다.
    \n4. 아플 때는 자가격리를 통해 다른 사람과의 접촉을 피합니다.""",
    '치료': """코로나19 치료는 환자의 증상에 대응하는 치료로 이루어집니다.\n기침/인후통/폐렴 등 주요 증상에 따라 항바이러스제나 항생제 투여가 해당됩니다.""",
}


def lambda_handler(event, context):
    # TODO implement

    if event["httpMethod"] == "GET":
        hub_challenge = event["queryStringParameters"]["hub.challenge"]
        hub_verify_token = event["queryStringParameters"]["hub.verify_token"]

        # store VERIFY_TOKEN in aws_lambda
        if hub_verify_token == os.environ['VERIFY_TOKEN']:
            return {'statusCode': '200', 'body': hub_challenge, 'headers': {'Content-Type': 'application/json'}}
        else:
            return {'statusCode': '401', 'body': 'Incorrect verify token', 'headers': {'Content-Type': 'application/json'}}

    elif event["httpMethod"] == "POST":
        try:
            incoming_message = json.loads(event['body'])
            message = incoming_message['entry'][0]['messaging'][0]
            if(message['sender']['id'] and message['message']['text']):
                send_dots(message['sender']['id'])
                send_text_message(
                    message['sender']['id'], message['message']['text'])
            return {'statusCode': '200', 'body': 'Success', 'headers': {'Content-Type': 'application/json'}}
        except:
            return {'statusCode': '500', 'body': 'Internal server error', 'headers': {'Content-Type': 'application/json'}}

def send_text_message(fbid, received_message):
    reply = ''
    quick_replies = list()

    # add crawler data in dict
    if '확진환자수' in received_message:
        data = json.loads(summary_info.get_json())
        CHATBOT_RESPONSE['확진환자수'] = "현재시각 기준, 코로나19 확진환자는 %s명, 검사가 진행중인 유증상자는 %s명입니다." % (
            data["confirmator_num"], data["check_num"])
    if '퇴원조치수' in received_message:
        data = json.loads(summary_info.get_json())
        CHATBOT_RESPONSE['퇴원조치수'] = "현재시각 기준, %s명이 코로나19 확진 후 퇴원조치(격리해제) 되었습니다." % data["discharged_num"]

    for key in CHATBOT_RESPONSE.keys():
        quick_replies.append(
            {"content_type": "text", "title": key, "payload": "DEVELOPER_DEFINED_PAYLOAD"})
        if key in received_message:
            reply += CHATBOT_RESPONSE[key] + '\n\n'

    if not reply:
        reply = "안녕하세요,\n코로나 알리미입니다!\n\n아래 제시된 키워드를 포함하여 질문해주세요."

    send_message_api(json.dumps({
        "recipient": {"id": fbid}, "message": {"text": reply, "quick_replies": quick_replies}}))

def send_media_message(fbid, media_url, media_type):
    send_message_api(json.dumps({
        "recipient": {"id": fbid},
        "message": {"attachment": {"type": media_type, "payload": {"url": media_url}}}
    }))

def send_dots(fbid):
    send_message_api(json.dumps({
        "recipient": {"id": fbid},
        "sender_action": "typing_on"
    }))

def send_message_api(response_msg):
    endpoint = 'https://graph.facebook.com/v6.0/me/messages?access_token=%s' % os.environ['PAGE_ACCESS_TOKEN']
    requests.post(endpoint, headers={
                  "Content-Type": "application/json"}, data=response_msg)