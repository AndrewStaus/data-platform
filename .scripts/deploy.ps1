$dbt_path = ".\data_foundation\dbt"
$branch_id = (-join ((97..122) | Get-Random -Count 15 | ForEach-Object {[char]$_}))

Write-Host("`nBUILDING FOUNDATION DOCKER IMAGE")
cd ./data_foundation/
$new_foundation_image = "dagster/data-foundation:"+$branch_id
$destination__password = ((Get-Content .env.prod) -match 'DESTINATION__PASSWORD=(.*)').split("=")[1].trim()
docker build . --target data_foundation -t $new_foundation_image --build-arg DESTINATION__PASSWORD=$destination__password
cd ..

Write-Host("`nBUILDING SCIENCE DOCKER IMAGE")
cd ./data_science/
$new_science_image = "dagster/data-science:"+$branch_id
$destination__password = ((Get-Content .env.prod) -match 'DESTINATION__PASSWORD=(.*)').split("=")[1].trim()
docker build . --target data_science -t $new_science_image --build-arg DESTINATION__PASSWORD=$destination__password
cd ..

Write-Host("`nDEPLOYING BUILD")
helm repo update
$values = Get-Content -Path .\.scripts\helm_template.yaml
$values = $values -replace "{{ branch_id }}", $branch_id
$values | Out-File -FilePath .\.scripts\helm_values.yaml
helm upgrade --install --hide-notes dagster dagster/dagster `
    -f .\.scripts\helm_values.yaml

Write-Host("`nCLEANING KUBERNETES")
kubectl delete pod --field-selector=status.phase==Succeeded
kubectl delete pod --field-selector=status.phase==Failed
kubectl delete pod --field-selector=status.phase==Completed
kubectl delete pod --field-selector=status.phase==ErrImagePull
kubectl delete pod --field-selector=status.phase==ImagePullBackoff

Write-Host("`nCLEANING DOCKER REPOSITORY")

$old_foundation_image=docker inspect data-foundation | ConvertFrom-Json
$old_foundation_image=$old_foundation_image.Config.Image

docker stop data-foundation
docker rm data-foundation

docker container create -t --name data-foundation $new_foundation_image

docker stop data-foundation-rollback
docker rm data-foundation-rollback
docker container create -t --name data-foundation-rollback $old_foundation_image

###

$old_science_image=docker inspect data-science | ConvertFrom-Json
$old_science_image=$old_science_image.Config.Image

docker stop data-science
docker rm data-science

docker container create -t --name data-science $new_science_image

docker stop data-science-rollback
docker rm data-science-rollback
docker container create -t --name data-science-rollback $new_science_image

Start-Sleep 5
docker image prune -a --force

Write-Host("`nDEPLOYMENT COMPLETE")
Write-Host("Branch ID: " + $branch_id + "`n")

Write-Host("`BUILDING DBT Deferal Target")
$defer_path = $dbt_path+"\state\"
if (!(Test-Path -Path $defer_path -PathType Container)) {
    New-Item -Path $defer_path -ItemType Directory
}
Copy-Item -Path $dbt_path"\target\manifest.json" -Destination $defer_path -Force

uv run --env-file .env.prod dbt parse --project-dir $dbt_path --profiles-dir $dbt_path --target prod

Write-Host("`CREATING PROJECT DOCS")
uv run mkdocs build
uv run --env-file .env.prod dbt docs generate --project-dir $dbt_path --target prod