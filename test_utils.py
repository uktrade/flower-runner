import re

import pytest

from utils import create_email_regex


class TestCreateEmailRegex:
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
