import boto3
from botocore.exceptions import ClientError

# def send_email(sender, recipient, subject, body):
#     # Create a new SES resource
#     # Replace 'YOUR_ACCESS_KEY' and 'YOUR_SECRET_KEY' with your IAM user's credentials
#     ses_client = boto3.client('ses', region_name='us-east-1', aws_access_key_id='AKIAYKD5OHVSBQCNBIPJ',
#                               aws_secret_access_key='Erx1KdwTihLBKUF7Jt0e3DhhHkdkmd5rAm+6k4mB')
#
#     # # Create the email message
#     # message = {
#     #     'Subject': {'Data': subject},
#     #     'Body': {'Html': {'Data': body}},
#     #     # 'Body': {'Text': {'Data': body}},
#     #     'Source': sender,
#     #     'Destination': {'ToAddresses': [recipient]},
#     #
#     # }
#     try:
#         success = True
#         # Send the email
#         response = ses_client.send_email(
#             Source=sender,
#             Destination={'ToAddresses': [recipient]},
#             Message={
#                 'Subject': {'Data': subject},
#                 'Body': {'Html': {'Data': body}}
#             },
#
#         )
#     except ClientError as e:
#         success = False
#         print(f"Email sending failed: {e.response['Error']['Message']}")
#     else:
#         print(f"Email sent! Message ID: {response['MessageId']}")
#
#     return success

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
def send_email(sender, recipient, subject, body):
    SENDGRID_API_KEY = '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'
    message = Mail(
        from_email=sender,
        to_emails=recipient,
        subject=subject,
        html_content=body)
    try:
        success = True
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        success = False
        print(e.message)
    return success

