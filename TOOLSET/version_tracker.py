"""
Version Tracker - Complete system for tracking FastAPI models and API versions
Integrates with Git for versioning and provides YAML output for CI/CD pipelines
"""

import ast
import os
import json
import yaml
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict


@dataclass
class FieldInfo:
    """Field information with versioning"""
    name: str
    type: str
    default: Optional[str] = None
    required: bool = True
    description: Optional[str] = None


@dataclass
class ModelVersion:
    """Complete model information with version tracking"""
    name: str
    version: str
    file_path: str
    line_number: int
    module: str
    base_classes: List[str]
    fields: List[FieldInfo]
    docstring: Optional[str]
    is_pydantic: bool
    is_dataclass: bool
    hash: str  # Hash of model structure for change detection
    git_commit: Optional[str] = None
    git_author: Optional[str] = None
    last_modified: Optional[str] = None
    used_in_endpoints: List[str] = field(default_factory=list)


@dataclass
class EndpointVersion:
    """API endpoint with version tracking"""
    path: str
    method: str
    function_name: str
    file_path: str
    line_number: int
    request_model: Optional[str] = None
    response_model: Optional[str] = None
    status_codes: List[int] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None
    deprecated: bool = False
    version: str = "1.0.0"


@dataclass
class GitInfo:
    """Git repository information"""
    commit_hash: Optional[str] = None
    branch: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[str] = None
    is_dirty: bool = False
    remote_url: Optional[str] = None


@dataclass
class AnalysisResult:
    """Complete analysis result with versioning"""
    timestamp: str
    project_root: str
    git_info: GitInfo
    models: List[ModelVersion]
    endpoints: List[EndpointVersion]
    files_analyzed: List[str]
    summary: Dict[str, Any]


