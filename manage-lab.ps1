# Conceptual Laboratory Manager
# On-demand resource loading for AI-assisted development

param(
    [string]$Context = "all",
    [switch]$Cleanup,
    [switch]$Status
)

$ToolsetPath = "C:\Users\HP\my-tiny-toolset"
$OutputPath = "C:\Users\HP\Desktop\krabbel\tool-outputs"

# Lightweight resource definitions
$ConceptualCollections = @{
    "schemas" = @{
        path = "SCHEMAS/schemastore"
        desc = "JSON Schema patterns & validation"
        size = "Large"
        ondemand = $true
    }
    "prompts" = @{
        path = "PROMPTS/awesome-prompts"
        desc = "AI prompt engineering collection"
        size = "Medium" 
        ondemand = $false
    }
    "templates" = @{
        path = "TEMPLATES/cookiecutter"
        desc = "Project scaffolding templates"
        size = "Large"
        ondemand = $true
    }
    "examples" = @{
        path = "EXAMPLES/pydantic-examples"
        desc = "Pydantic model patterns"
        size = "Large"
        ondemand = $true
    }
    "configs" = @{
        path = "CONFIGS/fastapi-configs"
        desc = "FastAPI configuration patterns"
        size = "Large"
        ondemand = $false
    }
}

function Show-LabStatus {
    Write-Host "🔬 Conceptual Laboratory Status" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    # Core tools
    Write-Host "`n🛠️  Core Analysis Tools:" -ForegroundColor Yellow
    $tools = @("code_analyzer", "mapping_analyzer", "excel_exporter", "version_tracker")
    foreach ($tool in $tools) {
        try {
            $null = & $tool --help 2>$null
            Write-Host "  ✓ $tool" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $tool" -ForegroundColor Red
        }
    }
    
    # Conceptual resources
    Write-Host "`n📚 Conceptual Resources:" -ForegroundColor Yellow
    cd $ToolsetPath
    foreach ($key in $ConceptualCollections.Keys) {
        $collection = $ConceptualCollections[$key]
        $path = $collection.path
        $status = git submodule status $path 2>$null
        
        if ($status -match "^\s*[a-f0-9]") {
            Write-Host "  ✓ $key - $($collection.desc)" -ForegroundColor Green
        } elseif ($status -match "^-") {
            Write-Host "  ⏳ $key - Available on-demand" -ForegroundColor Yellow
        } else {
            Write-Host "  ❌ $key - Not configured" -ForegroundColor Red
        }
    }
    
    # Context files
    Write-Host "`n📖 AI Context Files:" -ForegroundColor Yellow
    $contextFiles = @("FIELD_REFERENCES.md", "README.md")
    foreach ($file in $contextFiles) {
        if (Test-Path "$OutputPath\docs\$file") {
            Write-Host "  ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file" -ForegroundColor Red
        }
    }
}

function Load-ConceptualContext {
    param([string]$ContextType)
    
    Write-Host "🔄 Loading conceptual context: $ContextType" -ForegroundColor Yellow
    
    if ($ContextType -eq "all" -or $ContextType -eq "prompts") {
        # Always load prompt collections for AI work
        cd $ToolsetPath
        git submodule update --init PROMPTS/awesome-prompts PROMPTS/edu-prompts
    }
    
    if ($ContextType -eq "all" -or $ContextType -eq "configs") {
        # Load configuration patterns
        git submodule update --init CONFIGS/fastapi-configs CONFIGS/gitignore-templates
    }
    
    # On-demand loading for large collections
    if ($ContextType -ne "all") {
        $collection = $ConceptualCollections[$ContextType]
        if ($collection) {
            Write-Host "Loading $($collection.desc)..." -ForegroundColor Cyan
            git submodule update --init $collection.path
        }
    }
}

function Cleanup-Resources {
    Write-Host "🧹 Cleaning up large resources..." -ForegroundColor Yellow
    
    # Keep only essential collections, remove large ones
    $keep = @("CONFIGS/fastapi-configs", "PROMPTS/awesome-prompts", "PROMPTS/edu-prompts")
    
    cd $ToolsetPath
    $submodules = git submodule status | ForEach-Object { ($_ -split '\s+')[2] }
    
    foreach ($submodule in $submodules) {
        if ($submodule -notin $keep) {
            Write-Host "Removing $submodule..." -ForegroundColor Gray
            git submodule deinit -f $submodule
            Remove-Item -Recurse -Force $submodule -ErrorAction SilentlyContinue
        }
    }
}

# Main execution
switch ($true) {
    $Status { Show-LabStatus }
    $Cleanup { Cleanup-Resources }
    default { 
        Load-ConceptualContext -ContextType $Context
        Show-LabStatus
    }
}