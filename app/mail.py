from app       import app
from flask     import render_template, url_for
from app.token import generate_confirmation_token
from app.decorators import async

import requests

APP_FROM    = app.config['APP_FROM']
APP_ADMIN   = app.config['APP_ADMIN']
MAILGUN_API = app.config['MAILGUN_API']


@async
def send_async_email(app, subject, recipients, text_body, html_body):
    with app.app_context():
        uri     = 'https://api.mailgun.net/v3/{0}/messages'.format(MAILGUN_DOMAIN)
        payload = {
            'from':    APP_FROM,
            'to':      recipients,
            'subject': subject,
            'text':    text_body,
            'html':    html_body,
        }

        response = requests.post(
                       uri,
                       verify=False,
                       auth=('api', MAILGUN_API),
                       data=payload,
                    )

        if response.status_code == requests.codes.ok:
            app.logger.debug('SUCCESS: Message: "{0}", to: "{1}"'.format(subject, recipients))
            app.logger.debug(response.json())
        else:
            app.logger.debug('ERROR: Message: "{0}", to: "{1}", status: "{2}"'.format(subject, recipients, response.status_code))
            app.logger.debug(response.json())

def send_email(subject, recipients, text_body, html_body):
    send_async_email(app, subject, recipients, text_body, html_body)

def send_confirmation_email(user):
    token       = generate_confirmation_token(user.email)
    confirm_url = url_for('user_confirm', token=token, _external=True)
    app.logger.debug('Confirm url: {0}'.format(confirm_url))

    send_email("Confirmación de cuenta para https://it-dojo.io",
               user.email,
               render_template("confirm_email.txt",  user=user, token_url=confirm_url),
               render_template("confirm_email.html", user=user, token_url=confirm_url))

def send_reset_passwd_email(user):
    token = generate_confirmation_token(user.email)
    reset_password_url = url_for('user_reset', token=token, _external=True)
    app.logger.debug('Reset password url: {0}'.format(reset_password_url))

    send_email("Recuperación de cuenta para https://it-dojo.io",
               user.email,
               render_template("reset_password.txt",  user=user, token_url=reset_password_url),
               render_template("reset_password.html", user=user, token_url=reset_password_url))

def send_test_notification(test):
    token = generate_confirmation_token(str(test.id))
    access_url = url_for('test_confirm', token=token, _external=True)
    app.logger.debug('información enviada a {}'.format(test.email))
    app.logger.debug('hash:  http://localhost:5000/applicant/interview/{}'.format(token))

    send_email("Información de la prueba en https://it-dojo.io",
               test.email,
               render_template("test_notification.txt",test=test, access_url=access_url ),
               render_template("test_notification.html", test=test, access_url=access_url)
    )

def send_test_completion(users):
    app.logger.debug('información enviada a {}'.format(test.email))
    app.logger.debug('completion: {}'.format(users))

    for user in users:
        send_email("Información de la prueba en https://it-dojo.io",
                   test.email,
                   render_template("test_completion.txt",test=test, access_url=access_url ),
                   render_template("test_completion.html", test=test, access_url=access_url)
        )

