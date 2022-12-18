from unittest import mock

import pytest
from airflow.exceptions import AirflowNotFoundException
from common import matrix


@pytest.mark.parametrize(
    "environment, slack_message_override, expected_result",
    [
        # Dev
        # Message is not sent by default. It is only sent if the override is enabled.
        # Default
        ("dev", False, False),
        # Override is enabled
        ("dev", True, True),
        # Prod
        # Message is sent by default; the override has no effect.
        # Default
        ("prod", False, True),
        # Override enabled
        ("prod", True, True),
    ],
)
def test_should_send_message(environment, slack_message_override, expected_result):
    with mock.patch("common.matrix.Variable") as MockVariable:
        MockVariable.get.return_value = slack_message_override
        assert matrix.should_send_message(environment) == expected_result


@pytest.mark.parametrize("environment", ["dev", "prod"])
def test_should_send_message_is_false_without_hook(environment):
    with mock.patch("common.matrix.HttpHook") as HttpHookMock:
        conn_mock = HttpHookMock.return_value.get_conn
        conn_mock.side_effect = AirflowNotFoundException("nope")
        assert not matrix.should_send_message(environment)
