import re


def create_email_regex(emails):
    if not emails:
        raise ValueError()

    escaped_emails = [re.escape(email.lower()) for email in emails]
    regex_body = '|'.join(escaped_emails)
    return rf'^({regex_body})$'
