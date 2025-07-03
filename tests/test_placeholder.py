import pytest


def test_placeholder(num=1):
    if not num:
        pytest.fail("Test failed!")
