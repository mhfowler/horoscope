from hello_settings import SECRETS_DICT

import json
import urllib2
import time
import random
import numpy

from hello_utilities.text_helper import send_text
from hello_utilities.log_helper import _log
from hello_models.models import KeyVal


class FbEventChecker:

    def __init__(self, db_session, fb_event_id, to_phone_number):
        self.db_session = db_session
        self.fb_event_id = fb_event_id
        self.to_phone_number = to_phone_number
        # keys for retrieving and storing values
        self.latest_alert_id_key = 'alertid_' + str(fb_event_id) + str(to_phone_number)
        self.latest_alert_date_key = 'alertdate_' + str(fb_event_id) + str(to_phone_number)
        self.sent_alert_key = 'sentalert_' + str(fb_event_id) + str(to_phone_number)

    def get_keyval_or_none(self, key):
        try:
            keyval = self.db_session.query(KeyVal).filter(KeyVal.key == key).one()
            return keyval
        except:
            return None

    def get_value_helper(self, key):
        keyval = self.get_keyval_or_none(key=key)
        if keyval:
            return keyval.value
        else:
            return None

    def save_value_helper(self, key, val):
        keyval = self.get_keyval_or_none(key=key)
        if not keyval:
            keyval = KeyVal(key=key, value=val)
        keyval.value = val
        self.db_session.add(keyval)
        self.db_session.commit()

    def get_latest_alert_id(self):
        return self.get_value_helper(key=self.latest_alert_id_key)

    def get_latest_alert_date(self):
        return self.get_value_helper(key=self.latest_alert_date_key)

    def save_latest_alert_date(self, date_string):
        self.save_value_helper(key=self.latest_alert_date_key, val=date_string)

    def save_latest_alert_id(self, fb_id):
        self.save_value_helper(key=self.latest_alert_id_key, val=fb_id)

    def check_for_ps1(self):
        access_token = SECRETS_DICT['FB_FRIENDSFRIENDS_ACCESS_TOKEN']
        url = "https://graph.facebook.com/{}/feed?access_token={}".format(self.fb_event_id, access_token)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()
        returned = json.loads(the_page)
        messages = returned['data']

        # also check for mo recent date
        previous_latest_date_string = self.get_latest_alert_date()
        if not previous_latest_date_string:
            first_date_string = messages[0]['created_time']
            self.save_latest_alert_date(date_string=first_date_string)

        previous_latest_date = numpy.datetime64(previous_latest_date_string)
        latest_found = previous_latest_date
        for message in messages:
            updated_time_string = message.get('created_time')
            if updated_time_string:
                message_date = numpy.datetime64(updated_time_string)
                if previous_latest_date == numpy.datetime64('NaT') or message_date > previous_latest_date:
                    if latest_found == numpy.datetime64('NaT') or message_date > latest_found:
                        latest_found = message_date
                        self.save_latest_alert_date(date_string=updated_time_string)
                    message_text = message.get('message') if message.get('message') else ''
                    message_id = message['id']
                    link_to_comment = 'http://facebook.com/{}/'.format(message_id)
                    message_text += '--> {}'.format(link_to_comment)

                    already_sent = self.db_session.query(KeyVal).filter(KeyVal.key == self.sent_alert_key, KeyVal.value == message_id)
                    if not already_sent.count():
                        already_sent = KeyVal(key=self.sent_alert_key, value=message_id)
                        self.db_session.add(already_sent)
                        self.db_session.commit()
                        _log('++ sending text to {phone_number}: {msg}'.format(
                            phone_number=self.to_phone_number,
                            msg=message_text.encode('ascii', 'ignore')
                        ))
                        send_text(msg=message_text, to_phone_number=self.to_phone_number)


if __name__ == '__main__':

    fb_e_id = '1195942747097385'
    to_phone_number = SECRETS_DICT['MY_PHONE_NUMBER']
    from hello_models.database import db_session
    expo_sleep = 0
    event_checker = FbEventChecker(db_session=db_session, fb_event_id=fb_e_id, to_phone_number=to_phone_number)
    while True:
        try:
            event_checker.check_for_ps1()
            expo_sleep = 0
            time.sleep(20 + random.randint(0,5))
        except Exception as e:
            raise e
            # print 'XX exception'
            # send_text('XX ' + str(expo_sleep), to_phone_number=to_phone_number)
            # expo_sleep += 1
            # time.sleep(2**expo_sleep * 60)