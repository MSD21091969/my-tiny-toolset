#!/usr/bin/env python3
r"""
Parameter Flow Validator

Validate parameter flow compatibility in workflow chains (method1 → method2 → method3).

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Validate two-method chain
    python parameter_flow_validator.py create_casefile add_session_to_casefile
    
    # Validate multi-method workflow
    python parameter_flow_validator.py create_casefile add_session_to_casefile grant_permission
    
    # JSON output
    python parameter_flow_validator.py create_casefile update_casefile --json
    
    # Detailed mode (show all field mappings)
    python parameter_flow_validator.py create_casefile update_casefile --detailed
    
    # Validate workflow from file
    python parameter_flow_validator.py --workflow-file workflow.txt
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CompatibilityStatus(Enum):
    """Compatibility status for field mappings."""
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    MISSING = "missing"
    OPTIONAL = "optional"


@dataclass
class FieldMapping:
    """Mapping between source and target fields."""
    source_field: str
    target_field: str
    source_type: str
    target_type: str
    status: CompatibilityStatus
    notes: Optional[str] = None


@dataclass
class StepValidation:
    """Validation result for a single workflow step."""
    step_index: int
    source_method: str
    target_method: str
    source_model: str
    target_model: str
    compatible_fields: List[FieldMapping] = field(default_factory=list)
    incompatible_fields: List[FieldMapping] = field(default_factory=list)
    missing_required_fields: List[str] = field(default_factory=list)
    extra_fields: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if step is valid (no missing required fields or incompatibilities)."""
        return len(self.missing_required_fields) == 0 and len(self.incompatible_fields) == 0
    
    @property
    def compatibility_score(self) -> float:
        """Calculate compatibility score (0.0 to 1.0)."""
        total = len(self.compatible_fields) + len(self.incompatible_fields) + len(self.missing_required_fields)
        if total == 0:
            return 1.0
        return len(self.compatible_fields) / total


@dataclass
class WorkflowValidation:
    """Complete workflow validation result."""
    methods: List[str]
    steps: List[StepValidation] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if entire workflow is valid."""
        return all(step.is_valid for step in self.steps)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall compatibility score."""
        if not self.steps:
            return 1.0
        return sum(step.compatibility_score for step in self.steps) / len(self.steps)


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
    
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    
    collider_src = path / "src"
    if str(collider_src) not in sys.path:
        sys.path.insert(0, str(collider_src))
    
    return path


def load_method_registry() -> Dict[str, Any]:
    """Load MANAGED_METHODS registry."""
    try:
        from pydantic_ai_integration.method_registry import MANAGED_METHODS
        
        # Import services to trigger registration
        service_modules = [
            'casefileservice', 'tool_sessionservice', 
            'communicationservice', 'authservice', 'coreservice'
        ]
        for module_name in service_modules:
            try:
                __import__(module_name)
            except ImportError:
                pass
        
        return dict(MANAGED_METHODS)
    except ImportError as e:
        print(f"Error: Could not load method registry: {e}", file=sys.stderr)
        sys.exit(1)


def load_pydantic_models() -> Dict[str, type]:
    """Load all Pydantic models."""
    models = {}
    
    try:
        from pydantic import BaseModel
        import inspect
        
        model_packages = [
            'pydantic_models.canonical',
            'pydantic_models.envelopes',
            'pydantic_models.operations',
            'pydantic_models.views',
            'pydantic_models.workspace',
        ]
        
        for package in model_packages:
            try:
                module = __import__(package, fromlist=['*'])
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseModel) and 
                        obj is not BaseModel and
                        not name.startswith('_')):
                        models[name] = obj
            except ImportError:
                continue
                
    except ImportError as e:
        print(f"Error: Could not load Pydantic models: {e}", file=sys.stderr)
        sys.exit(1)
    
    return models


def extract_model_fields(model_class: type) -> Dict[str, Dict[str, Any]]:
    """Extract field information from Pydantic model."""
    fields_info = {}
    
    try:
        for field_name, field_info in model_class.model_fields.items():
            # Get type string (simplified)
            type_str = str(field_info.annotation)
            if hasattr(field_info.annotation, '__name__'):
                type_str = field_info.annotation.__name__
            
            fields_info[field_name] = {
                'type': type_str,
                'required': field_info.is_required(),
                'annotation': field_info.annotation,
                'description': field_info.description
            }
    except Exception as e:
        print(f"Warning: Could not extract fields: {e}", file=sys.stderr)
    
    return fields_info


