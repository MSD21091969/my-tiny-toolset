#!/usr/bin/env python3
r"""
JSON Schema Example Generator

Add comprehensive JSON schema examples to Pydantic models for better API documentation.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # List models without examples
    python json_schema_examples.py --list-missing
    
    # Generate examples for specific model
    python json_schema_examples.py --model CreateCasefileRequest
    
    # Generate examples for all models (dry run)
    python json_schema_examples.py --generate-all --dry-run
    
    # Apply examples to models
    python json_schema_examples.py --generate-all --apply
    
    # Export all examples to JSON
    python json_schema_examples.py --export examples.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from datetime import datetime, timezone
from uuid import UUID
import inspect


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


def load_pydantic_models() -> Dict[str, Type]:
    """Load all Pydantic models from collider."""
    models = {}
    
    try:
        from pydantic import BaseModel
        
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
            except ImportError as e:
                print(f"Warning: Could not import {package}: {e}", file=sys.stderr)
                continue
                
    except ImportError as e:
        print(f"Error: Could not import Pydantic: {e}", file=sys.stderr)
        sys.exit(1)
    
    return models


def has_schema_example(model_class: Type) -> bool:
    """Check if model already has a schema example."""
    if not hasattr(model_class, 'model_config'):
        return False
    
    config = model_class.model_config
    if isinstance(config, dict):
        return 'json_schema_extra' in config and 'example' in config.get('json_schema_extra', {})
    
    return hasattr(config, 'json_schema_extra') and 'example' in getattr(config, 'json_schema_extra', {})


def generate_example_value(field_name: str, field_type: Any) -> Any:
    """Generate example value for a field based on its type and name."""
    
    # Handle by field name patterns
    if 'email' in field_name.lower():
        return "user@example.com"
    elif field_name in ['casefile_id', 'id'] and 'casefile' in field_name:
        return "cf_250116_abc123"
    elif field_name == 'user_id' or field_name == 'owner_id':
        return "user@example.com"
    elif field_name == 'session_id':
        return "session_xyz789"
    elif 'timestamp' in field_name or field_name in ['created_at', 'updated_at']:
        return datetime.now(timezone.utc).isoformat()
    elif field_name == 'request_id':
        return str(UUID('12345678-1234-5678-1234-567812345678'))
    elif 'title' in field_name:
        return "Example Title"
    elif 'description' in field_name:
        return "Example description text"
    elif 'name' in field_name:
        return "Example Name"
    elif 'status' in field_name:
        return "success"
    elif 'message' in field_name:
        return "Operation completed successfully"
    elif 'url' in field_name:
        return "https://example.com"
    
    # Handle by type
    type_str = str(field_type).lower()
    
    if 'str' in type_str:
        return f"example_{field_name}"
    elif 'int' in type_str:
        return 42
    elif 'float' in type_str:
        return 3.14
    elif 'bool' in type_str:
        return True
    elif 'uuid' in type_str:
        return str(UUID('12345678-1234-5678-1234-567812345678'))
    elif 'datetime' in type_str:
        return datetime.now(timezone.utc).isoformat()
    elif 'list' in type_str or 'array' in type_str:
        return []
    elif 'dict' in type_str:
        return {}
    
    return None


def generate_model_example(model_class: Type) -> Dict[str, Any]:
    """Generate example data for a Pydantic model."""
    example = {}
    
    try:
        for field_name, field_info in model_class.model_fields.items():
            # Skip if not required and no default
            if not field_info.is_required() and field_info.default is None:
                continue
            
            # Generate value
            value = generate_example_value(field_name, field_info.annotation)
            
            # Handle nested models
            if value is None and hasattr(field_info.annotation, 'model_fields'):
                value = generate_model_example(field_info.annotation)
            
            if value is not None:
                example[field_name] = value
                
    except Exception as e:
        print(f"Warning: Could not generate example for {model_class.__name__}: {e}", file=sys.stderr)
    
    return example


def list_models_without_examples(models: Dict[str, Type]) -> List[str]:
    """List models that don't have schema examples."""
    missing = []
    
    for name, model_class in sorted(models.items()):
        if not has_schema_example(model_class):
            missing.append(name)
    
    return missing


