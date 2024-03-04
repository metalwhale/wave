## Deploy to DigitalOcean Kubernetes (DOKS)
### Create cluster
Using Control Panel ([doc](https://docs.digitalocean.com/products/kubernetes/how-to/create-clusters/)) or Terraform (coming soon)

### Connect to cluster
Download <code><b>CLUSTER_NAME</b>-kubeconfig.yaml</code> from Control Panel ([doc](https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/)) and put in `~/.kube` directory

Setup `KUBECONFIG` ([doc](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/)):
<pre>
export KUBECONFIG=/Users/<b>USER</b>/.kube/<b>CLUSTER_NAME</b>-kubeconfig.yaml
</pre>
Test the connection by running some command:
```bash
kubectl get nodes
```

### Setup ArgoCD
#### Install
Install ArgoCD ([doc](https://argo-cd.readthedocs.io/en/release-2.9/getting_started/)):
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.7/manifests/install.yaml
```
Apply `wave` application and wait for a while for it to synchronize:
```bash
kubectl apply -n argocd -f ./application.yaml
```

#### Login
Get the public IP address:
```bash
kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath={.status.loadBalancer.ingress}
```
Get the admin password (Use `-D` for macOS, `-d` for linux):
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath={.data.password} | base64 -D
```
