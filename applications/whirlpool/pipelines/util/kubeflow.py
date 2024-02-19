import os
import re
import requests
from urllib.parse import urlsplit

import kfp


def login() -> kfp.Client:
    kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
    kubeflow_username = os.environ["KUBEFLOW_USERNAME"]
    kubeflow_password = os.environ["KUBEFLOW_PASSWORD"]
    auth_session = _get_istio_auth_session(
        url=kubeflow_endpoint,
        username=kubeflow_username,
        password=kubeflow_password
    )
    client = kfp.Client(host=f"{kubeflow_endpoint}/pipeline", cookies=auth_session["session_cookie"])
    return client


def _get_istio_auth_session(url: str, username: str, password: str) -> dict:
    # See: https://www.kubeflow.org/docs/components/pipelines/v1/sdk/connect-api/#full-kubeflow-subfrom-outside-clustersub
    auth_session = {
        "endpoint_url": url,    # KF endpoint URL
        "redirect_url": None,   # KF redirect URL, if applicable
        "dex_login_url": None,  # Dex login URL (for POST of credentials)
        "is_secured": None,     # True if KF endpoint is secured
        "session_cookie": None  # Resulting session cookies in the form "key1=value1; key2=value2"
    }
    with requests.Session() as s:
        resp = s.get(url, allow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(
                f"HTTP status code '{resp.status_code}' for GET against: {url}"
            )
        auth_session["redirect_url"] = resp.url
        if len(resp.history) == 0:
            auth_session["is_secured"] = False
            return auth_session
        else:
            auth_session["is_secured"] = True
        redirect_url_obj = urlsplit(auth_session["redirect_url"])
        if re.search(r"/auth$", redirect_url_obj.path):
            redirect_url_obj = redirect_url_obj._replace(
                path=re.sub(r"/auth$", "/auth/local", redirect_url_obj.path)
            )
        if re.search(r"/auth/.*/login$", redirect_url_obj.path):
            auth_session["dex_login_url"] = redirect_url_obj.geturl()
        else:
            resp = s.get(redirect_url_obj.geturl(), allow_redirects=True)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"HTTP status code '{resp.status_code}' for GET against: {redirect_url_obj.geturl()}"
                )
            auth_session["dex_login_url"] = resp.url
        resp = s.post(
            auth_session["dex_login_url"],
            data={"login": username, "password": password},
            allow_redirects=True
        )
        if len(resp.history) == 0:
            raise RuntimeError(
                f"Login credentials were probably invalid - "
                f"No redirect after POST to: {auth_session['dex_login_url']}"
            )
        auth_session["session_cookie"] = "; ".join([f"{c.name}={c.value}" for c in s.cookies])
    return auth_session