class VersionTracker:
    """Track versions of models and API endpoints"""
    
    def __init__(self, root_path: str, version: str = "1.0.0"):
        self.root_path = Path(root_path).resolve()
        self.project_version = version
        self.models: Dict[str, ModelVersion] = {}
        self.endpoints: List[EndpointVersion] = []
        self.files_analyzed: List[str] = []
        self.git_info = self._get_git_info()
        
    def _get_git_info(self) -> GitInfo:
        """Extract Git repository information"""
        try:
            # Check if in git repo
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.root_path,
                capture_output=True,
                check=True
            )
            
            # Get commit hash
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get author
            author = subprocess.run(
                ["git", "log", "-1", "--format=%an <%ae>"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get timestamp
            timestamp = subprocess.run(
                ["git", "log", "-1", "--format=%aI"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Check if dirty
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            is_dirty = bool(status)
            
            # Get remote URL
            remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.root_path,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            return GitInfo(
                commit_hash=commit,
                branch=branch,
                author=author,
                timestamp=timestamp,
                is_dirty=is_dirty,
                remote_url=remote
            )
        except Exception as e:
            print(f"Warning: Could not get Git info: {e}")
            return GitInfo()
    
    def _get_file_git_info(self, file_path: Path) -> tuple:
        """Get last modified info for specific file"""
        try:
            # Get last commit that modified this file
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%aI|%an", "--", str(file_path)],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                commit, timestamp, author = result.stdout.strip().split("|")
                return commit, timestamp, author
        except Exception:
            pass
        return None, None, None
    
    def analyze_directory(self, exclude_patterns: List[str] = None):
        """Analyze all Python files in directory"""
        if exclude_patterns is None:
            exclude_patterns = ["venv", ".venv", "__pycache__", "node_modules", ".git", "analysis_output"]
        
        python_files = []
        for py_file in self.root_path.rglob("*.py"):
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)
        
        for py_file in python_files:
            self._analyze_file(py_file)
            self.files_analyzed.append(str(py_file.relative_to(self.root_path)))
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            # Get git info for this file
            commit, timestamp, author = self._get_file_git_info(file_path)
            
            # Extract models and endpoints
            self._extract_models(tree, file_path, commit, timestamp, author)
            self._extract_endpoints(tree, file_path)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _extract_models(self, tree: ast.AST, file_path: Path, commit: str, timestamp: str, author: str):
        """Extract model definitions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                model = self._parse_model(node, file_path, commit, timestamp, author)
                if model:
                    self.models[model.name] = model
    
    def _parse_model(self, node: ast.ClassDef, file_path: Path, 
                     commit: str, timestamp: str, author: str) -> Optional[ModelVersion]:
        """Parse a class into ModelVersion"""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_attr_name(base))
        
        # Check if it's a model we care about
        is_pydantic = any("BaseModel" in base for base in base_classes)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        is_dataclass = "dataclass" in decorators
        
        if not (is_pydantic or is_dataclass):
            return None
        
        # Extract fields
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                field_type = self._get_annotation_str(item.annotation)
                default_value = self._get_default_value(item.value) if item.value else None
                
                # Determine if required (no default means required)
                required = default_value is None
                
                # Try to extract description from inline comment or docstring
                description = None
                
                field_info = FieldInfo(
                    name=field_name,
                    type=field_type,
                    default=default_value,
                    required=required,
                    description=description
                )
                fields.append(field_info)
        
        # Calculate hash of model structure
        model_structure = {
            "name": node.name,
            "bases": sorted(base_classes),
            "fields": sorted([f.name + ":" + f.type for f in fields])
        }
        model_hash = hashlib.md5(json.dumps(model_structure, sort_keys=True).encode()).hexdigest()[:8]
        
        # Get module path
        module = str(file_path.relative_to(self.root_path)).replace("\\", ".").replace("/", ".").replace(".py", "")
        
        # Determine version (could be enhanced with more sophisticated logic)
        version = self.project_version
        
        return ModelVersion(
            name=node.name,
            version=version,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            module=module,
            base_classes=base_classes,
            fields=fields,
            docstring=ast.get_docstring(node),
            is_pydantic=is_pydantic,
            is_dataclass=is_dataclass,
            hash=model_hash,
            git_commit=commit,
            git_author=author,
            last_modified=timestamp
        )
    
    def _extract_endpoints(self, tree: ast.AST, file_path: Path):
        """Extract FastAPI endpoint definitions"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                endpoint = self._parse_endpoint(node, file_path)
                if endpoint:
                    self.endpoints.append(endpoint)
                    
                    # Link models to endpoints
                    if endpoint.request_model and endpoint.request_model in self.models:
                        self.models[endpoint.request_model].used_in_endpoints.append(
                            f"{endpoint.method} {endpoint.path}"
                        )
                    if endpoint.response_model and endpoint.response_model in self.models:
                        self.models[endpoint.response_model].used_in_endpoints.append(
                            f"{endpoint.method} {endpoint.path}"
                        )
    
    def _parse_endpoint(self, node: ast.FunctionDef, file_path: Path) -> Optional[EndpointVersion]:
        """Parse a function into EndpointVersion"""
        # Check for FastAPI decorators
        http_method = None
        endpoint_path = None
        tags = []
        deprecated = False
        
        for decorator in node.decorator_list:
            dec_name = self._get_decorator_name(decorator)
            
            # Check for HTTP method decorators
            if dec_name in ["get", "post", "put", "patch", "delete", "options", "head"]:
                http_method = dec_name.upper()
                
                # Extract path from decorator
                if isinstance(decorator, ast.Call) and decorator.args:
                    if isinstance(decorator.args[0], ast.Constant):
                        endpoint_path = decorator.args[0].value
                
                # Extract additional info from decorator kwargs
                if isinstance(decorator, ast.Call):
                    for keyword in decorator.keywords:
                        if keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                            tags = [e.value for e in keyword.value.elts if isinstance(e, ast.Constant)]
                        elif keyword.arg == "deprecated" and isinstance(keyword.value, ast.Constant):
                            deprecated = keyword.value.value
        
        if not http_method:
            return None
        
        # Extract request and response models from type hints
        request_model = None
        response_model = None
        
        for arg in node.args.args:
            if arg.annotation:
                type_str = self._get_annotation_str(arg.annotation)
                # Check if it's a model name we recognize
                for model_name in self.models.keys():
                    if model_name in type_str:
                        request_model = model_name
                        break
        
        if node.returns:
            type_str = self._get_annotation_str(node.returns)
            for model_name in self.models.keys():
                if model_name in type_str:
                    response_model = model_name
                    break
        
        # Get docstring for summary/description
        docstring = ast.get_docstring(node)
        summary = None
        description = None
        if docstring:
            lines = docstring.split("\n", 1)
            summary = lines[0].strip()
            description = lines[1].strip() if len(lines) > 1 else None
        
        return EndpointVersion(
            path=endpoint_path or f"/{node.name}",
            method=http_method,
            function_name=node.name,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            request_model=request_model,
            response_model=response_model,
            tags=tags,
            summary=summary,
            description=description,
            deprecated=deprecated,
            version=self.project_version
        )
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_attr_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return self._get_attr_name(decorator)
        return ""
    
    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get full attribute name"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    
    def _get_annotation_str(self, annotation: ast.expr) -> str:
        """Convert annotation to string"""
        if annotation is None:
            return ""
        try:
            return ast.unparse(annotation)
        except:
            return str(annotation)
    
    def _get_default_value(self, value: ast.expr) -> str:
        """Get default value as string"""
        if value is None:
            return None
        try:
            return ast.unparse(value)
        except:
            return str(value)
    
    def compare_with_previous(self, previous_file: str) -> Dict[str, Any]:
        """Compare current analysis with previous version"""
        try:
            with open(previous_file, "r", encoding="utf-8") as f:
                previous_data = json.load(f)
            
            previous_models = {m["name"]: m for m in previous_data.get("models", [])}
            current_models = {name: asdict(model) for name, model in self.models.items()}
            
            changes = {
                "models_added": [],
                "models_removed": [],
                "models_modified": [],
                "fields_added": {},
                "fields_removed": {},
                "fields_modified": {},
                "breaking_changes": []
            }
            
            # Find added models
            for name in current_models:
                if name not in previous_models:
                    changes["models_added"].append(name)
            
            # Find removed models
            for name in previous_models:
                if name not in current_models:
                    changes["models_removed"].append(name)
                    changes["breaking_changes"].append({
                        "type": "model_removed",
                        "model": name,
                        "severity": "high"
                    })
            
            # Find modified models
            for name in current_models:
                if name in previous_models:
                    current = current_models[name]
                    previous = previous_models[name]
                    
                    if current["hash"] != previous.get("hash"):
                        changes["models_modified"].append(name)
                        
                        # Detailed field comparison
                        current_fields = {f["name"]: f for f in current["fields"]}
                        previous_fields = {f["name"]: f for f in previous.get("fields", [])}
                        
                        # Fields added
                        for field_name in current_fields:
                            if field_name not in previous_fields:
                                changes["fields_added"].setdefault(name, []).append(field_name)
                                
                                # Breaking change if required field added
                                if current_fields[field_name]["required"]:
                                    changes["breaking_changes"].append({
                                        "type": "required_field_added",
                                        "model": name,
                                        "field": field_name,
                                        "severity": "high"
                                    })
                        
                        # Fields removed
                        for field_name in previous_fields:
                            if field_name not in current_fields:
                                changes["fields_removed"].setdefault(name, []).append(field_name)
                                changes["breaking_changes"].append({
                                    "type": "field_removed",
                                    "model": name,
                                    "field": field_name,
                                    "severity": "high"
                                })
                        
                        # Fields modified (type changed)
                        for field_name in current_fields:
                            if field_name in previous_fields:
                                if current_fields[field_name]["type"] != previous_fields[field_name]["type"]:
                                    changes["fields_modified"].setdefault(name, []).append(field_name)
                                    changes["breaking_changes"].append({
                                        "type": "field_type_changed",
                                        "model": name,
                                        "field": field_name,
                                        "old_type": previous_fields[field_name]["type"],
                                        "new_type": current_fields[field_name]["type"],
                                        "severity": "high"
                                    })
            
            return changes
        except Exception as e:
            print(f"Error comparing with previous version: {e}")
            return {}
    
    def export_to_json(self, output_file: str = ".tool-outputs/analysis/version_analysis.json"):
        """Export complete analysis to JSON"""
        result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            project_root=str(self.root_path),
            git_info=self.git_info,
            models=list(self.models.values()),
            endpoints=self.endpoints,
            files_analyzed=self.files_analyzed,
            summary={
                "total_models": len(self.models),
                "total_endpoints": len(self.endpoints),
                "pydantic_models": sum(1 for m in self.models.values() if m.is_pydantic),
                "dataclasses": sum(1 for m in self.models.values() if m.is_dataclass),
                "files_analyzed": len(self.files_analyzed),
                "project_version": self.project_version
            }
        )
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        print(f"✓ Exported version analysis to: {output_file}")
        return output_file
    
    def export_to_yaml(self, output_file: str = ".tool-outputs/analysis/api_versions.yaml"):
        """Export to YAML for CI/CD integration"""
        data = {
            "version": self.project_version,
            "git": {
                "commit": self.git_info.commit_hash,
                "branch": self.git_info.branch,
                "author": self.git_info.author,
                "timestamp": self.git_info.timestamp,
                "dirty": self.git_info.is_dirty
            },
            "models": [],
            "endpoints": []
        }
        
        # Group models by file
        models_by_file = defaultdict(list)
        for model in self.models.values():
            models_by_file[model.file_path].append(model)
        
        # Export models
        for file_path, models in sorted(models_by_file.items()):
            for model in models:
                model_data = {
                    "name": model.name,
                    "version": model.version,
                    "file": model.file_path,
                    "module": model.module,
                    "hash": model.hash,
                    "type": "pydantic" if model.is_pydantic else "dataclass",
                    "fields": [
                        {
                            "name": f.name,
                            "type": f.type,
                            "required": f.required,
                            "default": f.default
                        }
                        for f in model.fields
                    ],
                    "used_in": model.used_in_endpoints,
                    "last_modified": model.last_modified
                }
                if model.docstring:
                    model_data["description"] = model.docstring
                data["models"].append(model_data)
        
        # Export endpoints
        for endpoint in self.endpoints:
            endpoint_data = {
                "path": endpoint.path,
                "method": endpoint.method,
                "function": endpoint.function_name,
                "file": endpoint.file_path,
                "version": endpoint.version
            }
            if endpoint.request_model:
                endpoint_data["request"] = endpoint.request_model
            if endpoint.response_model:
                endpoint_data["response"] = endpoint.response_model
            if endpoint.tags:
                endpoint_data["tags"] = endpoint.tags
            if endpoint.summary:
                endpoint_data["summary"] = endpoint.summary
            if endpoint.deprecated:
                endpoint_data["deprecated"] = True
            data["endpoints"].append(endpoint_data)
        
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)
        
        print(f"✓ Exported to YAML: {output_file}")
        return output_file
    
    def export_per_file_manifest(self, output_dir: str = ".tool-outputs/analysis/manifests"):
        """Export individual YAML manifest for each file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Group by file
        models_by_file = defaultdict(list)
        endpoints_by_file = defaultdict(list)
        
        for model in self.models.values():
            models_by_file[model.file_path].append(model)
        
        for endpoint in self.endpoints:
            endpoints_by_file[endpoint.file_path].append(endpoint)
        
        # Get all files
        all_files = set(models_by_file.keys()) | set(endpoints_by_file.keys())
        
        for file_path in all_files:
            manifest = {
                "file": file_path,
                "version": self.project_version,
                "models": [],
                "endpoints": []
            }
            
            # Add models
            for model in models_by_file.get(file_path, []):
                manifest["models"].append({
                    "name": model.name,
                    "hash": model.hash,
                    "fields": [{"name": f.name, "type": f.type} for f in model.fields]
                })
            
            # Add endpoints
            for endpoint in endpoints_by_file.get(file_path, []):
                manifest["endpoints"].append({
                    "path": endpoint.path,
                    "method": endpoint.method,
                    "request": endpoint.request_model,
                    "response": endpoint.response_model
                })
            
            # Write manifest
            safe_filename = file_path.replace("/", "_").replace("\\", "_").replace(".py", ".yaml")
            manifest_file = output_path / safe_filename
            
            with open(manifest_file, "w", encoding="utf-8") as f:
                yaml.dump(manifest, f, sort_keys=False)
        
        print(f"✓ Exported {len(all_files)} file manifests to: {output_dir}/")
        return output_path
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 70)
        print("VERSION TRACKER ANALYSIS")
        print("=" * 70)
        print(f"Project: {self.root_path}")
        print(f"Version: {self.project_version}")
        
        if self.git_info.commit_hash:
            print(f"\nGit Info:")
            print(f"  Commit:  {self.git_info.commit_hash[:8]}")
            print(f"  Branch:  {self.git_info.branch}")
            print(f"  Author:  {self.git_info.author}")
            print(f"  Dirty:   {self.git_info.is_dirty}")
        
        print(f"\nModels: {len(self.models)}")
        print(f"  Pydantic: {sum(1 for m in self.models.values() if m.is_pydantic)}")
        print(f"  Dataclass: {sum(1 for m in self.models.values() if m.is_dataclass)}")
        
        print(f"\nEndpoints: {len(self.endpoints)}")
        methods = defaultdict(int)
        for ep in self.endpoints:
            methods[ep.method] += 1
        for method, count in sorted(methods.items()):
            print(f"  {method}: {count}")
        
        print(f"\nFiles Analyzed: {len(self.files_analyzed)}")
        
        if self.models:
            print(f"\nTop Models:")
            for model in list(self.models.values())[:5]:
                print(f"  • {model.name} ({len(model.fields)} fields) - {model.file_path}")
                if model.used_in_endpoints:
                    print(f"    Used in: {', '.join(model.used_in_endpoints[:3])}")
        
        if self.endpoints:
            print(f"\nAPI Endpoints:")
            for endpoint in self.endpoints[:10]:
                print(f"  • {endpoint.method:6} {endpoint.path}")
                if endpoint.request_model:
                    print(f"           ← {endpoint.request_model}")
                if endpoint.response_model:
                    print(f"           → {endpoint.response_model}")
        
        print("=" * 70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Version tracking for FastAPI models and endpoints"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)"
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="Project version (default: 1.0.0)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export to JSON"
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Export to YAML (for CI/CD)"
    )
    parser.add_argument(
        "--manifests",
        action="store_true",
        help="Export per-file manifests"
    )
    parser.add_argument(
        "--mapping",
        action="store_true",
        help="Export mapping analysis (dependencies, impact, reuse)"
    )
    parser.add_argument(
        "--compare",
        metavar="FILE",
        help="Compare with previous analysis JSON file"
    )
    parser.add_argument(
        "--output-dir",
        default="version_analysis",
        help="Output directory (default: version_analysis)"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["venv", ".venv", "__pycache__", "node_modules"],
        help="Patterns to exclude"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Analyze
    tracker = VersionTracker(args.path, version=args.version)
    print(f"Analyzing: {tracker.root_path}")
    tracker.analyze_directory(exclude_patterns=args.exclude)
    
    # Print summary
    tracker.print_summary()
    
    # Compare with previous
    if args.compare:
        print("\nComparing with previous version...")
        changes = tracker.compare_with_previous(args.compare)
        
        print("\n" + "=" * 70)
        print("CHANGES DETECTED")
        print("=" * 70)
        
        if changes.get("models_added"):
            print(f"\n✓ Models Added: {len(changes['models_added'])}")
            for model in changes["models_added"]:
                print(f"  + {model}")
        
        if changes.get("models_removed"):
            print(f"\n✗ Models Removed: {len(changes['models_removed'])}")
            for model in changes["models_removed"]:
                print(f"  - {model}")
        
        if changes.get("models_modified"):
            print(f"\n~ Models Modified: {len(changes['models_modified'])}")
            for model in changes["models_modified"]:
                print(f"  ~ {model}")
                if model in changes.get("fields_added", {}):
                    for field in changes["fields_added"][model]:
                        print(f"      + field: {field}")
                if model in changes.get("fields_removed", {}):
                    for field in changes["fields_removed"][model]:
                        print(f"      - field: {field}")
                if model in changes.get("fields_modified", {}):
                    for field in changes["fields_modified"][model]:
                        print(f"      ~ field: {field}")
        
        if changes.get("breaking_changes"):
            print(f"\n⚠ BREAKING CHANGES: {len(changes['breaking_changes'])}")
            for change in changes["breaking_changes"]:
                print(f"  ⚠ {change['type']}: {change.get('model', '')}.{change.get('field', '')}")
        
        # Export changes
        changes_file = output_dir / "changes.json"
        with open(changes_file, "w", encoding="utf-8") as f:
            json.dump(changes, f, indent=2)
        print(f"\n✓ Changes exported to: {changes_file}")
    
    # Export formats
    if args.json or (not args.yaml and not args.manifests):
        json_file = output_dir / "version_analysis.json"
        tracker.export_to_json(str(json_file))
    
    if args.yaml:
        yaml_file = output_dir / "api_versions.yaml"
        tracker.export_to_yaml(str(yaml_file))
    
    if args.manifests:
        manifests_dir = output_dir / "manifests"
        tracker.export_per_file_manifest(str(manifests_dir))
    
    # Export mapping analysis
    if args.mapping:
        from mapping_analyzer import MappingAnalyzer
        mapping = MappingAnalyzer(tracker)
        mapping.export_analysis(str(output_dir / "mapping_analysis.json"))
        mapping.export_html_report(str(output_dir / "mapping_report.html"))
    
    print(f"\n✓ Analysis complete! Output in: {output_dir}/")


if __name__ == "__main__":
    main()
