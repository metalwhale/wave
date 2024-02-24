## Usage
Refer to the guide at [`vault` config example](/manifests/core/vault/README.md#config-example) to setup the following config:

Secret:
<pre>
vault kv put <i>clam/sandbox shell="white-shell" pearl="black-pearl"</i>
</pre>

Policy:
<pre>
vault policy write <i>sandbox-read</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>sandbox</i>" {
  capabilities = ["read"]
}
EOF
</pre>

Role:
<pre>
vault write auth/kubernetes/role/<i>sandbox-app</i> \
  bound_service_account_names=<i>sandbox-app</i> \
  bound_service_account_namespaces=<i>sandbox</i> \
  policies=<i>sandbox-read</i> \
  ttl=24h
</pre>
