# import httplib2
# import os
# from oauth2client import file, client, tools
# import base64
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from apiclient import errors, discovery
#
# SCOPES = 'https://www.googleapis.com/auth/gmail.send'
# CLIENT_SECRET_FILE ='/home/vc/Downloads/credentials.json'
# APPLICATION_NAME = 'Gmail API Python Send Email'
#
# def get_credentials():
#     home_dir = os.path.expanduser('~')
#     credential_dir = os.path.join(home_dir, '.credentials')
#     if not os.path.exists(credential_dir):
#         os.makedirs(credential_dir)
#     credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
#     store = file.Storage(credential_path)
#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#         flow.user_agent = APPLICATION_NAME
#         credentials = tools.run_flow(flow, store)
#         print('Storing credentials to ' + credential_path)
#     return credentials
#
#
# def send_message_internal(service, user_id, message):
#     try:
#         message = (service.users().messages().send(userId=user_id, body=message).execute())
#         print('Message Id: %s' % message['id'])
#     except errors.HttpError as error:
#         print('An error occurred: %s' % error)
#
# def create_message(sender, to, subject, plain_msg):
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = subject
#     msg['From'] = sender
#     msg['To'] = to
#     msg.attach(MIMEText(plain_msg, 'plain'))
#     raw = base64.urlsafe_b64encode(msg.as_bytes())
#     raw = raw.decode()
#     body = {'raw': raw}
#     return body
#
# def send_message(sender, to, subject, plain_msg):
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('gmail', 'v1', http=http)
#     message = create_message(sender, to, subject, plain_msg)
#     send_message_internal(service, "me", message)
#
#
# #Testing
# to = 'ramramesh1374@gmail.com'
# sender = "hotimanage@gmail.com"
# subject = "Test"
# message = "Test"
# send_message(sender, to, subject, message)


# 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

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

print(os.environ.get('SENDGRID_API_KEY'))
SENDGRID_API_KEY = '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'
message = Mail(
    from_email='hotimanage@gmail.com',
    to_emails='ramramesh1374@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)