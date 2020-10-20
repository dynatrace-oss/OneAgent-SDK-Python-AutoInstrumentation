from mock import patch

from autodynatrace.wrappers.django.utils import get_host, get_request_uri, get_app_name


@patch("django.http.HttpRequest")
def test_get_host(django_request_mock):
    django_request_mock.get_host = lambda: "myhost:80"
    assert get_host(django_request_mock) == "myhost:80"

    django_request_mock.get_host = lambda: None
    django_request_mock.META = {"HTTP_HOST": "myhost:80"}
    assert get_host(django_request_mock) == "myhost:80"

    django_request_mock.META = {"SERVER_NAME": "myhost", "SERVER_PORT": 80}
    assert get_host(django_request_mock) == "myhost:80"

    django_request_mock.META = {}
    assert get_host(django_request_mock) == "unknown"

    django_request_mock = None
    assert get_host(django_request_mock) == "unknown"


@patch("django.http.HttpRequest")
def test_get_request_uri(django_request_mock):
    django_request_mock.get_host = lambda: "myhost:80"
    django_request_mock.scheme = "http"
    django_request_mock.path = "/path"

    assert get_request_uri(django_request_mock) == "http://myhost:80/path"


@patch("django.http.HttpRequest")
def test_get_app_name(django_request_mock):
    django_request_mock.path = "/path"
    django_request_mock.META = {"SERVER_NAME": "myhost", "SERVER_PORT": 80}
    assert get_app_name(django_request_mock) == "Django (myhost:80)"
