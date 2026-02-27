param (
    [string]$message = "Atualizacoes de interface e correcoes gerais"
)

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "         ATUALIZADOR AUTOMATICO DO GITHUB" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Verifica se o Git está instalado
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    # Tenta localizar o Git do GitHub Desktop
    $githubDesktopGit = Get-ChildItem -Path "$env:LOCALAPPDATA\GitHubDesktop\app-*" -Filter "git.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($githubDesktopGit) {
        $gitDir = Split-Path -Parent $githubDesktopGit.FullName
        $env:PATH = "$gitDir;" + $env:PATH
        Write-Host "[OK] Motor do Git localizado com sucesso via GitHub Desktop." -ForegroundColor Green
    }
    else {
        Write-Error "O Git nao foi encontrado no sistema. Instale o Git for Windows."
        Read-Host "Pressione ENTER para sair"
        exit
    }
}

$inputMsg = Read-Host "`nDigite a mensagem de commit (ou pressione ENTER para '$message')"
if (![string]::IsNullOrWhiteSpace($inputMsg)) {
    $message = $inputMsg
}

Write-Host "`n>> Adicionando arquivos alterados..." -ForegroundColor Yellow
git add .

Write-Host ">> Realizando commit: '$message'..." -ForegroundColor Yellow
git commit -m $message

Write-Host ">> Enviando para o GitHub..." -ForegroundColor Yellow
git push

Write-Host "`n=======================================================" -ForegroundColor Green
Write-Host "     Atualizacao enviada com sucesso!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Read-Host "Pressione ENTER para fechar"
