from twilio.rest import Client


class SMSClient:
    def __init__(self, sid: str, token: str, from_number: str, to_number: str):
        self._sid = sid
        self._token = token
        self.from_number = from_number
        self.to_number = to_number

        self._client = Client(self._sid, self._token)

    def send_session_report_sms(self, follows_count: int):
        """
        Send a SMS message containing information about the finished Pygram session.
        """

        body = f"""Your Pygram session has finished!

        Session Report:

        Total Follows: {follows_count}"""

        self._client.messages.create(
            to=self.to_number, from_=self.from_number, body=body
        )
