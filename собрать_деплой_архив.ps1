# Скрипт сборки ZIP-архива для деплоя на Bothost
# Запуск: в папке проекта выполнить .\собрать_деплой_архив.ps1

$ErrorActionPreference = "Stop"
$projectDir = $PSScriptRoot
$archiveName = "Tg_BOT_Assist_deploy_$(Get-Date -Format 'yyyy-MM-dd_HH-mm').zip"
$archivePath = Join-Path $projectDir $archiveName

# Файлы и папки для включения в архив
$include = @(
    "bot.py",
    "config.py",
    "requirements.txt",
    "Dockerfile",
    ".dockerignore",
    "handlers",
    "keyboards",
    "texts",
    "database"
)

Write-Host "Сборка архива для деплоя..." -ForegroundColor Cyan
Write-Host "Папка: $projectDir" -ForegroundColor Gray
Write-Host ""

# Временно переходим в папку проекта
Push-Location $projectDir

try {
    # Удаляем старый архив с таким же именем, если есть
    if (Test-Path $archivePath) { Remove-Item $archivePath -Force }

    # Создаём временную папку для сборки
    $tempDir = Join-Path $env:TEMP "bot_deploy_$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

    foreach ($item in $include) {
        $src = Join-Path $projectDir $item
        $dst = Join-Path $tempDir $item
        if (Test-Path $src) {
            if (Test-Path $src -PathType Container) {
                Copy-Item -Path $src -Destination $dst -Recurse -Force
                # Удаляем __pycache__ из скопированных папок
                Get-ChildItem -Path $dst -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                Get-ChildItem -Path $dst -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
                Get-ChildItem -Path $dst -Recurse -Filter "*.db" | Remove-Item -Force -ErrorAction SilentlyContinue
            } else {
                Copy-Item -Path $src -Destination $dst -Force
            }
            Write-Host "  + $item" -ForegroundColor Green
        } else {
            Write-Host "  ! Пропуск (не найден): $item" -ForegroundColor Yellow
        }
    }

    # Создаём ZIP
    Compress-Archive -Path "$tempDir\*" -DestinationPath $archivePath -Force
    Remove-Item -Path $tempDir -Recurse -Force

    Write-Host ""
    Write-Host "Готово!" -ForegroundColor Green
    Write-Host "Архив: $archivePath" -ForegroundColor White
    Write-Host ""
    Write-Host "Дальше:" -ForegroundColor Cyan
    Write-Host "  1. Зарегистрируйся на https://bothost.ru" -ForegroundColor Gray
    Write-Host "  2. Создай проект (Docker/Python), загрузи этот ZIP" -ForegroundColor Gray
    Write-Host "  3. В настройках проекта добавь переменные: BOT_TOKEN, ADMIN_ID, DEBUG=False" -ForegroundColor Gray
    Write-Host "  4. Нажми Деплой" -ForegroundColor Gray
}
finally {
    Pop-Location
}
