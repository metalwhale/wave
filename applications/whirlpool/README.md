## Note
We are using `kfp==1.8.22` because deployKF version `0.1.3` requires Kubeflow Pipelines version `2.0.0-alpha.7`, which is v1.
See more at: [Access Kubeflow Pipelines API](https://www.deploykf.org/user-guides/access-kubeflow-pipelines-api/)

## Usage example
```bash
GITHUB_SHA=DUMMY_SHA python3 -m pipelines.app.weather_forecast
```