def export_examples(models: Dict[str, Type], output_file: Path):
    """Export all model examples to JSON file."""
    examples = {}
    
    for name, model_class in sorted(models.items()):
        examples[name] = {
            'module': model_class.__module__,
            'has_example': has_schema_example(model_class),
            'generated_example': generate_model_example(model_class)
        }
    
    output_file.write_text(json.dumps(examples, indent=2, default=str))
    print(f"Exported examples to {output_file}")


def generate_config_code(model_name: str, example: Dict[str, Any]) -> str:
    """Generate model_config code snippet for adding examples."""
    example_json = json.dumps(example, indent=8, default=str)
    
    return f"""
    model_config = ConfigDict(
        json_schema_extra={{
            "example": {example_json}
        }}
    )
"""


def print_missing_examples(models: Dict[str, Type], detailed: bool = False):
    """Print models without examples."""
    missing = list_models_without_examples(models)
    
    print(f"\nFound {len(missing)} model(s) without JSON schema examples:\n")
    print("=" * 80)
    
    for name in missing:
        model_class = models[name]
        field_count = len(model_class.model_fields)
        print(f"\n{name} ({field_count} fields)")
        print(f"  Module: {model_class.__module__}")
        
        if detailed:
            example = generate_model_example(model_class)
            print(f"  Generated Example:")
            print(json.dumps(example, indent=4, default=str))
    
    print("\n" + "=" * 80 + "\n")
    
    # Summary by package
    by_package = {}
    for name in missing:
        package = models[name].__module__.split('.')[1]  # canonical, envelopes, etc.
        by_package.setdefault(package, []).append(name)
    
    print("By Package:")
    for package, model_names in sorted(by_package.items()):
        print(f"  {package}: {len(model_names)} models")
    print()


def generate_examples_report(models: Dict[str, Type]) -> Dict[str, Any]:
    """Generate comprehensive examples report."""
    total = len(models)
    with_examples = sum(1 for m in models.values() if has_schema_example(m))
    without_examples = total - with_examples
    
    report = {
        'summary': {
            'total_models': total,
            'with_examples': with_examples,
            'without_examples': without_examples,
            'coverage': f"{with_examples/total*100:.1f}%" if total > 0 else "0%"
        },
        'by_package': {},
        'missing': []
    }
    
    # By package stats
    packages = {}
    for name, model_class in models.items():
        package = model_class.__module__.split('.')[1]
        packages.setdefault(package, {'total': 0, 'with_examples': 0, 'models': []})
        packages[package]['total'] += 1
        packages[package]['models'].append(name)
        if has_schema_example(model_class):
            packages[package]['with_examples'] += 1
    
    for package, stats in packages.items():
        coverage = stats['with_examples'] / stats['total'] * 100 if stats['total'] > 0 else 0
        report['by_package'][package] = {
            'total': stats['total'],
            'with_examples': stats['with_examples'],
            'coverage': f"{coverage:.1f}%"
        }
    
    # Missing models
    report['missing'] = list_models_without_examples(models)
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSON schema examples for Pydantic models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--list-missing', action='store_true', help='List models without examples')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--model', help='Generate example for specific model')
    parser.add_argument('--export', help='Export all examples to JSON file')
    parser.add_argument('--report', action='store_true', help='Generate coverage report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    # List missing examples
    if args.list_missing:
        print_missing_examples(models, args.detailed)
        return
    
    # Export examples
    if args.export:
        export_examples(models, Path(args.export))
        return
    
    # Generate report
    if args.report:
        report = generate_examples_report(models)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\nJSON Schema Examples Coverage Report")
            print("=" * 80)
            print(f"\nTotal Models: {report['summary']['total_models']}")
            print(f"With Examples: {report['summary']['with_examples']}")
            print(f"Without Examples: {report['summary']['without_examples']}")
            print(f"Coverage: {report['summary']['coverage']}\n")
            
            print("By Package:")
            for package, stats in sorted(report['by_package'].items()):
                print(f"  {package}: {stats['with_examples']}/{stats['total']} ({stats['coverage']})")
            print()
        return
    
    # Single model example
    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        model_class = models[args.model]
        example = generate_model_example(model_class)
        
        if args.json:
            print(json.dumps(example, indent=2, default=str))
        else:
            print(f"\nGenerated example for {args.model}:")
            print(generate_config_code(args.model, example))
        return
    
    # Default: show summary
    report = generate_examples_report(models)
    print(f"\n{report['summary']['total_models']} models loaded")
    print(f"Coverage: {report['summary']['coverage']}")
    print("\nUse --help to see available commands")


if __name__ == '__main__':
    main()
