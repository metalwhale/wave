from pathlib import Path

import kfp
import kfp.components as comp
from kubernetes.client.models import V1EnvVar

with open(Path(__file__).parent / "train_component.yaml") as train_comp_file:
    # See: https://www.kubeflow.org/docs/components/pipelines/v1/sdk/component-development/#using-your-component-in-a-pipeline
    train_comp_text = train_comp_file.read()
    train_comp = comp.load_component_from_text(train_comp_text)


def pipeline(input_start_date: str, trainer_image: str):
    # See more about the env vars at model repo: https://github.com/metalwhale/weather-forecast-model
    train_step: kfp.dsl.ContainerOp = train_comp()\
        .add_env_variable(V1EnvVar(name="WP_INPUT_DATABASE_HOST", value="host"))\
        .add_env_variable(V1EnvVar(name="WP_INPUT_DATABASE_PORT", value="port"))\
        .add_env_variable(V1EnvVar(name="WP_INPUT_DATABASE_DB", value="db"))\
        .add_env_variable(V1EnvVar(name="WP_INPUT_DATABASE_USER", value="user"))\
        .add_env_variable(V1EnvVar(name="WP_INPUT_START_DATE", value=input_start_date))\
        .add_env_variable(V1EnvVar(name="WP_KFP_RUN_ID", value=kfp.dsl.RUN_ID_PLACEHOLDER))\
        .add_env_variable(V1EnvVar(name="WP_KFP_EXECUTION_ID", value=kfp.dsl.EXECUTION_ID_PLACEHOLDER))
    train_step.container.image = trainer_image  # See: https://github.com/kubeflow/pipelines/issues/4572#issuecomment-703055554
    train_step.container.set_image_pull_policy("Always")
