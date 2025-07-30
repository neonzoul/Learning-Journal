# tasks.py : Task functions - the actual work that gets done
# Why separate file? Keeps slow work isolated from fast web responses

import time

def send_fake_email(email_address: str):
    """Simulates sending an email (takes 10 seconds)
    
    Why fake? Safe for learning - no real emails sent by accident
    Why 10 seconds? Shows the problem: users can't wait this long
    """
    
    print(f"Starting email to {email_address}...")
    time.sleep(10)  # Pretend email sending takes time
    print(f"Email sent to {email_address}!")
    
    return f"Email sent to {email_address}"
