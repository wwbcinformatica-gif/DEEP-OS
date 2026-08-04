Write-Output 'Desativando Cortana...'
Get-AppxPackage -allusers Microsoft.Windows.Cortana | Remove-AppxPackage

Write-Output 'Desativando Copilot...'
# Adicione aqui o comando para desativar o Copilot, se necessário

Write-Output 'Desativando Windows Defender...'
Set-MpPreference -DisableRealtimeMonitoring $true