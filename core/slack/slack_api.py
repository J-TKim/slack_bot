import os
import ssl
from dotenv import load_dotenv

from slack_sdk import WebClient

ssl._create_default_https_context = ssl._create_unverified_context


load_dotenv()
SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]


class SlackAPI:
    """
    슬랙 API 핸들러
    """

    def __init__(self, token):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)
        self.token = token
        self.channel_name_set = set()
        self.channel_dict = dict()
        self.user_group_encoder = dict()
        self.user_group_decoder = dict()

    def __call__(self):
        return self.client

    def get_channel_id(self, channel_name):
        """
        슬랙 채널ID 조회
        """
        # conversations_list() 메서드 호출

        if channel_name in self.channel_name_set:
            return self.channel_dict[channel_name]

        result = self.client.conversations_list()
        # 채널 정보 딕셔너리 리스트
        channels = result.data['channels']
        # 채널 명이 channel_name인 채널 딕셔너리 쿼리
        channel = list(filter(lambda c: c["name"] == channel_name, channels))[0]
        # 채널ID 파싱
        channel_id = channel["id"]

        self.channel_dict[channel_name] = channel_id
        self.channel_name_set.add(channel_name)

        return channel_id

    def get_message_ts(self, channel_id, query):
        """
        슬랙 채널 내 메세지 조회
        """
        # conversations_history() 메서드 호출
        result = self.client.conversations_history(channel=channel_id)
        # 채널 내 메세지 정보 딕셔너리 리스트
        messages = result.data['messages']
        # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
        message = list(filter(lambda m: m["text"] == query, messages))[0]
        # 해당 메세지ts 파싱
        message_ts = message["ts"]
        return message_ts

    def post_thread_message(self, channel_id, message_ts, text):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=message_ts
        )
        return result

    def post_message(self, channel_id, text):
        """
        슬랙 채널에 글 남기기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text=text,
        )
        return result

    def post_file(self, channel_id, text, file_path, file_explain):
        """
        슬랙 채널에 파일 전송
        """
        result = self.client.files_upload(
            channels=channel_id,
            file=file_path,
            title=file_explain,
            initial_comment=text
        )
        return result

    def post_thread_file(self, channel_id, message_ts, text, file_path, file_explain):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기 파일 전송
        """
        result = self.client.files_upload(
            channels=channel_id,
            file=file_path,
            title=file_explain,
            initial_comment=text,
            thread_ts=message_ts,
        )
        return result

    def get_user_groups_list(self):
        result = self.client.usergroups_list()

        user_groups_list = self.client.usergroups_list()["usergroups"]
        user_group_team_id_set = set()

        for user_group in user_groups_list:
            self.user_group_encoder[user_group["name"]] = user_group["team_id"]
            self.user_group_decoder[user_group["team_id"]] = user_group["name"]

            user_group_team_id_set.add(user_group["team_id"])

        return user_group_team_id_set


slackAPI = SlackAPI(SLACK_API_TOKEN)

if __name__ == "__main__":
    channel_id = os.environ['SLACK_TEST_CHANNEL_ID'] # 테스트 채널

    slackAPI.post_message(channel_id, f"Hello World! <@{os.environ['OPEN_AI_TOKEN']}>")