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
Install ArgoCD ([doc](https://argo-cd.readthedocs.io/en/release-2.9/getting_started/)):
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.9.7/manifests/install.yaml
```
Apply `wave` application and wait for a while for it to synchronize:
```bash
kubectl apply -n argocd -f ./application.yaml
```

### Setup DNS
Get the public IP address:
```bash
kubectl -n ingress-nginx get svc ingress-nginx-controller -o jsonpath={.status.loadBalancer.ingress}
```
Add an `A record` with host as `*.wave` and value as the above IP address at the DNS provider. After that your cluster can be accessed at <code><i>*.wave.</i><b>DOMAIN_NAME</b></code> where **DOMAIN_NAME** is the domain you registered with the DNS provider (here I chose `metalwhale.dev` for my domain but it can be any valid domain name).

## Usage
### Login to ArgoCD
The login url is: https://argocd.wave.metalwhale.dev

Or use the local url https://localhost:8080 after port-forwarding the service:
```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Run the following command to retrieve password of `admin` user (use `-D` for macOS, `-d` for linux):
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath={.data.password} | base64 -D
```
