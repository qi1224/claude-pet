# Windows PowerShell 5.1 and PowerShell 7.
param([ValidateSet('claude', 'codex', 'all')][string]$Provider = 'claude', [string]$ConfigDir)
$ErrorActionPreference = 'Stop'
$PetArguments = @((Join-Path $PSScriptRoot 'install.py'), '--provider', $Provider)
if ($ConfigDir) { $PetArguments += @('--config-dir', $ConfigDir) }
if (Get-Command py.exe -ErrorAction SilentlyContinue) {
    & py.exe -3 @PetArguments
} elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
    & python.exe @PetArguments
} else {
    throw 'Python 3.8+ is required. Install Python and add it to PATH.'
}
exit $LASTEXITCODE
