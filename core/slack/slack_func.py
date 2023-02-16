import logging


class SlackParser:
    @staticmethod
    def get_token(request_body: dict) -> str:
        return request_body["token"]

    @staticmethod
    def get_type(request_body: dict) -> str:
        return request_body["type"]

    @staticmethod
    def get_event_id(request_body: dict) -> str:
        return request_body["event_id"]

    @staticmethod
    def get_channel_id(request_body: dict) -> str:
        return request_body["event"]["channel"]

    @staticmethod
    def get_event_ts(request_body: dict) -> str:
        return request_body["event"]["event_ts"]

    @staticmethod
    def get_text(request_body: dict) -> str:
        return request_body["event"]["text"]

    @staticmethod
    def get_event_type(request_body: dict) -> str:
        return request_body["event"]["type"]

    @staticmethod
    def get_event_user_id(request_body: dict) -> str:
        return request_body["event"]["user"]

    @staticmethod
    def get_cmd_and_text(request_body: dict) -> tuple:
        line = request_body["event"]["text"].split(" ")
        logging.info(line)

        if len(line) < 2:
            return None, None
        elif len(line) >= 3:
            cmd, text = line[1], ' '.join(line[2:])
            return cmd, text
        return line[1], None