## Troubleshooting
If you make changes to `tembo-operator` in [`./kustomization.yaml`](./kustomization.yaml) file or resynchronize the resources so that `tembo-pod-init` *MutatingWebhookConfiguration* is recreated, you may encounter the following error in `initdb` *Job* afterward when creating a `CoreDB` object:
<pre>
Error creating: Internal error occurred: failed calling webhook "tembo-pod-init.tembo.svc": failed to call webhook: Post "https://tembo-pod-init.tembo.svc:443/mutate?timeout=10s": tls: failed to verify certificate: x509: certificate signed by unknown authority (possibly because of "x509: invalid signature: parent certificate cannot sign this kind of certificate" while trying to verify candidate authority certificate "serial:<i>xxxxxxxxxxxx</i>")
</pre>
To fix this error, you can try recreating the pod in `tembo-po-init` *Deployment* of this namespace (by deleting it and waiting for it to be recreated), and then recreate the `CoreDB` object.
