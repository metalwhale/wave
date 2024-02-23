import datetime
import json
import os
import yaml
from pathlib import Path
from zoneinfo import ZoneInfo

import kfp
from kfp.onprem import use_k8s_secret
from kfp.compiler import Compiler
from kubernetes.client.models import V1EnvVar

from ..kubeflow import login


def notify():
    # See: https://www.deploykf.org/user-guides/access-kubeflow-pipelines-api/#authentication-flow_2, PodDefault injection
    import os
    import kfp
    kfp_client = kfp.Client()
    run = kfp_client.get_run(os.environ["WP_KFP_RUN_ID"])
    print(vars(run))


def simple_pipeline(config_obj, **inputs):
    # Load train component
    with open(Path(__file__).parent / "train_component.yaml") as train_comp_file:
        # See: https://www.kubeflow.org/docs/components/pipelines/v1/sdk/component-development/#using-your-component-in-a-pipeline
        train_obj = yaml.safe_load(train_comp_file)
        train_obj["implementation"]["container"]["image"] = f"{config_obj['container']['image']}"
        train_obj["implementation"]["container"]["command"] = config_obj["container"]["command"]
        train_comp_text = yaml.safe_dump(train_obj)
        train_op: kfp.dsl.ContainerOp = kfp.components.load_component_from_text(train_comp_text)()
    # Add env vars and secrets
    if "env" in config_obj["container"]:
        for env in config_obj["container"]["env"]:
            if "value" in env:
                train_op.container.add_env_variable(V1EnvVar(name=env["name"], value=env["value"]))
            elif "secretName" in env and "secretKey" in env:
                train_op.apply(use_k8s_secret(
                    secret_name=env["secretName"],
                    k8s_secret_key_to_env={env["secretKey"]: env["name"]},
                ))
    # Additional placeholder env vars
    train_op.container\
        .add_env_variable(V1EnvVar(name="WP_KFP_RUN_ID", value=kfp.dsl.RUN_ID_PLACEHOLDER))\
        .add_env_variable(V1EnvVar(name="WP_KFP_EXECUTION_ID", value=kfp.dsl.EXECUTION_ID_PLACEHOLDER))
    # Add inputs
    for input_env, input_value in inputs.items():
        if input_env in config_obj["runInputs"]:
            train_op.container.add_env_variable(V1EnvVar(
                name=config_obj["runInputs"][input_env]["envName"],
                value=input_value,
            ))
    train_op.container.set_image_pull_policy("Always")
    if "podAnnotations" in config_obj:
        for name, value in config_obj["podAnnotations"].items():
            train_op.add_pod_annotation(name, value)
    # Notify component
    notify_op: kfp.dsl.ContainerOp = kfp.components.create_component_from_func(
        notify,
        packages_to_install=["kfp==1.8.22"],
    )()
    notify_op.container.add_env_variable(V1EnvVar(name="WP_KFP_RUN_ID", value=kfp.dsl.RUN_ID_PLACEHOLDER))
    # For PodDefault injection, see https://github.com/deployKF/deployKF/blob/v0.1.3/generator/default_values.yaml#L1854-L1871
    notify_op.add_pod_label("kubeflow-pipelines-api-token", "true")
    notify_op.after(train_op)


def compiple_simple_pipeline(pipeline_func, pipeline_file_output_dir_path: str) -> str:
    pipeline_file_path = os.path.join(pipeline_file_output_dir_path, "pipeline.yaml")
    Compiler().compile(pipeline_func=pipeline_func, package_path=pipeline_file_path)
    return pipeline_file_path


def upload_simple_pipeline(config_obj, app_name: str, pipeline_file_path: str):
    client = login()
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
        # TODO: Delete old pipeline which has the same version but different config
    pipeline_version_name = f"{app_name}:{config_obj['version']}"
    pipeline_versions = [
        v for v in client.list_pipeline_versions(pipeline_id).versions
        if v.name == pipeline_version_name
    ]
    if len(pipeline_versions) == 0:
        version_id = client.upload_pipeline_version(
            pipeline_file_path, pipeline_version_name,
            pipeline_id=pipeline_id,
            description=f"https://github.com/metalwhale/wave/commit/{os.environ['GITHUB_SHA']}",
        ).id
    else:
        version_id = pipeline_versions[0].id
    # Run
    if config_obj["runPolicy"] == "WhenConfigChanged":
        job_name = f"{pipeline_version_name} {str(datetime.datetime.now(tz=ZoneInfo('Asia/Tokyo')))}"
        client.run_pipeline(
            experiment_id, job_name, pipeline_id=pipeline_id, version_id=version_id,
            params={input_env: input_param["value"] for input_env, input_param in config_obj["runInputs"].items()},
        )
