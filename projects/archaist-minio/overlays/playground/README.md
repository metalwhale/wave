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
  name: archaist-env-configuration
  namespace: playground-archaist-minio
stringData:
  config.env: |-
    export MINIO_ROOT_USER=<b>${USER}</b>
    export MINIO_ROOT_PASSWORD=<b>${PASSWORD}</b>
</pre>
Where **\${USER}** and **\${PASSWORD}** are the username and password of root user.
