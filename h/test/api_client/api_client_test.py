"""Unit tests for h/api_client/api_client.py."""
import mock
import pytest
import requests.exceptions

from h import api_client


@mock.patch("requests.request")
def test_get(mock_request):
    """get() should request the right URL."""
    def mock_request_function(method, url, params, timeout):
        assert method == "GET"
        assert url == "http://www.example.com/api/stream"
        assert params is None
        return mock.Mock()

    mock_request.side_effect = mock_request_function

    client = api_client.Client("http://www.example.com/api")
    client.get("/stream")

    assert mock_request.call_count == 1


@mock.patch("requests.request")
def test_get_with_trailing_slash_on_root_url(mock_request):
    """get() should handle base URLs with trailing /'s correctly."""
    def mock_request_function(method, url, params, timeout):
        assert method == "GET"
        assert url == "http://www.example.com/api/stream"
        assert params is None
        return mock.Mock()

    mock_request.side_effect = mock_request_function

    # Trailing slash.
    client = api_client.Client("http://www.example.com/api/")

    client.get("/stream")

    assert mock_request.call_count == 1


@mock.patch("requests.request")
def test_get_without_leading_slash_on_path(mock_request):
    """get() should handle paths with no leading slash.

    Even when the root_url doesn't have a trailing slash.

    """
    def mock_request_function(method, url, params, timeout):
        assert url == "http://www.example.com/api/stream"
        assert params is None
        return mock.Mock()

    mock_request.side_effect = mock_request_function

    # No trailing slash.
    client = api_client.Client("http://www.example.com/api")
    client.get("stream")  # No leading slash.

    assert mock_request.call_count == 1


@mock.patch("requests.request")
def test_get_with_url_params(mock_request):
    """get() should pass the right URL params to requests.request()."""
    def mock_request_function(method, url, params, timeout):
        assert params == {"limit": 10, "foo": "bar"}
        return mock.Mock()

    mock_request.side_effect = mock_request_function

    client = api_client.Client("http://www.example.com/api")
    client.get("/stream", params={"limit": 10, "foo": "bar"})

    assert mock_request.call_count == 1


@mock.patch("requests.request")
def test_connection_error(mock_request):
    """get() should raise ConnectionError if requests.request() does."""
    mock_request.side_effect = requests.exceptions.ConnectionError
    client = api_client.Client("http://www.example.com/api")

    with pytest.raises(api_client.ConnectionError):
        client.get("/stream")


@mock.patch("requests.request")
def test_timeout(mock_request):
    """get() should raise Timeout if requests.request() does."""
    mock_request.side_effect = requests.exceptions.Timeout
    client = api_client.Client("http://www.example.com/api")

    with pytest.raises(api_client.Timeout):
        client.get("/stream")


@mock.patch("requests.request")
def test_unknown_exception(mock_request):
    """get() should raise APIError if requests raises an unknown exception."""
    mock_request.side_effect = requests.exceptions.ChunkedEncodingError
    client = api_client.Client("http://www.example.com/api")

    with pytest.raises(api_client.APIError):
        client.get("/stream")


def test_invalid_base_url():
    """get() should raise APIError if given an invalid base_url."""
    client = api_client.Client("invalid")

    with pytest.raises(api_client.APIError):
        client.get("/stream")
