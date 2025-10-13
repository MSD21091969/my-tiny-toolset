# Toolset Self-Setup & Maintenance Script
# Ensures toolset is always ready for conceptual laboratory work

param(
    [switch]$ForceUpdate,
    [switch]$QuickCheck
)

$ToolsetPath = "C:\Users\HP\my-tiny-toolset"
$OutputPath = "C:\Users\HP\Desktop\krabbel\tool-outputs"

Write-Host "🔬 Conceptual Laboratory Setup" -ForegroundColor Cyan

# Phase 1: Health Check
Write-Host "`n📊 Checking toolset health..." -ForegroundColor Yellow

if (!(Test-Path "$ToolsetPath\TOOLSET")) {
    Write-Host "❌ Toolset not found - cloning..." -ForegroundColor Red
    git clone https://github.com/MSD21091969/my-tiny-toolset.git $ToolsetPath
}

Set-Location $ToolsetPath

# Check PATH tools
$toolsWorking = $true
try {
    $null = code_analyzer --help 2>$null
    Write-Host "✓ Code analyzer available" -ForegroundColor Green
} catch {
    Write-Host "❌ Tools not in PATH - regenerating batch files..." -ForegroundColor Red
    $toolsWorking = $false
}

# Phase 2: Auto-generate batch files if needed
if (!$toolsWorking -or $ForceUpdate) {
    Write-Host "`n🔧 Regenerating tool wrappers..." -ForegroundColor Yellow
    
    $tools = @("code_analyzer", "mapping_analyzer", "excel_exporter", "version_tracker")
    foreach ($tool in $tools) {
        $batContent = "@echo off`npython `"%~dp0$tool.py`" %*"
        $batPath = "$ToolsetPath\TOOLSET\$tool.bat"
        $batContent | Out-File -FilePath $batPath -Encoding ASCII -Force
        Write-Host "✓ Generated $tool.bat" -ForegroundColor Green
    }
}

# Phase 3: Submodule health check
if (!$QuickCheck) {
    Write-Host "`n📚 Checking conceptual resources..." -ForegroundColor Yellow
    
    $brokenSubmodules = git submodule status | Select-String "^-"
    if ($brokenSubmodules) {
        Write-Host "🔄 Initializing conceptual resource collections..." -ForegroundColor Yellow
        git submodule update --init --recursive
    } else {
        Write-Host "✓ Conceptual resources available" -ForegroundColor Green
    }
}

# Phase 4: Context preparation
Write-Host "`n📖 Preparing conceptual context..." -ForegroundColor Yellow

# Ensure output directories
@("docs", "analysis", "mappings", "excel") | ForEach-Object {
    $dir = "$OutputPath\$_"
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Sync contextual references
Copy-Item -Path "$ToolsetPath\*.md" -Destination "$OutputPath\docs\" -Force -ErrorAction SilentlyContinue
if (Test-Path "$ToolsetPath\FIELD_REFERENCES.md") {
    Copy-Item -Path "$ToolsetPath\FIELD_REFERENCES.md" -Destination "$OutputPath\docs\conceptual-context.md" -Force
    Write-Host "✓ Conceptual context ready for AI collaboration" -ForegroundColor Green
}

Write-Host "`n🚀 Conceptual Laboratory Ready!" -ForegroundColor Green
Write-Host "Available for AI-assisted exploration:" -ForegroundColor Cyan
Write-Host "  • Code analysis and pattern discovery" 
Write-Host "  • Schema mapping and transformation design"
Write-Host "  • Conceptual modeling with rich context"
Write-Host "  • Documentation-driven development"
Write-Host "`nContext files: $OutputPath\docs" -ForegroundColor Gray