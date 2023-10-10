## Usage
Retrieve password:
<pre>
sudo kubectl -n newswaters get secret <i>coral-app</i> -o jsonpath='{.data.password}' | base64 --decode
</pre>

## References
[CloudNativePG](https://cloudnative-pg.io/documentation/1.20/bootstrap/#bootstrap-an-empty-cluster-initdb)
