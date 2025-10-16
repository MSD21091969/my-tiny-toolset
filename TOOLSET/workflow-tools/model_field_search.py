#!/usr/bin/env python3
r"""
Model Field Search Tool

Search Pydantic models for fields and analyze field compatibility for workflow composition.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Search for field name
    python model_field_search.py "casefile_id"
    
    # Search in specific model
    python model_field_search.py --model CreateCasefileRequest "title"
    
    # Find compatible mappings (response field → request field)
    python model_field_search.py --map-from CreateCasefileResponse --map-to UpdateCasefileRequest
    
    # List all models
    python model_field_search.py --list-models
    
    # JSON output
    python model_field_search.py "email" --json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, get_type_hints, get_origin, get_args
from dataclasses import dataclass
import inspect


@dataclass
class FieldInfo:
    """Information about a model field."""
    name: str
    type_str: str
    required: bool
    default: Optional[str]
    description: Optional[str]
    model_name: str
    model_module: str


@dataclass
class FieldMapping:
    """Mapping between source and target fields."""
    source_field: str
    target_field: str
    source_model: str
    target_model: str
    type_compatible: bool
    source_type: str
    target_type: str
    notes: Optional[str] = None


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
            # Try relative path from toolset to collider
            toolset_root = Path(__file__).parent.parent
            path = toolset_root.parent / "my-tiny-data-collider"
    
    if not path.exists():
        print(f"Error: Collider repository not found at {path}", file=sys.stderr)
        print("Set COLLIDER_PATH environment variable or use --collider-path", file=sys.stderr)
        sys.exit(1)
    
    # Add both repository root and src to sys.path
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    
    collider_src = path / "src"
    if str(collider_src) not in sys.path:
        sys.path.insert(0, str(collider_src))
    
    return path


def load_pydantic_models() -> Dict[str, type]:
    """Load all Pydantic models from collider."""
    models = {}
    
    try:
        from pydantic import BaseModel
        
        # Import all model modules
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
                
                # Find all BaseModel subclasses
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


def get_type_string(field_type: Any) -> str:
    """Convert type annotation to readable string."""
    # Handle string annotations
    if isinstance(field_type, str):
        return field_type
    
    # Get origin (e.g., list, dict, Optional)
    origin = get_origin(field_type)
    
    if origin is None:
        # Simple type
        if hasattr(field_type, '__name__'):
            return field_type.__name__
        return str(field_type)
    
    # Handle Union (Optional)
    if origin is type(None) or str(origin) == 'typing.Union':
        args = get_args(field_type)
        if len(args) == 2 and type(None) in args:
            # Optional[X]
            other = args[0] if args[1] is type(None) else args[1]
            return f"Optional[{get_type_string(other)}]"
        else:
            # Union[X, Y, ...]
            arg_strs = [get_type_string(arg) for arg in args]
            return f"Union[{', '.join(arg_strs)}]"
    
    # Handle generic types (List, Dict, etc.)
    args = get_args(field_type)
    if args:
        arg_strs = [get_type_string(arg) for arg in args]
        origin_name = origin.__name__ if hasattr(origin, '__name__') else str(origin)
        return f"{origin_name}[{', '.join(arg_strs)}]"
    
    return str(field_type)


def extract_field_info(model_name: str, model_class: type) -> List[FieldInfo]:
    """Extract field information from a Pydantic model."""
    fields = []
    
    try:
        # Get model fields
        model_fields = model_class.model_fields
        
        for field_name, field_info in model_fields.items():
            # Get type annotation
            type_str = get_type_string(field_info.annotation)
            
            # Check if required
            required = field_info.is_required()
            
            # Get default value
            default = None
            if not required and field_info.default is not None:
                default = str(field_info.default)
            
            # Get description
            description = field_info.description
            
            fields.append(FieldInfo(
                name=field_name,
                type_str=type_str,
                required=required,
                default=default,
                description=description,
                model_name=model_name,
                model_module=model_class.__module__
            ))
            
    except Exception as e:
        print(f"Warning: Could not extract fields from {model_name}: {e}", file=sys.stderr)
    
    return fields


def search_fields(models: Dict[str, type], query: str, model_filter: Optional[str] = None) -> List[FieldInfo]:
    """Search for fields matching query."""
    results = []
    query_lower = query.lower()
    
    for model_name, model_class in models.items():
        # Apply model filter
        if model_filter and model_name != model_filter:
            continue
        
        fields = extract_field_info(model_name, model_class)
        
        for field in fields:
            # Match field name or description
            if (query_lower in field.name.lower() or
                (field.description and query_lower in field.description.lower())):
                results.append(field)
    
    return results


def find_compatible_mappings(models: Dict[str, type], source_model: str, target_model: str) -> List[FieldMapping]:
    """Find compatible field mappings between two models."""
    mappings = []
    
    if source_model not in models:
        print(f"Error: Source model '{source_model}' not found", file=sys.stderr)
        return mappings
    
    if target_model not in models:
        print(f"Error: Target model '{target_model}' not found", file=sys.stderr)
        return mappings
    
    source_fields = {f.name: f for f in extract_field_info(source_model, models[source_model])}
    target_fields = {f.name: f for f in extract_field_info(target_model, models[target_model])}
    
    # Find exact name matches
    for field_name in source_fields:
        if field_name in target_fields:
            source_field = source_fields[field_name]
            target_field = target_fields[field_name]
            
            # Check type compatibility (simple string comparison)
            type_compatible = source_field.type_str == target_field.type_str
            
            notes = None
            if not type_compatible:
                notes = f"Type mismatch: {source_field.type_str} vs {target_field.type_str}"
            
            mappings.append(FieldMapping(
                source_field=field_name,
                target_field=field_name,
                source_model=source_model,
                target_model=target_model,
                type_compatible=type_compatible,
                source_type=source_field.type_str,
                target_type=target_field.type_str,
                notes=notes
            ))
    
    # Find semantic matches (common patterns)
    semantic_patterns = [
        ('id', 'casefile_id'),
        ('casefile_id', 'id'),
        ('user_id', 'owner_id'),
        ('owner_id', 'user_id'),
    ]
    
    for source_pattern, target_pattern in semantic_patterns:
        if source_pattern in source_fields and target_pattern in target_fields:
            source_field = source_fields[source_pattern]
            target_field = target_fields[target_pattern]
            
            # Check if not already mapped
            if not any(m.source_field == source_pattern and m.target_field == target_pattern for m in mappings):
                type_compatible = source_field.type_str == target_field.type_str
                
                mappings.append(FieldMapping(
                    source_field=source_pattern,
                    target_field=target_pattern,
                    source_model=source_model,
                    target_model=target_model,
                    type_compatible=type_compatible,
                    source_type=source_field.type_str,
                    target_type=target_field.type_str,
                    notes="Semantic mapping"
                ))
    
    return mappings


def print_field_results(fields: List[FieldInfo], json_output: bool = False):
    """Print field search results."""
    if json_output:
        output = {
            'count': len(fields),
            'fields': [
                {
                    'name': f.name,
                    'type': f.type_str,
                    'required': f.required,
                    'default': f.default,
                    'description': f.description,
                    'model': f.model_name,
                    'module': f.model_module
                }
                for f in fields
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nFound {len(fields)} field(s):\n")
        print("=" * 80)
        
        for i, field in enumerate(fields, 1):
            print(f"\n{i}. {field.model_name}.{field.name}")
            print(f"   Type: {field.type_str}")
            print(f"   Required: {field.required}")
            if field.default:
                print(f"   Default: {field.default}")
            if field.description:
                print(f"   Description: {field.description}")
            print(f"   Module: {field.model_module}")
        
        print("\n" + "=" * 80 + "\n")


def print_mapping_results(mappings: List[FieldMapping], json_output: bool = False):
    """Print field mapping results."""
    if json_output:
        output = {
            'count': len(mappings),
            'compatible': sum(1 for m in mappings if m.type_compatible),
            'incompatible': sum(1 for m in mappings if not m.type_compatible),
            'mappings': [
                {
                    'source_field': m.source_field,
                    'target_field': m.target_field,
                    'source_model': m.source_model,
                    'target_model': m.target_model,
                    'type_compatible': m.type_compatible,
                    'source_type': m.source_type,
                    'target_type': m.target_type,
                    'notes': m.notes
                }
                for m in mappings
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        compatible = [m for m in mappings if m.type_compatible]
        incompatible = [m for m in mappings if not m.type_compatible]
        
        print(f"\nFound {len(mappings)} field mapping(s):")
        print(f"  ✓ Compatible: {len(compatible)}")
        print(f"  ⚠ Incompatible: {len(incompatible)}\n")
        print("=" * 80)
        
        if compatible:
            print("\n✓ Compatible Mappings:\n")
            for i, m in enumerate(compatible, 1):
                print(f"{i}. {m.source_model}.{m.source_field} → {m.target_model}.{m.target_field}")
                print(f"   Type: {m.source_type}")
                if m.notes:
                    print(f"   Note: {m.notes}")
        
        if incompatible:
            print("\n⚠ Incompatible Mappings:\n")
            for i, m in enumerate(incompatible, 1):
                print(f"{i}. {m.source_model}.{m.source_field} → {m.target_model}.{m.target_field}")
                print(f"   Source: {m.source_type}")
                print(f"   Target: {m.target_type}")
                if m.notes:
                    print(f"   Note: {m.notes}")
        
        print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Search Pydantic model fields and analyze field compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('query', nargs='?', help='Field name to search for')
    parser.add_argument('--model', help='Filter by specific model name')
    parser.add_argument('--list-models', action='store_true', help='List all available models')
    parser.add_argument('--map-from', help='Source model for field mapping')
    parser.add_argument('--map-to', help='Target model for field mapping')
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup paths
    setup_collider_path(args.collider_path)
    
    # Load models
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    # List models
    if args.list_models:
        if args.json:
            print(json.dumps({'count': len(models), 'models': sorted(models.keys())}, indent=2))
        else:
            print(f"\nFound {len(models)} model(s):\n")
            for name in sorted(models.keys()):
                model_class = models[name]
                field_count = len(model_class.model_fields)
                print(f"  {name} ({field_count} fields)")
            print()
        return
    
    # Field mapping mode
    if args.map_from and args.map_to:
        mappings = find_compatible_mappings(models, args.map_from, args.map_to)
        print_mapping_results(mappings, args.json)
        return
    
    # Search mode
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    results = search_fields(models, args.query, args.model)
    print_field_results(results, args.json)


if __name__ == '__main__':
    main()
