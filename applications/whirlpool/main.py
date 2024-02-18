import datetime
import json
import os
import re
import requests
import sys
from importlib import import_module
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import kfp


def get_istio_auth_session(url: str, username: str, password: str) -> dict:
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


def upload_pipeline(
    client: kfp.Client, app_name: str, pipeline_version: str,
    job_params: dict = None, run_job: bool = False,
):
    app_dir_name = app_name.replace("-", "_")
    app_dir_path = Path(__file__).parent / "pipelines" / app_dir_name
    if not os.path.exists(app_dir_path):
        print(f"App name '{app_name}' (dir path '{app_dir_path}') does not exist")
        exit(1)
    # Compile pipeline
    module_name, method_name = f"pipelines.{app_dir_name}.pipeline.pipeline".rsplit(".", 1)
    pipeline_func = getattr(import_module(module_name), method_name)
    pipeline_file_path = str(app_dir_path / "pipeline.yaml")
    kfp.compiler.Compiler().compile(pipeline_func=pipeline_func, package_path=pipeline_file_path)
    # Experiment
    experiment_name = app_name
    experiment_id = client.create_experiment(experiment_name, namespace=f"whirlpool-{app_name}").id  # Idempotent?
    # Pipeline
    pipeline_name = app_name
    pipelines = client.list_pipelines(filter=json.dumps(
        {"predicates": [{"key": "name", "op": 1, "string_value": pipeline_name}]}
    )).pipelines
    if pipelines is None:
        # Default version (no version number)
        pipeline_id = client.upload_pipeline(pipeline_name=pipeline_name, pipeline_package_path=pipeline_file_path).id
    else:
        pipeline_id = pipelines[0].id
    pipeline_version_name = f"{app_name}:{pipeline_version}"
    pipeline_version_ids = [
        v.id for v in client.list_pipeline_versions(pipeline_id).versions
        if v.name == pipeline_version_name
    ]
    if len(pipeline_version_ids) == 0:
        version_id = client.upload_pipeline_version(
            pipeline_file_path, pipeline_version_name,
            pipeline_id=pipeline_id,
        ).id
    else:
        version_id = pipeline_version_ids[0]
    # Run
    if run_job:
        job_name = f"{pipeline_version_name} {str(datetime.datetime.now(tz=ZoneInfo('Asia/Tokyo')))}"
        client.run_pipeline(experiment_id, job_name, pipeline_id=pipeline_id, version_id=version_id, params=job_params)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 main.py APP_NAME PIPELINE_VERSION")
        exit(1)
    # Login
    kubeflow_endpoint = os.environ["KUBEFLOW_ENDPOINT"]
    kubeflow_username = os.environ["KUBEFLOW_USERNAME"]
    kubeflow_password = os.environ["KUBEFLOW_PASSWORD"]
    auth_session = get_istio_auth_session(
        url=kubeflow_endpoint,
        username=kubeflow_username,
        password=kubeflow_password
    )
    client = kfp.Client(host=f"{kubeflow_endpoint}/pipeline", cookies=auth_session["session_cookie"])
    # Upload pipeline
    app_name = sys.argv[1]
    pipeline_version = sys.argv[2]
    upload_pipeline(client, app_name, pipeline_version, run_job=True, job_params={
        # TODO: Change to command line args
        "input_start_date": str(datetime.datetime.now()),
        "trainer_image": f"metalwhaledev/weather-forecast-model-trainer:{pipeline_version}",
    })
