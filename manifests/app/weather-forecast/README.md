## Learning database
### Create database and user
<pre>
CREATE DATABASE <i>weather</i>;

CREATE USER <i>model_trainer</i> WITH PASSWORD '<b>MODEL_TRAINER_PASSWORD</b>';
\c <i>weather</i>;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO <i>model_trainer</i>;
</pre>

### Setup secrets on Vault
Refer to the guide at [`vault` config example](../vault/README.md#config-example) to setup the following config:

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
Model trainer (`default-editor` is the name of Service Account assigned to pods that Kubeflow Runs use):
<pre>
vault write auth/kubernetes/role/<i>weather-forecast-model-trainer</i> \
  bound_service_account_names=<i>default-editor</i> \
  bound_service_account_namespaces=<i>whirlpool-weather-forecast</i> \
  policies=<i>weather-forecast-learning-database</i> \
  ttl=24h
</pre>
