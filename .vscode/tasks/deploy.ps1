# setup env
$env:DESTINATION__USER = ((Get-Content .env.prod) -match 'DESTINATION__USER=(.*)').split("=")[1].trim()
$env:DESTINATION__DATABASE = ((Get-Content .env.prod) -match 'DESTINATION__DATABASE=(.*)').split("=")[1].trim()
$env:DESTINATION__HOST = ((Get-Content .env.prod) -match 'DESTINATION__HOST=(.*)').split("=")[1].trim()
$env:DESTINATION__ROLE = ((Get-Content .env.prod) -match 'DESTINATION__ROLE=(.*)').split("=")[1].trim()
$env:DESTINATION__PASSWORD = ((Get-Content .env.prod) -match 'DESTINATION__PASSWORD=(.*)').split("=")[1].trim()
$env:DESTINATION__WAREHOUSE = ((Get-Content .env.prod) -match 'DESTINATION__WAREHOUSE=(.*)').split("=")[1].trim()
$env:TARGET = ((Get-Content .env.prod) -match 'TARGET=(.*)').split("=")[1].trim()

$dbt_path = ".\packages\data_foundation\dbt"
$tag = (-join ((97..122) | Get-Random -Count 15 | ForEach-Object {[char]$_}))
$foundation_image = "dagster/data-foundation:"+$tag
$science_image = "dagster/data-science:"+$tag
$defer_path = $dbt_path+"\state\"

# build docker
Write-Host("`nBUILDING FOUNDATION DOCKER IMAGE")
docker build . -f Dockerfile.data_foundation --target data_foundation -t $foundation_image `
    --build-arg TARGET="prod" `
    --secret id=destination__user,env=DESTINATION__USER `
    --secret id=destination__database,env=DESTINATION__DATABASE `
    --secret id=destination__host,env=DESTINATION__HOST `
    --secret id=destination__role,env=DESTINATION__ROLE `
    --secret id=destination__password,env=DESTINATION__PASSWORD `
    --secret id=destination__warehouse,env=DESTINATION__WAREHOUSE
    
Write-Host("`nBUILDING SCIENCE DOCKER IMAGE")
docker build . -f Dockerfile.data_science --target data_science -t $science_image

# deploy to kubernetes
Write-Host("`nDEPLOYING BUILD")
winget install Helm.Helm
kubectl config set-context desktop-linux --namespace default --cluster docker-desktop --user=docker-desktop
kubectl config use-context desktop-linux
helm repo add dagster https://dagster-io.github.io/helm
helm repo update
kubectl delete secret destination-password
kubectl create secret generic destination-password `
    --from-literal=DESTINATION__PASSWORD='$env:DESTINATION__PASSWORD'

helm upgrade --install --hide-notes dagster dagster/dagster `
    -f .\.helm\prod\values.yaml `
    --set dagster-user-deployments.deployments[0].image.tag=$tag `
    --set dagster-user-deployments.deployments[1].image.tag=$tag

# clean old workers
Write-Host("`nCLEANING KUBERNETES")
kubectl delete pod --field-selector=status.phase==Succeeded
kubectl delete pod --field-selector=status.phase==Failed
kubectl delete pod --field-selector=status.phase==Completed
kubectl delete pod --field-selector=status.phase==ErrImagePull
kubectl delete pod --field-selector=status.phase==ImagePullBackoff

# clean old images
Write-Host("`nCLEANING DOCKER REPOSITORY")
docker stop data-foundation
docker rm data-foundation
docker container create --name data-foundation $foundation_image

docker stop data-science
docker rm data-science
docker container create -t --name data-science $science_image

Start-Sleep 5
docker image prune -a --force

Write-Host("`nDEPLOYMENT COMPLETE")
Write-Host("Branch ID: " + $tag + "`n")

# Write-Host("`BUILDING DBT Deferal Target")
# if (!(Test-Path -Path $defer_path -PathType Container)) {
#     New-Item -Path $defer_path -ItemType Directory
# }
# Copy-Item -Path $dbt_path"\target\manifest.json" -Destination $defer_path -Force

# .\packages\data_foundation\.venv\Scripts\activate
# uv run --env-file .env.prod dbt parse --project-dir $dbt_path --profiles-dir $dbt_path --target prod

# # Write-Host("`CREATING PROJECT DOCS") # fusion does not have doc generation yet
# # uv run --env-file .env.prod dbt docs generate --project-dir $dbt_path --target prod