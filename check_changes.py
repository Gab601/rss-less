#!/usr/bin/env python3
"""
Webpage Change Tracker
Monitors a list of webpages for changes and sends email notifications.
"""

import os
import sys
import hashlib
import smtplib
import requests
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_urls():
    """Load URLs from environment variable (comma-separated list)."""
    urls_string = os.environ.get('TRACKED_URLS', '')

    if not urls_string:
        print("Error: TRACKED_URLS environment variable not set")
        return []

    # Split by comma and clean up whitespace
    urls = [url.strip() for url in urls_string.split(',') if url.strip()]

    return urls


def get_content_hash(content):
    """Generate a hash of the webpage content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def fetch_webpage(url):
    """Fetch webpage content with error handling."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_snapshot_hash(url, content_hash, snapshots_dir='snapshots'):
    """Save only the hash of webpage content to disk."""
    Path(snapshots_dir).mkdir(exist_ok=True)

    # Create a safe filename from the URL
    filename = hashlib.md5(url.encode()).hexdigest() + '.hash'
    filepath = Path(snapshots_dir) / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_hash)

    return filepath


def load_previous_snapshot_hash(url, snapshots_dir='snapshots'):
    """Load previous snapshot hash if it exists."""
    filename = hashlib.md5(url.encode()).hexdigest() + '.hash'
    filepath = Path(snapshots_dir) / filename

    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None


def send_email(subject, body, recipient_email, sender_email, sender_password, smtp_server, smtp_port):
    """Send email notification about changes."""
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def check_changes():
    """Main function to check all URLs for changes."""
    urls = load_urls()

    if not urls:
        print("No URLs to check")
        return

    # Get email configuration from environment variables
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL', sender_email)
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))

    if not sender_email or not sender_password:
        print("Error: Email credentials not configured")
        print("Set SENDER_EMAIL and SENDER_PASSWORD environment variables")
        sys.exit(1)

    changes_detected = []

    print(f"Checking {len(urls)} URLs for changes...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for url in urls:
        print(f"\nChecking: {url}")

        # Fetch current content
        current_content = fetch_webpage(url)
        if current_content is None:
            continue

        # Calculate current content hash
        current_hash = get_content_hash(current_content)

        # Load previous snapshot hash
        previous_hash = load_previous_snapshot_hash(url)

        if previous_hash is None:
            # First time checking this URL
            print(f"  -> First time tracking this URL, saving initial hash")
            save_snapshot_hash(url, current_hash)
        else:
            # Compare with previous version
            if current_hash != previous_hash:
                print(f"  -> CHANGE DETECTED!")
                changes_detected.append(url)
                save_snapshot_hash(url, current_hash)
            else:
                print(f"  -> No changes")

    # Send notification email if changes detected
    if changes_detected:
        subject = f"Webpage Changes Detected - {len(changes_detected)} page(s) updated"
        body = f"""Hello,

The following webpage(s) have been updated since the last check:

"""
        for url in changes_detected:
            body += f"  - {url}\n"

        body += f"""

Check timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
This is an automated message from your webpage change tracker.
"""

        send_email(subject, body, recipient_email, sender_email, sender_password, smtp_server, smtp_port)
    else:
        print("\nNo changes detected on any tracked pages")


if __name__ == '__main__':
    check_changes()
