from ..util.simple_pipeline.pipeline import compiple_simple_pipeline, simple_pipeline, upload_simple_pipeline


def pipeline(start_date: str):
    # The param names must match those in the `runInputs` section of `config.yaml` file
    simple_pipeline(start_date=start_date)


pipeline_file_path = compiple_simple_pipeline(pipeline)
upload_simple_pipeline("weather-forecast", pipeline_file_path)
