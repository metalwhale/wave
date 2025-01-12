## Instructions
Trust the tenant's CA in MinIO Operator ([Doc](https://min.io/docs/minio/kubernetes/upstream/operations/cert-manager/cert-manager-tenants.html#trust-the-tenant-s-ca-in-minio-operator)):
<pre>
kubectl -n <b>${environment}</b>-archaist-minio get secrets archaist-minio-ca-tls -o=jsonpath='{.data.ca\.crt}' | base64 -d > archaist-minio-ca.crt
kubectl -n core-minio-operator create secret generic operator-ca-tls-archaist --from-file=ca.crt=archaist-minio-ca.crt
</pre>
