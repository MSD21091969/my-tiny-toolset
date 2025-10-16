#!/usr/bin/env python3
r"""
Workflow Validator

Comprehensive workflow validation combining method discovery, field mapping, and parameter flow.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Validate workflow by method names
    python workflow_validator.py create_casefile add_session_to_casefile grant_permission
    
    # Validate from file
    python workflow_validator.py --workflow-file myworkflow.txt
    
    # Suggest fixes for invalid workflow
    python workflow_validator.py create_casefile grant_permission --suggest-fixes
    
    # Full report with all details
    python workflow_validator.py method1 method2 method3 --full-report
    
    # JSON output for CI/CD
    python workflow_validator.py method1 method2 --json
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class WorkflowIssue:
    """An issue found in workflow validation."""
    severity: str  # error, warning, info
    step: Optional[int]
    category: str  # missing_field, type_mismatch, method_not_found, etc.
    message: str
    suggestion: Optional[str] = None


@dataclass
class WorkflowValidationResult:
    """Complete workflow validation result."""
    valid: bool
    methods: List[str]
    issues: List[WorkflowIssue] = field(default_factory=list)
    parameter_flow_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'error')
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == 'warning')


def setup_collider_path(collider_path: Optional[str] = None) -> Path:
    """Set up path to collider repository."""
    if collider_path:
        path = Path(collider_path)
    else:
        import os
        collider_env = os.getenv("COLLIDER_PATH")
        if collider_env:
            path = Path(collider_env)
        else:
            toolset_root = Path(__file__).parent.parent
            path = toolset_root.parent / "my-tiny-data-collider"
    
    if not path.exists():
        print(f"Error: Collider repository not found at {path}", file=sys.stderr)
        sys.exit(1)
    
    return path


def run_tool(tool_name: str, args: List[str], collider_path: Path) -> Dict[str, Any]:
    """Run a workflow tool and return JSON output."""
    tool_path = Path(__file__).parent / f"{tool_name}.py"
    
    if not tool_path.exists():
        return {'error': f'Tool {tool_name} not found'}
    
    cmd = [
        sys.executable,
        str(tool_path),
        *args,
        '--json',
        '--collider-path', str(collider_path)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse JSON from stdout
        if result.stdout:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON output', 'stdout': result.stdout[:200]}
        
        return {'error': 'No output', 'stderr': result.stderr[:200]}
        
    except subprocess.TimeoutExpired:
        return {'error': 'Tool execution timeout'}
    except Exception as e:
        return {'error': str(e)}


def validate_methods_exist(methods: List[str], collider_path: Path) -> List[WorkflowIssue]:
    """Validate that all methods exist in registry."""
    issues = []
    
    # Run method_search to get all methods
    result = run_tool('method_search', ['--list-all'], collider_path)
    
    if 'error' in result:
        issues.append(WorkflowIssue(
            severity='error',
            step=None,
            category='tool_error',
            message=f"Could not load method registry: {result['error']}"
        ))
        return issues
    
    available_methods = {m['name'] for m in result.get('methods', [])}
    
    for i, method in enumerate(methods, 1):
        if method not in available_methods:
            issues.append(WorkflowIssue(
                severity='error',
                step=i,
                category='method_not_found',
                message=f"Method '{method}' not found in registry",
                suggestion=f"Run 'python method_search.py \"{method}\"' to find similar methods"
            ))
    
    return issues


def validate_parameter_flow(methods: List[str], collider_path: Path) -> tuple[List[WorkflowIssue], float]:
    """Validate parameter flow between methods."""
    issues = []
    
    # Run parameter_flow_validator
    result = run_tool('parameter_flow_validator', methods, collider_path)
    
    if 'error' in result:
        issues.append(WorkflowIssue(
            severity='error',
            step=None,
            category='tool_error',
            message=f"Could not validate parameter flow: {result['error']}"
        ))
        return issues, 0.0
    
    score = result.get('score', 0.0)
    
    # Process each step
    for step_data in result.get('steps', []):
        step_index = step_data['index']
        
        # Missing required fields
        for field in step_data.get('missing_required_fields', []):
            issues.append(WorkflowIssue(
                severity='error',
                step=step_index,
                category='missing_field',
                message=f"Step {step_index}: Required field '{field}' not provided by previous method",
                suggestion=f"Add manual parameter for '{field}' or insert intermediate method"
            ))
        
        # Incompatible fields
        for incomp in step_data.get('incompatible_fields', []):
            issues.append(WorkflowIssue(
                severity='error',
                step=step_index,
                category='type_mismatch',
                message=f"Step {step_index}: Field '{incomp['field']}' type mismatch: {incomp['source_type']} → {incomp['target_type']}",
                suggestion="Add transformation step between methods"
            ))
        
        # Warnings for extra fields
        if len(step_data.get('extra_fields', [])) > 3:
            issues.append(WorkflowIssue(
                severity='warning',
                step=step_index,
                category='extra_fields',
                message=f"Step {step_index}: {len(step_data['extra_fields'])} unused output fields",
                suggestion="Consider if workflow is extracting the right data"
            ))
    
    return issues, score


def get_method_metadata(method: str, collider_path: Path) -> Optional[Dict[str, Any]]:
    """Get metadata for a single method."""
    result = run_tool('method_search', [method], collider_path)
    
    if 'error' in result or not result.get('methods'):
        return None
    
    return result['methods'][0] if result['methods'] else None


def suggest_workflow_fixes(issues: List[WorkflowIssue], methods: List[str], collider_path: Path) -> List[str]:
    """Suggest fixes for workflow issues."""
    suggestions = []
    
    # Group issues by type
    missing_fields = {}
    for issue in issues:
        if issue.category == 'missing_field' and issue.step:
            step = issue.step
            missing_fields.setdefault(step, []).append(issue.message)
    
    # Suggest intermediate methods
    if missing_fields:
        for step, fields in missing_fields.items():
            if step > 1:
                source_method = methods[step - 2]
                target_method = methods[step - 1]
                suggestions.append(
                    f"Step {step} ({source_method}→{target_method}): "
                    f"Search for methods that output required fields using: "
                    f"python model_field_search.py \"<field_name>\""
                )
    
    # Check for method classification issues
    metadata_cache = {}
    for i in range(len(methods) - 1):
        source = methods[i]
        target = methods[i + 1]
        
        if source not in metadata_cache:
            metadata_cache[source] = get_method_metadata(source, collider_path)
        if target not in metadata_cache:
            metadata_cache[target] = get_method_metadata(target, collider_path)
        
        source_meta = metadata_cache[source]
        target_meta = metadata_cache[target]
        
        if source_meta and target_meta:
            # Check if complexity is compatible
            if source_meta.get('complexity') == 'atomic' and target_meta.get('complexity') == 'pipeline':
                suggestions.append(
                    f"Consider adding composite method between {source} (atomic) and {target} (pipeline)"
                )
    
    return suggestions


def validate_workflow(
    methods: List[str],
    collider_path: Path,
    suggest_fixes: bool = False
) -> WorkflowValidationResult:
    """Perform comprehensive workflow validation."""
    
    result = WorkflowValidationResult(
        valid=True,
        methods=methods
    )
    
    # Validate methods exist
    method_issues = validate_methods_exist(methods, collider_path)
    result.issues.extend(method_issues)
    
    # If methods don't exist, can't continue
    if any(i.category == 'method_not_found' for i in method_issues):
        result.valid = False
        return result
    
    # Validate parameter flow
    flow_issues, score = validate_parameter_flow(methods, collider_path)
    result.issues.extend(flow_issues)
    result.parameter_flow_score = score
    
    # Collect metadata
    for method in methods:
        meta = get_method_metadata(method, collider_path)
        if meta:
            result.metadata[method] = {
                'domain': meta.get('domain'),
                'subdomain': meta.get('subdomain'),
                'capability': meta.get('capability'),
                'complexity': meta.get('complexity')
            }
    
    # Determine validity
    result.valid = result.error_count == 0
    
    # Generate suggestions if requested
    if suggest_fixes and not result.valid:
        suggestions = suggest_workflow_fixes(result.issues, methods, collider_path)
        for suggestion in suggestions:
            result.issues.append(WorkflowIssue(
                severity='info',
                step=None,
                category='suggestion',
                message=suggestion
            ))
    
    return result


def print_validation_result(result: WorkflowValidationResult, full_report: bool = False):
    """Print validation result in human-readable format."""
    
    print("\n" + "=" * 80)
    print(f"Workflow Validation: {' → '.join(result.methods)}")
    print("=" * 80 + "\n")
    
    # Overall status
    status_icon = "✓" if result.valid else "✗"
    status_text = "VALID" if result.valid else "INVALID"
    print(f"Status: {status_icon} {status_text}")
    print(f"Parameter Flow Score: {result.parameter_flow_score:.1%}")
    print(f"Issues: {result.error_count} errors, {result.warning_count} warnings\n")
    
    # Issues by severity
    if result.issues:
        errors = [i for i in result.issues if i.severity == 'error']
        warnings = [i for i in result.issues if i.severity == 'warning']
        infos = [i for i in result.issues if i.severity == 'info']
        
        if errors:
            print("✗ ERRORS:\n")
            for issue in errors:
                step_text = f"[Step {issue.step}] " if issue.step else ""
                print(f"  {step_text}{issue.message}")
                if issue.suggestion and full_report:
                    print(f"    → Suggestion: {issue.suggestion}")
            print()
        
        if warnings:
            print("⚠ WARNINGS:\n")
            for issue in warnings:
                step_text = f"[Step {issue.step}] " if issue.step else ""
                print(f"  {step_text}{issue.message}")
            print()
        
        if infos and full_report:
            print("ℹ SUGGESTIONS:\n")
            for issue in infos:
                print(f"  • {issue.message}")
            print()
    
    # Method metadata
    if full_report and result.metadata:
        print("METHOD DETAILS:\n")
        for method, meta in result.metadata.items():
            print(f"  {method}:")
            print(f"    Domain: {meta.get('domain')}")
            print(f"    Capability: {meta.get('capability')}")
            print(f"    Complexity: {meta.get('complexity')}")
        print()
    
    print("=" * 80 + "\n")


def print_validation_json(result: WorkflowValidationResult):
    """Print validation result as JSON."""
    output = {
        'valid': result.valid,
        'workflow': result.methods,
        'score': result.parameter_flow_score,
        'errors': result.error_count,
        'warnings': result.warning_count,
        'issues': [
            {
                'severity': i.severity,
                'step': i.step,
                'category': i.category,
                'message': i.message,
                'suggestion': i.suggestion
            }
            for i in result.issues
        ],
        'metadata': result.metadata
    }
    
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive workflow validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('methods', nargs='*', help='Method names in workflow order')
    parser.add_argument('--workflow-file', help='Read workflow from file (one method per line)')
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--suggest-fixes', action='store_true', help='Suggest fixes for issues')
    parser.add_argument('--full-report', action='store_true', help='Show detailed report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Get method names
    method_names = args.methods
    
    if args.workflow_file:
        workflow_path = Path(args.workflow_file)
        if not workflow_path.exists():
            print(f"Error: Workflow file not found: {workflow_path}", file=sys.stderr)
            sys.exit(1)
        method_names = [line.strip() for line in workflow_path.read_text().splitlines() if line.strip()]
    
    if len(method_names) < 2:
        print("Error: Need at least 2 methods to validate workflow", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Setup
    collider_path = setup_collider_path(args.collider_path)
    
    # Validate
    result = validate_workflow(method_names, collider_path, args.suggest_fixes)
    
    # Output
    if args.json:
        print_validation_json(result)
    else:
        print_validation_result(result, args.full_report)
    
    # Exit code
    sys.exit(0 if result.valid else 1)


if __name__ == '__main__':
    main()
