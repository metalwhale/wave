## Instructions
Retrieve the password of `admin` user:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath={.data.password} | base64 -d
```
