[Console]::CursorVisible = $false
kubectl config set-context desktop-linux --namespace default --cluster docker-desktop --user=docker-desktop
while($true) {
    $buffer = kubectl get pods
    cls
    $buffer
    $i = 0
    while($i -le 5) {
        $buffer = kubectl get pods
        [Console]::SetCursorPosition(0, 0)
        $buffer
        Start-Sleep -Seconds 1
        $i++
    }
}
