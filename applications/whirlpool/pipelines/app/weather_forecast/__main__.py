import yaml
from pathlib import Path

from ...util.simple_pipeline.pipeline import compiple_simple_pipeline, simple_pipeline, upload_simple_pipeline


if __name__ == "__main__":
    # Load config
    with open(str(Path(__file__).parent / "config.yaml")) as config_file:
        config_obj = yaml.safe_load(config_file)

    def pipeline(start_date: str):
        # The param names must match those in the `runInputs` section of `config.yaml` file
        simple_pipeline(config_obj, start_date=start_date)
    pipeline_file_path = compiple_simple_pipeline(pipeline, str(Path(__file__).parent))
    upload_simple_pipeline(config_obj, "weather-forecast", pipeline_file_path)
