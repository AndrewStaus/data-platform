$env:DESTINATION__PASSWORD = ((Get-Content .env.prod) -match 'DESTINATION__PASSWORD=(.*)').split("=")[1].trim()
$dbt_path = ".\data_foundation\dbt"
$tag = (-join ((97..122) | Get-Random -Count 15 | ForEach-Object {[char]$_}))
$new_foundation_image = "dagster/data-foundation:"+$tag
$new_science_image = "dagster/data-science:"+$tag
$old_foundation_image=docker inspect data-foundation | ConvertFrom-Json
$old_foundation_image=$old_foundation_image.Config.Image
$old_science_image=docker inspect data-science | ConvertFrom-Json
$old_science_image=$old_science_image.Config.Image
$defer_path = $dbt_path+"\state\"

Write-Host("`nBUILDING FOUNDATION DOCKER IMAGE")
docker build . -f Dockerfile.data_foundation --target data_foundation -t $new_foundation_image `
    --secret id=DESTINATION__PASSWORD,env=DESTINATION__PASSWORD
    
Write-Host("`nBUILDING SCIENCE DOCKER IMAGE")
docker build . -f Dockerfile.data_science --target data_science -t $new_science_image

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
    -f .\.helm\values.yaml `
    --set dagster-user-deployments.deployments[0].image.tag=$tag `
    --set dagster-user-deployments.deployments[1].image.tag=$tag

Write-Host("`nCLEANING KUBERNETES")
kubectl delete pod --field-selector=status.phase==Succeeded
kubectl delete pod --field-selector=status.phase==Failed
kubectl delete pod --field-selector=status.phase==Completed
kubectl delete pod --field-selector=status.phase==ErrImagePull
kubectl delete pod --field-selector=status.phase==ImagePullBackoff

# Write-Host("`nCLEANING DOCKER REPOSITORY")
# docker stop data-foundation
# docker rm data-foundation
# docker container create -t --name data-foundation $new_foundation_image
# docker stop data-foundation-rollback
# docker rm data-foundation-rollback
# docker container create -t --name data-foundation-rollback $old_foundation_image

# docker stop data-science
# docker rm data-science
# docker container create -t --name data-science $new_science_image
# docker stop data-science-rollback
# docker rm data-science-rollback
# docker container create -t --name data-science-rollback $new_science_image

# Start-Sleep 5
# docker image prune -a --force

# Write-Host("`nDEPLOYMENT COMPLETE")
# Write-Host("Branch ID: " + $tag + "`n")

# Write-Host("`BUILDING DBT Deferal Target")
# if (!(Test-Path -Path $defer_path -PathType Container)) {
#     New-Item -Path $defer_path -ItemType Directory
# }
# Copy-Item -Path $dbt_path"\target\manifest.json" -Destination $defer_path -Force

# .\data_foundation\.venv\Scripts\activate
# uv run --env-file .env.prod dbt parse --project-dir $dbt_path --profiles-dir $dbt_path --target prod

# # Write-Host("`CREATING PROJECT DOCS") # fusion does not have doc generation yet
# # uv run --env-file .env.prod dbt docs generate --project-dir $dbt_path --target prod