import json

import kfp


def notify(client: kfp.Client, run_id: str, step_id: str):
    # TODO: Find a better way to retrieve output path
    run = client.get_run(run_id)
    workflow_manifest = json.loads(run.to_dict()["pipeline_runtime"]["workflow_manifest"])
    output_path_s3_keys = [
        a["s3"]["key"]
        for a in workflow_manifest["status"]["nodes"][step_id]["outputs"]["artifacts"]
        if a["name"] == "train-output_path"
    ]
    if len(output_path_s3_keys) > 0:
        print(output_path_s3_keys[0])
