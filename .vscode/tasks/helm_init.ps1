winget install Helm.Helm
kubectl config set-context desktop-linux --namespace default --cluster docker-desktop --user=docker-desktop
kubectl config use-context desktop-linux
helm repo add dagster https://dagster-io.github.io/helm