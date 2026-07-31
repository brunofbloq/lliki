param(
    [string]$Source = ".",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.9 or newer first."
}

try {
    py -m pipx --version | Out-Null
} catch {
    py -m pip install --user pipx
    py -m pipx ensurepath
}

$arguments = @("-m", "pipx", "install")
if ($Force) { $arguments += "--force" }
$arguments += $Source
& py @arguments

Write-Host "Installed. Restart PowerShell if 'lliki' is not yet on PATH."
