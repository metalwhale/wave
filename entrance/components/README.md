## Notes
- Charts in each subdirectory were created by running:
  <pre>
  docker run --rm -v ${PWD}/:/apps alpine/helm:3.15.4 create <b>NAME</b>
  </pre>
  The version `3.15.4` was chosen to match [`helm3_version` in ArgoCD](https://github.com/argoproj/argo-cd/blob/v2.13.2/hack/tool-versions.sh#L14)
