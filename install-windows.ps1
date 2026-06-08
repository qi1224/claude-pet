# Install claude-pet for Windows (PowerShell)
# Usage: .\install-windows.ps1

$ErrorActionPreference = "Stop"

$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { "$env:USERPROFILE\.claude" }
$PetDir    = "$ClaudeDir\pet"
$CmdDir    = "$ClaudeDir\commands"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==> Installing claude-pet to $PetDir"
New-Item -ItemType Directory -Force $PetDir | Out-Null
New-Item -ItemType Directory -Force $CmdDir | Out-Null

Copy-Item "$ScriptDir\worm.py"   $PetDir -Force
Copy-Item "$ScriptDir\hook.py"   $PetDir -Force
Copy-Item "$ScriptDir\launch.sh" $PetDir -Force
Copy-Item "$ScriptDir\pet.md"    $CmdDir -Force

"idle" | Set-Content "$PetDir\state" -NoNewline

Write-Host "==> Detecting Python installation"
$PyExe = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $PyExe) {
    $PyExe = (Get-Command python.exe -ErrorAction SilentlyContinue)?.Source
}
if (-not $PyExe) {
    Write-Warning "Python not found. Please set the hook command paths manually in settings.json"
    $PyExe = "python"
}

$HookPath  = "$PetDir\hook.py" -replace "\\", "/"
$PyExeSlash = $PyExe -replace "\\", "/"

Write-Host "==> Updating hooks in settings.json (Python: $PyExe)"

$SettingsPath = "$ClaudeDir\settings.json"
$cfg = if (Test-Path $SettingsPath) {
    Get-Content $SettingsPath -Raw | ConvertFrom-Json -AsHashtable
} else {
    @{}
}

if (-not $cfg.ContainsKey("hooks")) { $cfg["hooks"] = @{} }

$events = @{
    "Stop"             = "stop"
    "PreToolUse"       = "pre"
    "PostToolUse"      = "post"
    "UserPromptSubmit" = "submit"
}

foreach ($evt in $events.Keys) {
    $cmd   = "$PyExeSlash $HookPath $($events[$evt])"
    $entry = @{ matcher = ""; hooks = @(@{ type = "command"; command = $cmd }) }
    $existing = @($cfg["hooks"][$evt] | Where-Object { $_ })
    $cleaned  = @($existing | Where-Object {
        -not ($_.hooks | Where-Object { $_.command -like "*hook.py*" })
    })
    $cfg["hooks"][$evt] = @($cleaned) + @($entry)
}

$cfg | ConvertTo-Json -Depth 10 | Set-Content $SettingsPath -Encoding UTF8
Write-Host "  hooks written to $SettingsPath"

Write-Host ""
Write-Host "Done! Start the worm with /pet in Claude Code."
Write-Host "Windows Terminal split-pane is used automatically."
