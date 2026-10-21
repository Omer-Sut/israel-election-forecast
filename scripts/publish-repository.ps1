# First-publication helper. Run from any directory using PowerShell with Git and gh installed.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$expectedRemote = 'https://github.com/Omer-Sut/israel-election-forecast.git'

function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Program failed (exit $LASTEXITCODE). Resolve the error before rerunning."
    }
}

Get-Command git -ErrorAction Stop | Out-Null
Push-Location -LiteralPath $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.git/HEAD')) {
        Invoke-Checked -Program 'git' -Arguments @('init', '-b', 'main')
    }
    $branch = & git symbolic-ref --short HEAD
    if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') {
        throw 'Expected branch main. Review the current branch before publication.'
    }

    $remotes = @(& git remote)
    if ($LASTEXITCODE -ne 0) { throw 'Could not read Git remotes.' }
    $hasOrigin = $remotes -contains 'origin'
    if ($hasOrigin) {
        $origin = & git remote get-url origin
        if ($LASTEXITCODE -ne 0 -or $origin -ne $expectedRemote) {
            throw "Review origin before continuing. Expected $expectedRemote"
        }
    } else {
        Get-Command gh -ErrorAction Stop | Out-Null
        Invoke-Checked -Program 'gh' -Arguments @('auth', 'status')
    }

    & git show-ref --quiet --verify refs/heads/main
    $hasCommit = $LASTEXITCODE -eq 0
    if (-not $hasCommit) {
        Invoke-Checked -Program 'git' -Arguments @('var', 'GIT_AUTHOR_IDENT')
        Invoke-Checked -Program 'git' -Arguments @('add', '--', 'README.md', 'AGENTS.md', 'CONTRIBUTING.md', '.gitignore', '.gitattributes', 'docs', 'scripts', '*.pdf')
        Invoke-Checked -Program 'git' -Arguments @('commit', '-m', 'Initialize election forecast project and competition context')
    } else {
        $changes = @(& git status --porcelain)
        if ($LASTEXITCODE -ne 0 -or $changes.Count -gt 0) {
            throw 'Existing repository has uncommitted work. Review and commit it explicitly before publishing.'
        }
    }

    if (-not $hasOrigin) {
        Invoke-Checked -Program 'gh' -Arguments @('repo', 'create', 'Omer-Sut/israel-election-forecast', '--public', '--source=.', '--remote=origin', '--description', 'Reproducible Israeli Knesset election forecasting project')
    }
    Invoke-Checked -Program 'git' -Arguments @('push', '-u', 'origin', 'main')
    Invoke-Checked -Program 'git' -Arguments @('remote', '-v')
    Invoke-Checked -Program 'git' -Arguments @('status', '--short', '--branch')
    Write-Host 'Publication succeeded. Update README.md and docs/project-state.md with the verified remote status, then commit and push those updates.'
} finally {
    Pop-Location
}
