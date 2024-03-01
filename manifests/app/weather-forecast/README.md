## Learning database
### Create database and user
<pre>
\c <i>app</i>;

CREATE USER <i>model_trainer</i> WITH PASSWORD '<b>MODEL_TRAINER_PASSWORD</b>';
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO <i>model_trainer</i>;

CREATE USER <i>monitor</i> WITH PASSWORD '<b>MONITOR_PASSWORD</b>';
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO <i>monitor</i>;
</pre>
- `app`: default database name when using Tembo
- `model_trainer` is used at [`whirlpool-weather-forecast`](/manifests/core/whirlpool-weather-forecast)
- `monitor` is used at [`whirlpool/grafana`](/manifests/core/whirlpool/grafana)

### Setup secrets on Vault
Refer to the guide at [`vault` config example](/manifests/core/vault/README.md#config-example) to setup the following config:

#### Secret values
<pre>
vault kv put <i>clam/weather-forecast/learning-database</i> \
  <i>model_trainer_password="<b>MODEL_TRAINER_PASSWORD</b>"</i>
</pre>

#### Policy
<pre>
vault policy write <i>weather-forecast-learning-database</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>weather-forecast/learning-database</i>" {
  capabilities = ["read"]
}
EOF
</pre>

#### Role
Whirlpool model trainer (reuse `default-editor` service account, created by Kubeflow, will be assigned to pods that Kubeflow Runs use):
<pre>
vault write auth/kubernetes/role/<i>weather-forecast-model-trainer</i> \
  bound_service_account_names=<i>default-editor</i> \
  bound_service_account_namespaces=<i>whirlpool-weather-forecast</i> \
  policies=<i>weather-forecast-learning-database</i> \
  ttl=24h
</pre>
