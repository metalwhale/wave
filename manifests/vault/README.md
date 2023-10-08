## Usage
### Initial setup
Initialize ([reference](https://www.hashicorp.com/blog/announcing-the-vault-helm-chart)):
<pre>
sudo kubectl -n vault exec -it <i>clam-vault-0</i> -- vault operator init -format yaml
</pre>
<details><summary>Output:</summary>

<pre>
Unseal Key 1: <b>KEY_1</b>
Unseal Key 2: <b>KEY_2</b>
Unseal Key 3: <b>KEY_3</b>
Unseal Key 4: <b>KEY_4</b>
Unseal Key 5: <b>KEY_5</b>

Initial Root Token: <b>ROOT_TOKEN</b>

Vault initialized with 5 key shares and a key threshold of 3. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 3 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated root key. Without at least 3 keys to
reconstruct the root key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
</pre>
</details>

Unseal (`Threshold` = 3):
<pre>
sudo kubectl -n vault exec -it <i>clam-vault-0</i> -- vault operator unseal <b>KEY_1</b>
sudo kubectl -n vault exec -it <i>clam-vault-0</i> -- vault operator unseal <b>KEY_2</b>
sudo kubectl -n vault exec -it <i>clam-vault-0</i> -- vault operator unseal <b>KEY_3</b>
</pre>

Start an interactive shell session:
<pre>
sudo kubectl -n vault exec -it <i>clam-vault-0</i> -- /bin/sh
</pre>

Login with the root token ([reference](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-minikube-raft#set-a-secret-in-vault)):
```bash
vault login
```

Enable KV secrets:
<pre>
vault secrets enable -path=<i>clam</i> kv-v2
</pre>

Enable Kubernetes authentication:
```bash
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
```

### Config example
Create secret:
<pre>
vault kv put <i>clam/sample key="value"</i>
</pre>

Create policy:
<pre>
vault policy write <i>sample-read</i> - &lt&ltEOF
path "<i>clam</i>/data/<i>sample</i>" {
  capabilities = ["read"]
}
EOF
</pre>

Create role:
<pre>
vault write auth/kubernetes/role/<i>sample-app</i> \
  bound_service_account_names=<i>sample-app</i> \
  bound_service_account_namespaces=<i>sample</i> \
  policies=<i>sample-read</i> \
  ttl=24h
</pre>

Exit the pod:
```bash
exit
```

## References
[Injecting secrets via Vault Agent](https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-sidecar)

Other methods:
- [External Secrets Operator (ESO)](https://external-secrets.io/v0.9.5/)
- [Kubernetes Secrets Store CSI Driver (SSCSID) guide](https://kubernetes.io/docs/concepts/security/secrets-good-practices/#configure-access-to-external-secrets)

ESO vs SSCSID:
- [Clarity: secrets store CSI driver vs external secrets... what to use?](https://github.com/external-secrets/external-secrets/issues/478)
- [External Secrets Operator vs. Secret Store CSI Driver ](https://www.reddit.com/r/kubernetes/comments/uj4a56/external_secrets_operator_vs_secret_store_csi/)
- [Comparing External Secrets Operator with Secret Storage CSI as Kubernetes External Secrets is Deprecated](https://mixi-developers.mixi.co.jp/compare-eso-with-secret-csi-402bf37f20bc)
