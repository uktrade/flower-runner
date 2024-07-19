#!/usr/bin/env python
"""
Simple script for starting Flower while setting the broker URL.

Flower itself allows you to specify the broker URL via the --broker argument, but does not let you
specify it in flowerconfig.py. Hence, this script is used rather than flowerconfig.py.
"""

import os
import re
from urllib.parse import urlencode

import environ
import flower.__main__
import sentry_sdk

env = environ.Env()


class ImproperlyConfigured(Exception):
    pass

def init_sentry():
    if os.environ.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=env("SENTRY_DSN"),
            environment=env("SENTRY_ENVIRONMENT"),
            traces_sample_rate=1.0,
            integrations=[],
        )

def create_email_regex(emails):
    if not emails:
        raise ValueError()

    escaped_emails = [re.escape(email.lower()) for email in emails]
    regex_body = '|'.join(escaped_emails)
    return rf'^({regex_body})$'


def validate_auth_config_and_get_whitelist():
    basic_auth = env('FLOWER_BASIC_AUTH', default=None)
    auth_provider = env('FLOWER_AUTH_PROVIDER', default=None)
    email_whitelist = env.list('EMAIL_WHITELIST', default=None)

    if not basic_auth and not (auth_provider and email_whitelist):
        raise ImproperlyConfigured(
            f'Authentication was not appropriate configured – please set either '
            f'FLOWER_AUTH_PROVIDER and EMAIL_WHITELIST, or FLOWER_BASIC_AUTH',
        )

    if email_whitelist:
        return create_email_regex(email_whitelist)

    return None


def get_broker_url():
    vcap_services = env.json('VCAP_SERVICES', default={})

    if 'redis' in vcap_services:
        _redis_base_url = vcap_services['redis'][0]['credentials']['uri']
    else:
        _redis_base_url = env('REDIS_BASE_URL')

    is_rediss = _redis_base_url.startswith('rediss://')
    url_args = {'ssl_cert_reqs': 'CERT_REQUIRED'} if is_rediss else {}
    broker_db = env.int('REDIS_BROKER_DB', default=0)

    return _build_redis_url(_redis_base_url, broker_db, **url_args)


def _build_redis_url(base_url, db_number, **query_args):
    encoded_query_args = urlencode(query_args)
    return f'{base_url}/{db_number}?{encoded_query_args}'


def main():
    init_sentry()
    email_whitelist = validate_auth_config_and_get_whitelist()
    if email_whitelist:
        os.environ['FLOWER_AUTH'] = email_whitelist
    os.environ['CELERY_BROKER_URL'] = get_broker_url()
    flower.__main__.main()


if __name__ == '__main__':
    main()
