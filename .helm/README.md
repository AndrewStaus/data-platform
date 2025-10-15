# .helm/

Helm charts for deploying to Kubernetes.

## Purpose

Helm charts define, install, and upgrade even the most complex Kubernetes applications.
This directory centralizes the Helm charts used by this project, allowing for consistent
and version-controlled deployments.

## Contents

- `Chart.yaml`: Contains metadata about the chart (name, version, description).
- `values.yaml`: Defines the default configuration values for the chart.
- `templates/`: Contains Kubernetes manifest templates (e.g., Deployments, Services,
Ingresses) that Helm renders using the provided values.
- `charts/`: (Optional) Contains dependent Helm charts.

## Usage

To use these Helm charts:

1. **Install Helm:** Ensure you have Helm installed and configured for your Kubernetes
cluster.
3. **Create a Tag:**  This will typically be the id of commit for the merge into the
deployment branch so that a image can be traced back to a code version.  With Dagster,
it is best practice to specify a unique tag for each deployment so that Dagster can
identify that a new user-code version is available, otherwise it may not load the
change.
    ```bash
        $tag=615728ca1e37a5cab111b2b0b743f363ddfce7ae
    ```

2. **Build Docker Images:** Build the docker images in the root directory using the
specified tag.
    ```bash
        docker build . -f Dockerfile.data_foundation \
            -t dagster/data-foundation:$tag \
            --target data_foundation \
            --secret id=DESTINATION__PASSWORD,env=DESTINATION__PASSWORD
    ```

    ```bash
        docker build . -f Dockerfile.data_science \
            -t dagster/data-science:$tag \
            --target data_science
    ```

3. **Add Repository:**  run `helm repo add dagster https://dagster-io.github.io/helm`
to install the repository.
4. **Install/Upgrade Charts:** Navigate to the project root and use the `helm install`
or `helm upgrade` commands, specifying the path to the desired chart within the `.helm`
directory.

    ```bash
    helm upgrade --install dagster dagster/dagster \
        -f .\.helm\values.yaml \
        --set dagster-user-deployments.deployments[0].image.tag=$tag \
        --set dagster-user-deployments.deployments[1].image.tag=$tag
    ```