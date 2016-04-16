from hello_settings import SECRETS_DICT

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


def send_text(msg, to_phone_number):

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('myfreehoroscopetoday@gmail.com', SECRETS_DICT['TEXT_SECRET'])

    msg = msg.encode('ascii', 'ignore')
    message = MIMEText(msg)
    message['Date'] = formatdate()
    message['From'] = 'myfreehoroscopetoday@gmail.com'

    server.sendmail('myfreehoroscopetoday@gmail.com', to_phone_number, message.as_string())
    server.quit()


if __name__ == '__main__':
    # send_text('hello cman: colons bork it :) http://reddit.com', to_phone_number=SECRETS_DICT['MY_PHONE_NUMBER'])
    send_text('hello', to_phone_number=SECRETS_DICT['MY_PHONE_NUMBER'])
    # send_text('hello', to_phone_number='maxhfowler@gmail.com')