def normalize_type_string(type_str: str) -> str:
    """Normalize type string for comparison."""
    # Remove module paths
    if '.' in type_str:
        type_str = type_str.split('.')[-1]
    
    # Remove quotes
    type_str = type_str.replace("'", "").replace('"', '')
    
    # Handle common aliases
    aliases = {
        'typing.List': 'list',
        'typing.Dict': 'dict',
        'typing.Optional': 'Optional',
    }
    
    for old, new in aliases.items():
        type_str = type_str.replace(old, new)
    
    return type_str


def types_compatible(source_type: str, target_type: str) -> bool:
    """Check if two types are compatible."""
    source_norm = normalize_type_string(source_type)
    target_norm = normalize_type_string(target_type)
    
    # Exact match
    if source_norm == target_norm:
        return True
    
    # Optional compatibility
    if 'Optional' in target_norm and source_norm in target_norm:
        return True
    
    # Generic type compatibility (simplified)
    if source_norm.startswith('list') and target_norm.startswith('list'):
        return True
    if source_norm.startswith('dict') and target_norm.startswith('dict'):
        return True
    
    return False


def validate_step(
    source_method: str,
    target_method: str,
    methods_registry: Dict[str, Any],
    models: Dict[str, type]
) -> StepValidation:
    """Validate parameter flow between two methods."""
    
    # Get method metadata
    source_meta = methods_registry.get(source_method)
    target_meta = methods_registry.get(target_method)
    
    if not source_meta:
        raise ValueError(f"Method '{source_method}' not found in registry")
    if not target_meta:
        raise ValueError(f"Method '{target_method}' not found in registry")
    
    # Get model classes directly from metadata
    source_model = None
    source_model_name = "Unknown"
    target_model = None
    target_model_name = "Unknown"
    
    if hasattr(source_meta, 'response_model_class') and source_meta.response_model_class:
        source_model = source_meta.response_model_class
        source_model_name = source_model.__name__
    
    if hasattr(target_meta, 'request_model_class') and target_meta.request_model_class:
        target_model = target_meta.request_model_class
        target_model_name = target_model.__name__
    
    # Initialize validation result
    validation = StepValidation(
        step_index=0,
        source_method=source_method,
        target_method=target_method,
        source_model=source_model_name,
        target_model=target_model_name
    )
    
    # If models not specified, return early
    if not source_model or not target_model:
        validation.missing_required_fields.append("Model classes not available in registry")
        return validation
    
    # Extract fields
    source_fields = extract_model_fields(source_model)
    target_fields = extract_model_fields(target_model)
    
    # Check target required fields
    for field_name, field_info in target_fields.items():
        if not field_info['required']:
            continue
            
        if field_name in source_fields:
            source_info = source_fields[field_name]
            
            # Check type compatibility
            if types_compatible(source_info['type'], field_info['type']):
                validation.compatible_fields.append(FieldMapping(
                    source_field=field_name,
                    target_field=field_name,
                    source_type=source_info['type'],
                    target_type=field_info['type'],
                    status=CompatibilityStatus.COMPATIBLE
                ))
            else:
                validation.incompatible_fields.append(FieldMapping(
                    source_field=field_name,
                    target_field=field_name,
                    source_type=source_info['type'],
                    target_type=field_info['type'],
                    status=CompatibilityStatus.INCOMPATIBLE,
                    notes=f"Type mismatch: {source_info['type']} → {field_info['type']}"
                ))
        else:
            validation.missing_required_fields.append(field_name)
    
    # Check for extra source fields
    for field_name in source_fields:
        if field_name not in target_fields:
            validation.extra_fields.append(field_name)
    
    return validation


def validate_workflow(
    method_names: List[str],
    methods_registry: Dict[str, Any],
    models: Dict[str, type]
) -> WorkflowValidation:
    """Validate entire workflow chain."""
    workflow = WorkflowValidation(methods=method_names)
    
    for i in range(len(method_names) - 1):
        source = method_names[i]
        target = method_names[i + 1]
        
        try:
            step = validate_step(source, target, methods_registry, models)
            step.step_index = i + 1
            workflow.steps.append(step)
        except ValueError as e:
            print(f"Error validating step {i+1}: {e}", file=sys.stderr)
            sys.exit(1)
    
    return workflow


