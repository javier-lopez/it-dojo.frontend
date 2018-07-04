import logging, requests

from config import Config

class MailgunLogger(logging.Handler):
    def __init__(self):
        #run the regular Handler __init__
        logging.Handler.__init__(self)
        self.uri        = 'https://api.mailgun.net/v3/{0}/messages'.format(Config.MAILGUN_DOMAIN)
        self.api        = Config.MAILGUN_API
        self.subject    = "it-dojo.io critical error"
        self.sender     = Config.APP_FROM
        self.recipient  = Config.APP_ADMIN

    def emit(self, record): #record.message is the log message
        payload = {
            "from":    self.sender,
            "to":      self.recipient,
            "subject": self.subject,
            "text":    self.format(record)
        }

        response = requests.post(
                       self.uri,
                       verify=False,
                       auth=("api", self.api),
                       data=payload,
                   )

        if response.status_code != requests.codes.ok:
            raise ValueError("Error while mailing above exception, mailgun api response: {}, {}"
                             .format(response.status_code, response.text))
