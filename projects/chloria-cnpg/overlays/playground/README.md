## Notes
[`sealedsecret.yaml`](./sealedsecret.yaml) file was generated from a secret file using `kubeseal` command:
```bash
kubeseal --controller-namespace core-sealed-secrets --controller-name sealed-secrets -f secret.yaml -w sealedsecret.yaml
```
<pre>
# Content of `secret.yaml` file
---
apiVersion: v1
kind: Secret
metadata:
  annotations:
    reflector.v1.k8s.emberstack.com/reflection-allowed: "true"
    reflector.v1.k8s.emberstack.com/reflection-allowed-namespaces: "playground-chloria*"
  name: chloria-cnpg-cluster-init-auth
  namespace: playground-chloria-cnpg
type: kubernetes.io/basic-auth
stringData:
  username: app
  password: <b>${PASSWORD}</b>
</pre>
With the username **`app`** matches the `owner` in [`../../source/templates/application.yaml`](../../source/templates/application.yaml) file.
