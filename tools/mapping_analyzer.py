"""
Mapping Analyzer - Analyzes relationships between models and endpoints
Provides dependency graphs, impact analysis, and reuse metrics
"""

import json
from typing import Dict, List, Set, Any
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class DependencyInfo:
    """Model dependency information"""
    model_name: str
    depends_on: List[str]  # Models this model uses
    used_by: List[str]  # Models that use this model
    depth: int  # Nesting depth


@dataclass
class ImpactAnalysis:
    """Impact analysis for a model"""
    model_name: str
    affected_endpoints: List[str]  # Endpoints that will break
    affected_models: List[str]  # Models that depend on this
    risk_level: str  # low, medium, high
    usage_count: int  # How many places use this


@dataclass
class MappingStats:
    """Mapping statistics"""
    total_models: int
    total_endpoints: int
    models_with_endpoints: int  # Models used in endpoints
    orphaned_models: int  # Models not used anywhere
    endpoint_coverage: float  # % of endpoints with models
    avg_model_reuse: float  # Average endpoints per model
    most_reused_model: str
    most_reused_count: int


class MappingAnalyzer:
    """Analyze mappings between models and endpoints"""
    
    def __init__(self, version_tracker):
        self.tracker = version_tracker
        self.model_dependencies = {}
        self.model_impact = {}
        self.stats = None
        
        # Analyze
        self._analyze_dependencies()
        self._analyze_impact()
        self._calculate_stats()
    
    def _analyze_dependencies(self):
        """Analyze model dependencies (which models use which)"""
        for model_name, model in self.tracker.models.items():
            depends_on = []
            used_by = []
            
            # Check if fields reference other models
            for field in model.fields:
                field_type = field.type
                # Look for model names in field types
                for other_model in self.tracker.models.keys():
                    if other_model in field_type and other_model != model_name:
                        depends_on.append(other_model)
            
            # Find models that reference this model
            for other_name, other_model in self.tracker.models.items():
                if other_name == model_name:
                    continue
                for field in other_model.fields:
                    if model_name in field.type:
                        used_by.append(other_name)
            
            self.model_dependencies[model_name] = DependencyInfo(
                model_name=model_name,
                depends_on=list(set(depends_on)),
                used_by=list(set(used_by)),
                depth=self._calculate_depth(model_name, set())
            )
    
    def _calculate_depth(self, model_name: str, visited: Set[str]) -> int:
        """Calculate nesting depth of a model"""
        if model_name in visited:
            return 0  # Circular reference
        
        visited.add(model_name)
        model = self.tracker.models.get(model_name)
        if not model:
            return 0
        
        max_depth = 0
        for field in model.fields:
            for other_model in self.tracker.models.keys():
                if other_model in field.type:
                    depth = 1 + self._calculate_depth(other_model, visited.copy())
                    max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _analyze_impact(self):
        """Analyze impact of changing each model"""
        for model_name, model in self.tracker.models.items():
            affected_endpoints = model.used_in_endpoints.copy()
            affected_models = self.model_dependencies[model_name].used_by.copy()
            
            # Calculate risk level
            usage_count = len(affected_endpoints) + len(affected_models)
            if usage_count == 0:
                risk_level = "none"  # Orphaned
            elif usage_count <= 2:
                risk_level = "low"
            elif usage_count <= 5:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            self.model_impact[model_name] = ImpactAnalysis(
                model_name=model_name,
                affected_endpoints=affected_endpoints,
                affected_models=affected_models,
                risk_level=risk_level,
                usage_count=usage_count
            )
    
    def _calculate_stats(self):
        """Calculate mapping statistics"""
        total_models = len(self.tracker.models)
        total_endpoints = len(self.tracker.endpoints)
        
        # Models used in endpoints
        models_with_endpoints = sum(
            1 for m in self.tracker.models.values()
            if m.used_in_endpoints
        )
        
        # Orphaned models
        orphaned_models = total_models - models_with_endpoints
        
        # Endpoint coverage
        endpoints_with_models = sum(
            1 for ep in self.tracker.endpoints
            if ep.request_model or ep.response_model
        )
        endpoint_coverage = (endpoints_with_models / total_endpoints * 100) if total_endpoints > 0 else 0
        
        # Model reuse
        endpoint_counts = [len(m.used_in_endpoints) for m in self.tracker.models.values()]
        avg_model_reuse = sum(endpoint_counts) / len(endpoint_counts) if endpoint_counts else 0
        
        # Most reused model
        most_reused = max(
            self.tracker.models.values(),
            key=lambda m: len(m.used_in_endpoints),
            default=None
        )
        most_reused_model = most_reused.name if most_reused else "N/A"
        most_reused_count = len(most_reused.used_in_endpoints) if most_reused else 0
        
        self.stats = MappingStats(
            total_models=total_models,
            total_endpoints=total_endpoints,
            models_with_endpoints=models_with_endpoints,
            orphaned_models=orphaned_models,
            endpoint_coverage=endpoint_coverage,
            avg_model_reuse=avg_model_reuse,
            most_reused_model=most_reused_model,
            most_reused_count=most_reused_count
        )
    
    def export_analysis(self, output_file: str):
        """Export mapping analysis to JSON"""
        data = {
            "stats": asdict(self.stats),
            "dependencies": {
                name: asdict(dep)
                for name, dep in self.model_dependencies.items()
            },
            "impact_analysis": {
                name: asdict(impact)
                for name, impact in self.model_impact.items()
            },
            "reuse_matrix": self._generate_reuse_matrix(),
            "orphaned_models": self._get_orphaned_models(),
            "high_risk_models": self._get_high_risk_models()
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Mapping analysis exported to: {output_file}")
    
    def _generate_reuse_matrix(self) -> List[Dict[str, Any]]:
        """Generate model reuse matrix"""
        matrix = []
        for model_name, model in self.tracker.models.items():
            if model.used_in_endpoints:
                matrix.append({
                    "model": model_name,
                    "endpoints": model.used_in_endpoints,
                    "count": len(model.used_in_endpoints),
                    "file": model.file_path
                })
        
        # Sort by usage count descending
        matrix.sort(key=lambda x: x["count"], reverse=True)
        return matrix
    
    def _get_orphaned_models(self) -> List[Dict[str, str]]:
        """Get models not used in any endpoint"""
        orphaned = []
        for model_name, model in self.tracker.models.items():
            if not model.used_in_endpoints:
                orphaned.append({
                    "name": model_name,
                    "file": model.file_path,
                    "fields": len(model.fields)
                })
        return orphaned
    
    def _get_high_risk_models(self) -> List[Dict[str, Any]]:
        """Get models with high change impact"""
        high_risk = []
        for model_name, impact in self.model_impact.items():
            if impact.risk_level == "high":
                high_risk.append({
                    "name": model_name,
                    "affected_endpoints": impact.affected_endpoints,
                    "affected_models": impact.affected_models,
                    "usage_count": impact.usage_count
                })
        
        high_risk.sort(key=lambda x: x["usage_count"], reverse=True)
        return high_risk
    
    def export_html_report(self, output_file: str):
        """Export interactive HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapping Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4CAF50;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .risk-high {{ color: #f44336; font-weight: bold; }}
        .risk-medium {{ color: #ff9800; font-weight: bold; }}
        .risk-low {{ color: #4CAF50; font-weight: bold; }}
        .risk-none {{ color: #999; }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
        }}
        .badge-success {{ background: #4CAF50; color: white; }}
        .badge-warning {{ background: #ff9800; color: white; }}
        .badge-danger {{ background: #f44336; color: white; }}
        .badge-info {{ background: #2196F3; color: white; }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Mapping Analysis Report</h1>
        <p><strong>Generated:</strong> {self.tracker.git_info.timestamp or "N/A"}</p>
        <p><strong>Version:</strong> {self.tracker.project_version}</p>
        <p><strong>Git Commit:</strong> <code>{self.tracker.git_info.commit_hash[:8] if self.tracker.git_info.commit_hash else "N/A"}</code></p>
        
        <h2>📈 Overview Statistics</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{self.stats.total_models}</div>
                <div class="stat-label">Total Models</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats.total_endpoints}</div>
                <div class="stat-label">Total Endpoints</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats.models_with_endpoints}</div>
                <div class="stat-label">Models in Use</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats.orphaned_models}</div>
                <div class="stat-label">Orphaned Models</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats.endpoint_coverage:.1f}%</div>
                <div class="stat-label">Endpoint Coverage</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.stats.avg_model_reuse:.1f}</div>
                <div class="stat-label">Avg Model Reuse</div>
            </div>
        </div>
        
        <h2>🔥 Top Reused Models</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>File</th>
                <th>Usage Count</th>
                <th>Endpoints</th>
            </tr>
"""
        
        # Top reused models
        for item in self._generate_reuse_matrix()[:10]:
            endpoints_html = "<br>".join([f"<code>{ep}</code>" for ep in item["endpoints"][:5]])
            if len(item["endpoints"]) > 5:
                endpoints_html += f"<br><em>... and {len(item['endpoints']) - 5} more</em>"
            
            html += f"""            <tr>
                <td><strong>{item['model']}</strong></td>
                <td><code>{item['file']}</code></td>
                <td><span class="badge badge-success">{item['count']}</span></td>
                <td>{endpoints_html}</td>
            </tr>
"""
        
        html += """        </table>
        
        <h2>⚠️ High Risk Models (High Impact Changes)</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Risk Level</th>
                <th>Affected Endpoints</th>
                <th>Affected Models</th>
            </tr>
"""
        
        # High risk models
        for item in self._get_high_risk_models()[:10]:
            html += f"""            <tr>
                <td><strong>{item['name']}</strong></td>
                <td><span class="risk-high">HIGH</span></td>
                <td>{len(item['affected_endpoints'])}</td>
                <td>{len(item['affected_models'])}</td>
            </tr>
"""
        
        html += """        </table>
        
        <h2>🔍 Orphaned Models (Not Used in Any Endpoint)</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>File</th>
                <th>Fields</th>
            </tr>
"""
        
        # Orphaned models
        for item in self._get_orphaned_models()[:20]:
            html += f"""            <tr>
                <td><strong>{item['name']}</strong></td>
                <td><code>{item['file']}</code></td>
                <td>{item['fields']}</td>
            </tr>
"""
        
        html += """        </table>
    </div>
</body>
</html>
"""
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"✓ HTML report exported to: {output_file}")