def print_validation_result(workflow: WorkflowValidation, detailed: bool = False):
    """Print workflow validation result in text format."""
    print(f"\n{'='*80}")
    print(f"Workflow Validation: {' → '.join(workflow.methods)}")
    print(f"{'='*80}\n")
    
    print(f"Overall Status: {'✓ VALID' if workflow.is_valid else '✗ INVALID'}")
    print(f"Compatibility Score: {workflow.overall_score:.1%}")
    print(f"Steps: {len(workflow.steps)}\n")
    
    for step in workflow.steps:
        print(f"{'─'*80}")
        print(f"Step {step.step_index}: {step.source_method} → {step.target_method}")
        print(f"{'─'*80}")
        print(f"Models: {step.source_model} → {step.target_model}")
        print(f"Status: {'✓ Valid' if step.is_valid else '✗ Invalid'}")
        print(f"Score: {step.compatibility_score:.1%}\n")
        
        if step.compatible_fields:
            print(f"✓ Compatible Fields ({len(step.compatible_fields)}):")
            for mapping in step.compatible_fields:
                if detailed:
                    print(f"  • {mapping.source_field}: {mapping.source_type}")
                else:
                    print(f"  • {mapping.source_field}")
            print()
        
        if step.incompatible_fields:
            print(f"✗ Incompatible Fields ({len(step.incompatible_fields)}):")
            for mapping in step.incompatible_fields:
                print(f"  • {mapping.source_field}")
                print(f"    Source: {mapping.source_type}")
                print(f"    Target: {mapping.target_type}")
                if mapping.notes:
                    print(f"    Note: {mapping.notes}")
            print()
        
        if step.missing_required_fields:
            print(f"⚠ Missing Required Fields ({len(step.missing_required_fields)}):")
            for field in step.missing_required_fields:
                print(f"  • {field}")
            print()
        
        if detailed and step.extra_fields:
            print(f"ℹ Extra Source Fields ({len(step.extra_fields)}):")
            for field in step.extra_fields[:5]:  # Limit to 5
                print(f"  • {field}")
            if len(step.extra_fields) > 5:
                print(f"  ... and {len(step.extra_fields) - 5} more")
            print()
    
    print(f"{'='*80}\n")


def print_validation_json(workflow: WorkflowValidation):
    """Print workflow validation result in JSON format."""
    output = {
        'workflow': workflow.methods,
        'valid': workflow.is_valid,
        'score': workflow.overall_score,
        'steps': [
            {
                'index': step.step_index,
                'source_method': step.source_method,
                'target_method': step.target_method,
                'source_model': step.source_model,
                'target_model': step.target_model,
                'valid': step.is_valid,
                'score': step.compatibility_score,
                'compatible_fields': [
                    {
                        'field': m.source_field,
                        'source_type': m.source_type,
                        'target_type': m.target_type
                    }
                    for m in step.compatible_fields
                ],
                'incompatible_fields': [
                    {
                        'field': m.source_field,
                        'source_type': m.source_type,
                        'target_type': m.target_type,
                        'notes': m.notes
                    }
                    for m in step.incompatible_fields
                ],
                'missing_required_fields': step.missing_required_fields,
                'extra_fields': step.extra_fields
            }
            for step in workflow.steps
        ]
    }
    
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Validate parameter flow in workflow chains",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('methods', nargs='*', help='Method names in workflow order')
    parser.add_argument('--workflow-file', help='Read workflow from file (one method per line)')
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--detailed', action='store_true', help='Show detailed field information')
    
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
    setup_collider_path(args.collider_path)
    methods_registry = load_method_registry()
    models = load_pydantic_models()
    
    # Validate workflow
    workflow = validate_workflow(method_names, methods_registry, models)
    
    # Output results
    if args.json:
        print_validation_json(workflow)
    else:
        print_validation_result(workflow, args.detailed)
    
    # Exit code reflects validity
    sys.exit(0 if workflow.is_valid else 1)


if __name__ == '__main__':
    main()
