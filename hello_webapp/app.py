import os
import sys
import traceback
import re, json

from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request

from hello_settings import PROJECT_PATH, get_db_url, DEBUG
from hello_utilities.log_helper import _log
from hello_webapp.helper_routes import get_hello_helpers_blueprint
from hello_models.database import db_session
from hello_models.models import FbAlert
from hello_utilities.fb_event_checker import FbEventChecker


# paths
FLASK_DIR = os.path.join(PROJECT_PATH, 'hello_webapp')
TEMPLATE_DIR = os.path.join(FLASK_DIR, 'templates')
STATIC_DIR = os.path.join(FLASK_DIR, 'static')


# create flask app
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=PROJECT_PATH)
app.debug = DEBUG


# integrate sql alchemy
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
db = SQLAlchemy(app)


# register blueprints
hello_helpers = get_hello_helpers_blueprint(db=db, template_dir=TEMPLATE_DIR)
app.register_blueprint(hello_helpers)


@app.route("/get_all_tix/")
def get_all_tix_endpoint():
    active_alerts = db_session.query(FbAlert).all()
    to_return = 'getting all tix: '
    for alert in active_alerts:
        event_id = alert.fb_id
        to_phone_number = alert.phone_number
        event_checker = FbEventChecker(db_session=db_session, fb_event_id=event_id, to_phone_number=to_phone_number)
        event_checker.check_for_ps1()
        _log('..checking for new posts for: https://www.facebook.com/events/{fb_id}/ - {phone_number}'.format(
            fb_id=event_id,
            phone_number=to_phone_number
        ))
        to_return += '| fb_id: {}, phone: {} '.format(event_id, to_phone_number)
    return to_return


@app.route("/remove_alert/", methods=['POST'])
def remove_alert_endpoint():
    phone = request.form['phone']
    fb_id = request.form['fblink']
    alerts = db_session.query(FbAlert).filter(FbAlert.fb_id == fb_id, FbAlert.phone_number == phone)
    alerts.delete()
    db_session.commit()
    _log('++ removing alert for: {fb_id} - {phone_number}'.format(
        fb_id=fb_id,
        phone_number=phone
    ))
    return 'removed'


@app.route("/add_alert/", methods=['POST'])
def add_alert_endpoint():
    phone = request.form['phone']
    fb_link = request.form['fblink']
    phone = phone.strip()
    fb_link = fb_link.strip()
    matched = re.match('.*www\.facebook\.com/events/(\d+)/', fb_link)
    if not matched:
        return jsonify({
            'message': 'Invalid format of fb events link'
        })
    fb_id = matched.group(1)
    fb_alert = FbAlert(phone_number=phone, fb_id=fb_id)
    db_session.add(fb_alert)
    db_session.commit()
    _log('++ someone added a new horoscope alert! {fb_link} - {phone_number} \n http://www.myfreehoroscope.today/'.format(
        fb_link=fb_link,
        phone_number=phone
    ))
    return jsonify({
        'message': 'added new alert'
    })


@app.route("/")
def myfreehoroscope():
    active_alerts = db_session.query(FbAlert).all()
    return render_template('horoscope.html', active_alerts=active_alerts)


@app.route('/static/<path:path>')
def send_static(path):
    """
    for local static serving
    this route will never be reached on the server because nginx will bypass flask all together
    """
    return send_from_directory(STATIC_DIR, path)


@app.errorhandler(500)
def error_handler_500(e):
    """
    if a page throws an error, log the error to slack, and then re-raise the error
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    formatted_lines = traceback.format_exc()
    _log('@channel: 500 error: {}'.format(e.message))
    _log(formatted_lines)
    raise e


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run()
