import requests
import smtplib
import ssl
import imaplib
import time
import email
from email.message import EmailMessage
from email.parser import BytesParser

# Function to send an email

def send_email(sender, recipient, subject, body):
    
    # Lets breakdown the email structure
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)
    
# Connect the SMTP server to enable the email to be sent
    with smtplib.SMTP ('smtp.gmail.com' , 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login ('Your_Email' , 'your_smtp_password')
        smtp.send_message(msg)
        
        
# Lets define a function that is going to fetch all unread emails

def fetch_emails():
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_server.login('Your_Email' , 'your_smtp_password')
    imap_server.select('INBOX')
    
    #Search for all unread emails
    status, email_ids = imap_server.search(None, 'UNSEEN')
    email_ids = email_ids[0].split()
    
    emails = []
    
    #Fetch email for each ID
    for email_id in email_ids:
        status, email_data = imap_server.fetch(email_id, '(RFC822)')
        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        email_obj = {
            'email':msg            
        }
        emails.append(email_obj)
        
    imap_server.logout()
    return emails

#Lets create a funtcion that will process these emails

def process_emails():
    emails = fetch_emails()
    
    for email_obj in emails:
        email = email_obj['email']
        reply_to_email(email.as_bytes())
        
# Now lets create the reply function

def reply_to_email(email):
    msg  = BytesParser().parsebytes(email) # this are the parameters required to generate response
    sender =msg['From']
    subject = msg ['Subject']
    body= extract_body(msg)
    reply = compose_reply(subject,sender, body)
    send_email(sender = 'Your_Email',
              recipient = sender,
              subject=f"Re: {subject}",
              body=reply)
    
#Define a funtion to compose a reply
def extract_body(email_message):
    if email_message.is_multipart():
        # Iterate over email parts until the text/plain part is found
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8')
    else:
        # For simple email messages, return the payload directly
        return email_message.get_payload(decode=True).decode('utf-8')
    
    
            
def compose_reply(subject, sender, body):
    response = requests.post(
            'https://api.openai.com/v1/chat/completions',
        headers= {
            'Content-Type' : 'application/json',
            'Authorization' : 'Bearer Your_API_Key',
        },
        json = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'system', 'content' :' Your are Helpful'},
                        {'role': 'user', 'content' : body}],
        }
    )
    reply = response.json()['choices'][0]['message']['content']
    
    return reply

while True:
    process_emails()
    time.sleep(1)
           