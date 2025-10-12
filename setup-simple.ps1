param(
    [switch]$QuickCheck
)

$ToolsetPath = "C:\Users\HP\my-tiny-toolset"
$OutputPath = "C:\Users\HP\Desktop\krabbel\tool-outputs"

Write-Host "Conceptual Laboratory Setup" -ForegroundColor Cyan

# Check PATH tools
$toolsWorking = $true
try {
    code_analyzer --help | Out-Null
    Write-Host "Code analyzer available" -ForegroundColor Green
} catch {
    Write-Host "Tools not in PATH - regenerating batch files..." -ForegroundColor Red
    $toolsWorking = $false
}

# Auto-generate batch files if needed
if (-not $toolsWorking) {
    Write-Host "Regenerating tool wrappers..." -ForegroundColor Yellow
    
    $tools = @("code_analyzer", "mapping_analyzer", "excel_exporter", "version_tracker")
    foreach ($tool in $tools) {
        $batContent = "@echo off`npython `"%~dp0$tool.py`" %*"
        $batPath = "$ToolsetPath\TOOLSET\$tool.bat"
        Set-Content -Path $batPath -Value $batContent -Force
        Write-Host "Generated $tool.bat" -ForegroundColor Green
    }
}

# Ensure output directories with proper separation
@("docs", "analysis", "mappings", "excel") | ForEach-Object {
    $dir = "$OutputPath\$_"
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Create dedicated AI context subdirectory
$aiContextDir = "$OutputPath\docs\ai-context"
if (!(Test-Path $aiContextDir)) {
    New-Item -ItemType Directory -Path $aiContextDir -Force | Out-Null
}

# Sync contextual references to dedicated AI location
Copy-Item -Path "$ToolsetPath\FIELD_REFERENCES.md" -Destination "$aiContextDir\conceptual-patterns.md" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$ToolsetPath\README.md" -Destination "$aiContextDir\toolset-overview.md" -Force -ErrorAction SilentlyContinue

# Create AI context index
$aiIndex = @"
# 🤖 AI Collaboration Context

## Human-Relevant Context Hints

### 📚 **Conceptual Patterns** → `conceptual-patterns.md`
- Domain patterns when concrete data is absent
- Architecture guidance and design patterns  
- Technology stack references and examples
- Business → Technical translation patterns

### 🛠️ **Toolset Overview** → `toolset-overview.md`  
- Available analysis capabilities
- Tool usage patterns and workflows
- Integration points and automation

### 💡 **Usage for AI**
When human asks for guidance and concrete data is missing:
1. Reference conceptual-patterns.md for domain context
2. Use toolset-overview.md for capability awareness
3. Suggest specific tool runs for concrete insights
4. Provide pattern-based architectural guidance

---
*This is the AI go-to place for human-relevant context hints*
"@

Set-Content -Path "$aiContextDir\README.md" -Value $aiIndex -Force

Write-Host "Conceptual Laboratory Ready!" -ForegroundColor Green
Write-Host "Available for AI-assisted exploration:" -ForegroundColor Cyan
Write-Host "- Code analysis and pattern discovery" 
Write-Host "- Schema mapping and transformation design"
Write-Host "- Conceptual modeling with rich context"
Write-Host "- Documentation-driven development"