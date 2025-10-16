#!/usr/bin/env python3
r"""
Deprecated Fields Tracker

Track and report deprecated fields across Pydantic models for migration planning.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # List all deprecated fields
    python deprecated_fields.py --list
    
    # Check specific model
    python deprecated_fields.py --model CreateCasefileRequest
    
    # Generate migration report
    python deprecated_fields.py --report
    
    # Check field usage across models
    python deprecated_fields.py --field casefile_id
    
    # Export deprecation data
    python deprecated_fields.py --export deprecated.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field as dc_field
from datetime import datetime
import inspect


@dataclass
class DeprecatedField:
    """Information about a deprecated field."""
    model_name: str
    field_name: str
    deprecated_since: Optional[str]
    replacement: Optional[str]
    removal_version: Optional[str]
    reason: Optional[str]
    migration_guide: Optional[str]


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


def extract_deprecated_fields(model_class: Type) -> List[DeprecatedField]:
    """Extract deprecated field information from a Pydantic model."""
    deprecated = []
    model_name = model_class.__name__
    
    try:
        for field_name, field_info in model_class.model_fields.items():
            # Check field description for deprecation markers
            description = field_info.description or ""
            
            is_deprecated = False
            deprecated_since = None
            replacement = None
            removal_version = None
            reason = None
            migration_guide = None
            
            # Check for @deprecated tag or DEPRECATED marker
            if '@deprecated' in description.lower() or 'deprecated' in description.lower():
                is_deprecated = True
                
                # Try to parse structured deprecation info
                lines = description.split('\n')
                for line in lines:
                    line_lower = line.lower().strip()
                    
                    if 'deprecated since' in line_lower:
                        deprecated_since = line.split(':', 1)[1].strip() if ':' in line else None
                    elif 'use' in line_lower and 'instead' in line_lower:
                        # Extract replacement field name
                        parts = line.lower().split('use')
                        if len(parts) > 1:
                            replacement_text = parts[1].split('instead')[0].strip()
                            replacement = replacement_text.strip('`\'" ')
                    elif 'will be removed' in line_lower:
                        # Extract removal version
                        parts = line.split('in', 1)
                        if len(parts) > 1:
                            removal_version = parts[1].strip()
                    elif 'reason:' in line_lower:
                        reason = line.split(':', 1)[1].strip()
                    elif 'migration:' in line_lower:
                        migration_guide = line.split(':', 1)[1].strip()
            
            # Check for deprecation in field metadata/json_schema_extra
            if hasattr(field_info, 'json_schema_extra'):
                extra = field_info.json_schema_extra
                if isinstance(extra, dict):
                    if extra.get('deprecated'):
                        is_deprecated = True
                        deprecated_since = extra.get('deprecated_since', deprecated_since)
                        replacement = extra.get('replacement', replacement)
                        removal_version = extra.get('removal_version', removal_version)
                        reason = extra.get('reason', reason)
                        migration_guide = extra.get('migration_guide', migration_guide)
            
            if is_deprecated:
                deprecated.append(DeprecatedField(
                    model_name=model_name,
                    field_name=field_name,
                    deprecated_since=deprecated_since,
                    replacement=replacement,
                    removal_version=removal_version,
                    reason=reason,
                    migration_guide=migration_guide
                ))
                
    except Exception as e:
        print(f"Warning: Could not extract deprecated fields from {model_name}: {e}", file=sys.stderr)
    
    return deprecated


def find_all_deprecated_fields(models: Dict[str, Type]) -> List[DeprecatedField]:
    """Find all deprecated fields across all models."""
    all_deprecated = []
    
    for model_name, model_class in sorted(models.items()):
        deprecated = extract_deprecated_fields(model_class)
        all_deprecated.extend(deprecated)
    
    return all_deprecated


def find_field_usage(models: Dict[str, Type], field_name: str) -> List[str]:
    """Find which models use a specific field."""
    usage = []
    
    for model_name, model_class in sorted(models.items()):
        if field_name in model_class.model_fields:
            usage.append(model_name)
    
    return usage


def generate_deprecation_report(deprecated_fields: List[DeprecatedField]) -> Dict[str, Any]:
    """Generate comprehensive deprecation report."""
    report = {
        'summary': {
            'total_deprecated_fields': len(deprecated_fields),
            'models_affected': len(set(f.model_name for f in deprecated_fields)),
            'with_replacement': sum(1 for f in deprecated_fields if f.replacement),
            'with_removal_version': sum(1 for f in deprecated_fields if f.removal_version),
        },
        'by_model': {},
        'by_removal_version': {},
        'needs_migration': []
    }
    
    # Group by model
    for field in deprecated_fields:
        if field.model_name not in report['by_model']:
            report['by_model'][field.model_name] = []
        report['by_model'][field.model_name].append({
            'field': field.field_name,
            'deprecated_since': field.deprecated_since,
            'replacement': field.replacement,
            'removal_version': field.removal_version
        })
    
    # Group by removal version
    for field in deprecated_fields:
        version = field.removal_version or 'unspecified'
        if version not in report['by_removal_version']:
            report['by_removal_version'][version] = []
        report['by_removal_version'][version].append({
            'model': field.model_name,
            'field': field.field_name,
            'replacement': field.replacement
        })
    
    # Fields needing migration (have replacement)
    for field in deprecated_fields:
        if field.replacement:
            report['needs_migration'].append({
                'model': field.model_name,
                'old_field': field.field_name,
                'new_field': field.replacement,
                'migration_guide': field.migration_guide
            })
    
    return report


def print_deprecated_list(deprecated_fields: List[DeprecatedField], detailed: bool = False):
    """Print list of deprecated fields."""
    if not deprecated_fields:
        print("\n✓ No deprecated fields found\n")
        return
    
    print(f"\n⚠ Found {len(deprecated_fields)} deprecated field(s):\n")
    print("=" * 80)
    
    for field in deprecated_fields:
        print(f"\n{field.model_name}.{field.field_name}")
        
        if field.deprecated_since:
            print(f"  Deprecated since: {field.deprecated_since}")
        
        if field.replacement:
            print(f"  Replacement: {field.replacement}")
        
        if field.removal_version:
            print(f"  Will be removed in: {field.removal_version}")
        
        if detailed:
            if field.reason:
                print(f"  Reason: {field.reason}")
            if field.migration_guide:
                print(f"  Migration: {field.migration_guide}")
    
    print("\n" + "=" * 80 + "\n")


def print_deprecation_report(report: Dict[str, Any]):
    """Print deprecation report in human-readable format."""
    print("\nDeprecation Report")
    print("=" * 80)
    
    print(f"\nSummary:")
    print(f"  Total deprecated fields: {report['summary']['total_deprecated_fields']}")
    print(f"  Models affected: {report['summary']['models_affected']}")
    print(f"  With replacement: {report['summary']['with_replacement']}")
    print(f"  With removal version: {report['summary']['with_removal_version']}")
    
    if report['by_removal_version']:
        print(f"\nBy Removal Version:")
        for version, fields in sorted(report['by_removal_version'].items()):
            print(f"  {version}: {len(fields)} field(s)")
            for field_info in fields:
                replacement_text = f" → {field_info['replacement']}" if field_info['replacement'] else ""
                print(f"    • {field_info['model']}.{field_info['field']}{replacement_text}")
    
    if report['needs_migration']:
        print(f"\nMigration Required ({len(report['needs_migration'])} field(s)):")
        for migration in report['needs_migration']:
            print(f"  {migration['model']}: {migration['old_field']} → {migration['new_field']}")
            if migration['migration_guide']:
                print(f"    Guide: {migration['migration_guide']}")
    
    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Track and report deprecated fields in Pydantic models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--list', action='store_true', help='List all deprecated fields')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--model', help='Check specific model for deprecated fields')
    parser.add_argument('--field', help='Check which models use a specific field')
    parser.add_argument('--report', action='store_true', help='Generate deprecation report')
    parser.add_argument('--export', help='Export deprecation data to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    # List deprecated fields
    if args.list:
        deprecated = find_all_deprecated_fields(models)
        if args.json:
            output = [
                {
                    'model': f.model_name,
                    'field': f.field_name,
                    'deprecated_since': f.deprecated_since,
                    'replacement': f.replacement,
                    'removal_version': f.removal_version,
                    'reason': f.reason
                }
                for f in deprecated
            ]
            print(json.dumps(output, indent=2))
        else:
            print_deprecated_list(deprecated, args.detailed)
        return
    
    # Generate report
    if args.report:
        deprecated = find_all_deprecated_fields(models)
        report = generate_deprecation_report(deprecated)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_deprecation_report(report)
        return
    
    # Export to file
    if args.export:
        deprecated = find_all_deprecated_fields(models)
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_models': len(models),
            'deprecated_fields': [
                {
                    'model': f.model_name,
                    'field': f.field_name,
                    'deprecated_since': f.deprecated_since,
                    'replacement': f.replacement,
                    'removal_version': f.removal_version,
                    'reason': f.reason,
                    'migration_guide': f.migration_guide
                }
                for f in deprecated
            ]
        }
        
        export_path = Path(args.export)
        export_path.write_text(json.dumps(export_data, indent=2))
        print(f"Exported deprecation data to {export_path}")
        return
    
    # Check specific model
    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        deprecated = extract_deprecated_fields(models[args.model])
        
        if args.json:
            output = [
                {
                    'field': f.field_name,
                    'deprecated_since': f.deprecated_since,
                    'replacement': f.replacement,
                    'removal_version': f.removal_version
                }
                for f in deprecated
            ]
            print(json.dumps(output, indent=2))
        else:
            if deprecated:
                print_deprecated_list(deprecated, args.detailed)
            else:
                print(f"\n✓ No deprecated fields in {args.model}\n")
        return
    
    # Check field usage
    if args.field:
        usage = find_field_usage(models, args.field)
        
        if args.json:
            print(json.dumps({'field': args.field, 'used_in': usage}, indent=2))
        else:
            print(f"\nField '{args.field}' used in {len(usage)} model(s):")
            for model_name in usage:
                print(f"  • {model_name}")
            print()
        return
    
    # Default: show summary
    deprecated = find_all_deprecated_fields(models)
    print(f"\n{len(models)} models loaded")
    print(f"{len(deprecated)} deprecated fields found")
    print("\nUse --help to see available commands")


if __name__ == '__main__':
    main()
