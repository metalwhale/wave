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
  name: chloria-secrets
  namespace: playground-chloria
stringData:
  newsdata_api_key: <b>${NEWSDATA_API_KEY}</b>
</pre>
Where:
- **\${NEWSDATA_API_KEY}**: API key obtained from https://newsdata.io/
