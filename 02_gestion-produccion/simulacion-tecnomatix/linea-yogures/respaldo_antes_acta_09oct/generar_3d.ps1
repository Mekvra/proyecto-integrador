# Regenera el modelo de la línea de yogures con su escena 3D decorada.
# 1) construye y simula el modelo 2D, 2) lo abre en Plant Simulation visible, 3) crea la escena 3D (Open 2D/3D),
# 4) aplica la decoración (decorar_3d.py) y oculta las conexiones, 5) simula 30 h (arranque en caliente) y guarda
# linea_yogures_actual_3d.spp con tiempo real ×30 para que al dar Play se vea la línea trabajando.
# Requiere las herramientas de .claude/historial/archivos-de-trabajo/tecnomatix-automatizacion copiadas en $tx.
param([string]$tx = "$env:TEMP\tx3d", [int]$semanas = 12, [switch]$abierto, [int[]]$conservar = @())
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'live.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Get-Process PlantSim* -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -notmatch "_3d.spp" -and $_.Id -notin $conservar } | Stop-Process -Force   # no cierra un 3D que el usuario tenga abierto
python construir_yogures.py linea_yogures_actual.spp $semanas | Select-Object -Last 1
python decorar_3d.py "$env:TEMP\deco3d"
if ($LASTEXITCODE) { "la decoración falló; no se aplica nada"; exit 1 }
Remove-Item "$tx\out.txt", "$tx\cmd.txt" -ErrorAction SilentlyContinue
Start-Process python -ArgumentList "`"$tx\live.py`" `"$here\linea_yogures_actual.spp`"" -WindowStyle Hidden
$t0 = Get-Date
while (((Get-Date) - $t0).TotalSeconds -lt 150) { if ((Test-Path "$tx\out.txt") -and ((Get-Content "$tx\out.txt" -Raw) -match 'loaded')) { break }; Start-Sleep 2 }
Start-Sleep 4
& "$tx\uia2.ps1" -title "linea_yogures_actual.spp" -action typeat -name "950,61,2D/3D" -out "m.png" | Out-Null
Start-Sleep 2
& "$tx\yes3d.ps1" -title "linea_yogures_actual.spp"
Start-Sleep 25
$files = Get-ChildItem "$env:TEMP\deco3d\deco_*.txt" | Sort-Object Name | ForEach-Object FullName
& "$tx\sendq.ps1" -files $files -timeout 180
# pestaña View del 3D: ocultar las líneas de conexión (las sombras ya quedan activas como preferencia de Plant Simulation)
foreach ($p in "594,54,", "841,120,") { & "$tx\uia2.ps1" -title "linea_yogures_actual.spp" -action typeat -name $p -out "m.png" | Out-Null }
# arranque en caliente: se simulan 30 h sin animación para que al dar Play ya haya producto en bandas, robot y montacargas
Set-Content "$tx\warm.txt" "simtalk`n.Models.Model.EventController.End := 108000`n.Models.Model.EventController.startWithoutAnimation" -Encoding utf8
& "$tx\sendq.ps1" -files "$tx\warm.txt" -timeout 60 | Out-Null
Set-Content "$tx\simt.txt" "get`n.Models.Model.EventController.SimTime" -Encoding utf8
for ($i = 0; $i -lt 120; $i++) { Start-Sleep 2; & "$tx\sendq.ps1" -files "$tx\simt.txt" -timeout 10 | Out-Null; if ((Get-Content "$tx\out.txt" -Raw) -match '108000') { break } }
Set-Content "$tx\warm2.txt" "simtalk`n.Models.Model.EventController.End := 6220800`n.Models.Model.EventController.Speed := 100`n.Models.Model.EventController.RealTime := true`n.Models.Model.EventController.RealTimeScale := 30" -Encoding utf8
& "$tx\sendq.ps1" -files "$tx\warm2.txt" -timeout 30
Set-Content "$tx\save.txt" "save`n$here\linea_yogures_actual_3d.spp" -Encoding utf8
& "$tx\sendq.ps1" -files "$tx\save.txt" -timeout 120
if ($abierto) { "sesión abierta"; exit }
Set-Content "$tx\out.txt" "-"; Set-Content "$tx\cmd.tmp" "quit`n"; Move-Item "$tx\cmd.tmp" "$tx\cmd.txt" -Force
Start-Sleep 6
Get-Process PlantSim* -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -notmatch "_3d.spp" -and $_.Id -notin $conservar } | Stop-Process -Force   # no cierra un 3D que el usuario tenga abierto
Get-Item "$here\linea_yogures_actual_3d.spp" | Select-Object Name, Length, LastWriteTime
