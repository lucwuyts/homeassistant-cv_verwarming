[CmdletBinding()]
param(
    [ValidateSet('Snapshot', 'Deploy')]
    [string]$Mode = 'Snapshot',
    [string]$HomeAssistantConfig = '\\homeassistant\config',
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$HomeAssistantConfig = [System.IO.Path]::GetFullPath($HomeAssistantConfig)
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))

if (-not (Test-Path -LiteralPath $HomeAssistantConfig -PathType Container)) {
    throw "Home Assistant-configuratiemap niet bereikbaar: $HomeAssistantConfig"
}
if ($Mode -eq 'Deploy' -and -not $Apply) {
    throw 'Deploy schrijft alleen het CV-package en de CV-macro naar Home Assistant. Herhaal met -Mode Deploy -Apply na controle.'
}

$files = @(
    @{ Repo = 'packages\cv_heating.yaml'; HA = 'packages\cv_heating.yaml' },
    @{ Repo = 'custom_templates\rt_tools.jinja'; HA = 'custom_templates\rt_tools.jinja' }
)

foreach ($file in $files) {
    $repoPath = Join-Path $repoRoot $file.Repo
    $haPath = Join-Path $HomeAssistantConfig $file.HA
    if ($Mode -eq 'Snapshot') {
        if (-not (Test-Path -LiteralPath $haPath -PathType Leaf)) {
            throw "CV-bestand ontbreekt in Home Assistant: $haPath"
        }
        $destination = $repoPath
        $source = $haPath
    } else {
        if (-not (Test-Path -LiteralPath $repoPath -PathType Leaf)) {
            throw "CV-bestand ontbreekt in de repository: $repoPath"
        }
        $destination = $haPath
        $source = $repoPath
    }

    $parent = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    if ($Mode -eq 'Deploy' -and (Test-Path -LiteralPath $destination -PathType Leaf)) {
        Copy-Item -LiteralPath $destination -Destination "$destination.pre-cv-deploy.bak" -Force
    }
    Copy-Item -LiteralPath $source -Destination $destination -Force
    Write-Host "$Mode  $($file.HA)"
}

Write-Host 'Alleen het CV-package en de CV-macro zijn gesynchroniseerd.'
if ($Mode -eq 'Deploy') {
    Write-Host 'Controleer de HA-configuratie en voer daarna een herlaadactie of herstart uit.'
}
