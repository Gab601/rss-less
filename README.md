# rss-less
Stay up to date on websites without RSS feeds

## Overview

This project automatically monitors webpages for changes and sends email notifications when updates are detected. It runs daily via GitHub Actions, making it perfect for tracking websites that don't offer RSS feeds.

## Features

- Daily automated checks at 7:00 AM (configurable)
- Email notifications when changes are detected
- Stores snapshots of webpages for comparison
- Easy URL management through a simple text file
- Secure credential storage using GitHub Secrets

## Setup

### 1. Add URLs to Track

Edit [urls.txt](urls.txt) and add the URLs you want to monitor (one per line):

```
https://example.com/page1
https://example.com/page2
```

### 2. Configure GitHub Secrets

To enable email notifications, you need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of the following:

#### Required Secrets:

- `SENDER_EMAIL`: Your email address (e.g., `your-email@gmail.com`)
- `SENDER_PASSWORD`: Your email password or app-specific password

#### Optional Secrets:

- `RECIPIENT_EMAIL`: Email to receive notifications (defaults to `SENDER_EMAIL` if not set)
- `SMTP_SERVER`: SMTP server address (defaults to `smtp.gmail.com`)
- `SMTP_PORT`: SMTP port (defaults to `587`)

### 3. Gmail App Password Setup

If you're using Gmail, you'll need to create an app-specific password:

1. Go to your Google Account settings
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll to **App passwords**
4. Generate a new app password for "Mail"
5. Use this 16-character password as your `SENDER_PASSWORD` secret

### 4. Enable GitHub Actions

1. Go to the **Actions** tab in your GitHub repository
2. Enable workflows if prompted
3. The workflow will run automatically every day at 7:00 AM UTC

### 5. Manual Testing

You can manually trigger the workflow to test it:

1. Go to **Actions** → **Check Webpage Changes**
2. Click **Run workflow** → **Run workflow**

## How It Works

1. The GitHub Action runs daily at 7:00 AM UTC (cron: `0 7 * * *`)
2. The script reads URLs from [urls.txt](urls.txt)
3. For each URL:
   - Fetches the current webpage content
   - Compares it with the previous snapshot (stored in `snapshots/`)
   - If changed, adds the URL to the notification list
   - Saves the new snapshot
4. If any changes were detected, sends an email notification
5. Commits updated snapshots back to the repository

## Customization

### Change the Schedule

Edit [.github/workflows/check-changes.yml](.github/workflows/check-changes.yml) and modify the cron expression:

```yaml
schedule:
  - cron: '0 7 * * *'  # Daily at 7:00 AM UTC
```

Common examples:
- `0 7 * * *` - Daily at 7:00 AM UTC
- `0 */6 * * *` - Every 6 hours
- `0 7 * * 1` - Every Monday at 7:00 AM UTC

Note: GitHub Actions uses UTC time. Convert to your local timezone as needed.

### Use a Different Email Provider

Set the `SMTP_SERVER` and `SMTP_PORT` secrets according to your provider:

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| Custom | your.smtp.server | 587 |

## Local Testing

You can test the script locally before pushing to GitHub:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@example.com"

# Run the script
python check_changes.py
```

## File Structure

```
rss-less/
├── check_changes.py              # Main script
├── urls.txt                      # List of URLs to track
├── requirements.txt              # Python dependencies
├── snapshots/                    # Stored webpage snapshots
│   └── .gitkeep
├── .github/
│   └── workflows/
│       └── check-changes.yml     # GitHub Actions workflow
└── README.md                     # This file
```

## Troubleshooting

### No emails are being sent

1. Verify your GitHub Secrets are set correctly
2. Check the Actions log for error messages
3. Ensure you're using an app-specific password for Gmail
4. Verify your SMTP settings are correct

### Workflow not running

1. Ensure GitHub Actions is enabled in your repository settings
2. Check that the workflow file is in `.github/workflows/`
3. Verify the cron syntax is correct

### Changes not being detected

1. Some websites may block automated requests - check the Actions log
2. Dynamic content (JavaScript-generated) may not be captured
3. Try manually running the workflow to test

## License

MIT
