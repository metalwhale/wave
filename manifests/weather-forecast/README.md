## Create database and user
<pre>
CREATE DATABASE <i>weather</i>;

CREATE USER <i>model_trainer</i> WITH PASSWORD '<b>DATABASE_PASSWORD</b>';
GRANT ALL PRIVILEGES ON DATABASE <i>weather</i> TO <i>model_trainer</i>;
</pre>

## Setup secrets on Vault
Refer to the guide at [`vault` config example](../vault/README.md#config-example) to setup the following config:

### Secret values
<pre>
vault kv put <i>clam/weather-forecast/model-trainer database_password="<b>DATABASE_PASSWORD</b>"</i>
</pre>

### Policy
<pre>
vault policy write <i>weather-forecast-model-trainer</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>weather-forecast/model-trainer</i>" {
  capabilities = ["read"]
}
EOF
</pre>

### Role
<pre>
vault write auth/kubernetes/role/<i>weather-forecast-model-trainer</i> \
  bound_service_account_names=<i>default-editor</i> \
  bound_service_account_namespaces=<i>whirlpool-weather-forecast</i> \
  policies=<i>weather-forecast-model-trainer</i> \
  ttl=24h
</pre>
Note: `default-editor` is the name of Service Account assigned to pods that Kubeflow Runs use
