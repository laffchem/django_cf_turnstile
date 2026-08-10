from unittest.mock import patch

import pytest


@pytest.fixture
def mock_post():
    with patch("niquests.Session.post") as mock:
        yield mock
