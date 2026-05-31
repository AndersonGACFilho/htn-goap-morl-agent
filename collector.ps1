$rootPath = if ($PSScriptRoot) {
    $PSScriptRoot
} else {
    (Get-Location).Path
}

$output = Join-Path $rootPath "project_context.txt"

if (Test-Path $output) { Remove-Item $output -Force }

$ignoreFolders = @(
    ".venv", "env", "__pycache__", ".git", ".idea",
    ".mypy_cache", ".pytest_cache", ".ruff_cache"
)

$allowedExtensions = @(".py", ".toml", ".json")
$allowedFileNames = @("poetry.toml", "pyproject.toml")

$files = Get-ChildItem -Path $rootPath -Recurse -File | Where-Object {
    $item = $_

    $inForbiddenFolder = $false
    foreach ($folder in $ignoreFolders) {
        if ($item.FullName -like "*\$folder\*") {
            $inForbiddenFolder = $true
            break
        }
    }

    $isAllowedExtension = $allowedExtensions -contains $item.Extension
    $isAllowedName = $allowedFileNames -contains $item.Name
    $isLockFile = $item.Name -match "^(package-lock\.json|yarn\.lock)$"
    $isSelf = $item.Name -eq "project_context.txt"

    -not $inForbiddenFolder `
        -and ($isAllowedExtension -or $isAllowedName) `
        -and -not $isLockFile `
        -and -not $isSelf
}

foreach ($file in $files) {
    "--- FILE: $($file.FullName) ---" | Out-File -FilePath $output -Append -Encoding UTF8

    try {
        Get-Content $file.FullName -Raw -ErrorAction Stop |
            Out-File -FilePath $output -Append -Encoding UTF8
    } catch {
        "[ERROR: Failed to read $($file.FullName)]" |
            Out-File -FilePath $output -Append -Encoding UTF8
    }

    "`n--- END OF FILE ---`n" |
        Out-File -FilePath $output -Append -Encoding UTF8
}

Write-Host "Success! File generated at: $output" -ForegroundColor Green
