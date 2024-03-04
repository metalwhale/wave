## Secret for Grafana provider credential
### Secret values
([Reference](https://github.com/grafana/crossplane-provider-grafana/issues/32#issuecomment-1709965896))
<pre>
vault kv put <i>clam/whirlpool/grafana</i> \
  <i>provider_credential='{"auth":"admin:<b>ADMIN_PASSWORD</b>","url":"https://grafana.whirlpool.wave.m-cloud.dev"}'</i>
</pre>
With **ADMIN_PASSWORD** got from `monitor-grafana` secret, `admin-password` key.

### Policy
<pre>
vault policy write <i>whirlpool-grafana</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>whirlpool/grafana</i>" {
  capabilities = ["read"]
}
EOF
</pre>

### Role
<pre>
vault write auth/kubernetes/role/<i>whirlpool-grafana-provider</i> \
  bound_service_account_names=<i>grafana-provider</i> \
  bound_service_account_namespaces=<i>whirlpool</i> \
  policies=<i>whirlpool-grafana</i> \
  ttl=24h
</pre>

## Secret for `weather-forecast` data source
### Secret values
<pre>
vault kv put <i>clam/whirlpool/grafana/weather-forecast</i> \
  <i>learning_database='{"password":"<b>MONITOR_PASSWORD</b>"}'</i>
</pre>
The secure json data has `password` key ([reference](https://grafana.com/docs/grafana/latest/datasources/postgres/#provisioning-example)), with **MONITOR_PASSWORD** created at [`weather-forecast`](/manifests/app/weather-forecast/README.md).

### Policy
<pre>
vault policy write <i>whirlpool-grafana-weather-forecast</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>whirlpool/grafana/weather-forecast</i>" {
  capabilities = ["read"]
}
EOF
</pre>

### Role
<pre>
vault write auth/kubernetes/role/<i>whirlpool-grafana-weather-forecast-monitor</i> \
  bound_service_account_names=<i>monitor</i> \
  bound_service_account_namespaces=<i>whirlpool</i> \
  policies=<i>whirlpool-grafana-weather-forecast</i> \
  ttl=24h
</pre>

## Tips
To forcibly delete an organization, modify its finalizers as follows ([reference](https://stackoverflow.com/questions/52009124/not-able-to-completely-remove-kubernetes-customresource#comment105958532_52012367)):
<pre>
sudo kubectl -n whirlpool patch organization <b>ORGANIZATION_NAME</b> -p '{"metadata":{"finalizers":[]}}' --type=merge
</pre>
