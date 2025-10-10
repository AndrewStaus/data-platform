cls
while ($true) {
    Start-Sleep -Seconds 1

    $DAGSTER_WEBSERVER_POD_NAME=( `
        kubectl get pods --namespace default `
        -l "app.kubernetes.io/name=dagster,app.kubernetes.io/instance=dagster,component=dagster-webserver" `
        -o jsonpath="{.items[0].metadata.name}" `
    )

    kubectl port-forward $DAGSTER_WEBSERVER_POD_NAME 63446:80
}