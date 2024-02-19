import datetime
import json
import sys
import yaml
from pathlib import Path
from zoneinfo import ZoneInfo

import kfp
from kfp.onprem import use_k8s_secret
from kfp.compiler import Compiler
from kubernetes.client.models import V1EnvVar

from ..kubeflow import login


def simple_pipeline(**inputs):
    # Load config
    with open(sys.argv[1]) as config_file:
        config_obj = yaml.safe_load(config_file)
    # Load train component
    with open(Path(__file__).parent / "train_component.yaml") as train_comp_file:
        # See: https://www.kubeflow.org/docs/components/pipelines/v1/sdk/component-development/#using-your-component-in-a-pipeline
        train_obj = yaml.safe_load(train_comp_file)
        train_obj["implementation"]["container"]["image"] = f"{config_obj["trainerImage"]}:{config_obj["version"]}"
        train_obj["implementation"]["container"]["command"] = config_obj["command"]
        train_comp_text = yaml.safe_dump(train_obj)
        train_comp = kfp.components.load_component_from_text(train_comp_text)
    # Add env vars and secrets
    train_step: kfp.dsl.ContainerOp = train_comp()
    for env_var in config_obj["envVars"]:
        if "secretName" in env_var and "secretKey" in env_var:
            train_step = train_step.apply(use_k8s_secret(
                secret_name=env_var["secretName"],
                k8s_secret_key_to_env={env_var["secretKey"]: env_var["name"]},
            ))
        elif "value" in env_var:
            train_step = train_step.add_env_variable(V1EnvVar(name=env_var["name"], value=env_var["value"]))
    # Additional placeholder env vars
    train_step = train_step.add_env_variable(V1EnvVar(name="WP_KFP_RUN_ID", value=kfp.dsl.RUN_ID_PLACEHOLDER))\
        .add_env_variable(V1EnvVar(name="WP_KFP_EXECUTION_ID", value=kfp.dsl.EXECUTION_ID_PLACEHOLDER))
    # Add inputs
    for input_env_var_name, input_value in inputs.items():
        if input_env_var_name in config_obj["runInputs"]:
            train_step = train_step.add_env_variable(
                V1EnvVar(name=config_obj["runInputs"][input_env_var_name]["envVarName"], value=input_value)
            )
    train_step.container.set_image_pull_policy("Always")


def compiple_simple_pipeline(pipeline_func) -> str:
    pipeline_file_path = str(Path(sys.argv[1]).parent.absolute() / "pipeline.yaml")
    Compiler().compile(pipeline_func=pipeline_func, package_path=pipeline_file_path)
    return pipeline_file_path


def upload_simple_pipeline(app_name: str, pipeline_file_path: str):
    client = login()
    # Load config
    with open(sys.argv[1]) as config_file:
        config_obj = yaml.safe_load(config_file)
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
    # Align pipeline version with the trainer image version for simplicity
    pipeline_version_name = f"{app_name}:{config_obj["version"]}"
    pipeline_versions = [
        v for v in client.list_pipeline_versions(pipeline_id).versions
        if v.name == pipeline_version_name
    ]
    if len(pipeline_versions) == 0:
        version_id = client.upload_pipeline_version(
            pipeline_file_path, pipeline_version_name,
            pipeline_id=pipeline_id,
        ).id
    else:
        version_id = pipeline_versions[0].id
    # Run
    if config_obj["runPolicy"] == "WhenConfigUpdated":
        job_name = f"{pipeline_version_name} {str(datetime.datetime.now(tz=ZoneInfo("Asia/Tokyo")))}"
        client.run_pipeline(
            experiment_id, job_name, pipeline_id=pipeline_id, version_id=version_id,
            params={input_key: input_param["value"] for input_key, input_param in config_obj["runInputs"].items()},
        )
