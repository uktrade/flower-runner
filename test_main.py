import os
import re
from unittest.mock import Mock

import pytest

from main import (
    create_email_regex,
    ImproperlyConfigured,
    main,
    validate_auth_config_and_get_whitelist,
)


@pytest.fixture
def mock_environ(monkeypatch):
    old_environ = os.environ.copy()

    yield

    os.environ.clear()
    os.environ.update(old_environ)


class TestValidateAuthConfigAndGetWhitelist:
    """Tests for validate_auth_config_and_get_whitelist()."""

    @pytest.mark.parametrize(
        'env',
        [
            pytest.param(
                {},
                id='all vars missing',
            ),
            pytest.param(
                {
                    'FLOWER_AUTH_PROVIDER': 'flower.views.auth.GithubLoginHandler',
                },
                id='missing email whitelist',
            ),
            pytest.param(
                {
                    'EMAIL_WHITELIST': 'test@test.com',
                },
                id='missing auth provider',
            ),
        ],
    )
    def test_raises_exception_if_incorrectly_configured(self, env, monkeypatch):
        for key in {'FLOWER_BASIC_AUTH', 'FLOWER_AUTH_PROVIDER', 'EMAIL_WHITELIST'} - env.keys():
            monkeypatch.delenv(key, raising=False)

        for key, value in env.items():
            monkeypatch.setenv(key, value)

        with pytest.raises(ImproperlyConfigured):
            validate_auth_config_and_get_whitelist()

    @pytest.mark.parametrize(
        'env,expected_result',
        [
            pytest.param(
                {
                    'FLOWER_AUTH_PROVIDER': 'flower.views.auth.GithubLoginHandler',
                    'EMAIL_WHITELIST': 'test@test.com',
                },
                r'^(test@test\.com)$',
                id='valid auth provider config',
            ),
            pytest.param(
                {
                    'FLOWER_BASIC_AUTH': 'username:password',
                },
                None,
                id='valid basic auth config',
            ),
        ],
    )
    def test_no_error_if_correctly_configured(self, env, expected_result, monkeypatch):
        for key in {'FLOWER_BASIC_AUTH', 'FLOWER_AUTH_PROVIDER', 'EMAIL_WHITELIST'} - env.keys():
            monkeypatch.delenv(key, raising=False)

        for key, value in env.items():
            monkeypatch.setenv(key, value)

        assert validate_auth_config_and_get_whitelist() == expected_result


class TestCreateEmailRegex:
    """Tests for create_email_regex()."""

    @pytest.mark.parametrize(
        'emails,expected_regex',
        [
            (
                ['john.smith@example.com'],
                r'^(john\.smith@example\.com)$'
            ),
            (
                ['john.smith@example.com', 'roger.jones@example.com'],
                r'^(john\.smith@example\.com|roger\.jones@example\.com)$'
            ),
            (
                ['john.smith@example.com', 'roger.jones@example.com', 'me@me.com'],
                r'^(john\.smith@example\.com|roger\.jones@example\.com|me@me\.com)$'
            ),
        ],
    )
    def test_returns_regex(self, emails, expected_regex):
        assert create_email_regex(emails) == expected_regex

    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError):
            create_email_regex([])

    @pytest.mark.parametrize(
        'email_to_check,expected_result',
        [
            ('john', False),
            ('manyjohn.smith@example.com', False),
            ('john.smith@example.com.uk', False),
            ('john.smith@example.roger', False),
            ('john.smith@example.comroger.jones@example.com', False),
            ('john.smith@example.com', True),
            ('roger.jones@example.com', True),
        ]
    )
    def test_regex_behaviour(self, email_to_check, expected_result):
        emails = ['john.smith@example.com', 'roger.jones@example.com']
        regex_pattern = create_email_regex(emails)
        regex = re.compile(regex_pattern)
        assert bool(regex.match(email_to_check)) == expected_result


class TestMain:
    @pytest.mark.usefixtures('mock_environ')
    def test_main(self, monkeypatch):
        mock_flower_main = Mock()
        monkeypatch.setattr('flower.__main__.main', mock_flower_main)

        os.environ.pop('FLOWER_BASIC_AUTH', None)
        os.environ['FLOWER_AUTH_PROVIDER'] = 'flower.views.auth.GithubLoginHandler'
        os.environ['EMAIL_WHITELIST'] = 'test@example.com'
        os.environ['REDIS_BASE_URL'] = 'redis://localhost'
        os.environ['REDIS_BROKER_DB'] = '1'

        main()

        assert mock_flower_main.called
        assert os.environ['FLOWER_AUTH'] == r'^(test@example\.com)$'
        assert os.environ['CELERY_BROKER_URL'] == 'redis://localhost/1?'
