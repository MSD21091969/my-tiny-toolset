#!/usr/bin/env python3
r"""
Model Documentation Generator

Auto-generate comprehensive markdown documentation for Pydantic models.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Generate docs for all models
    python model_docs_generator.py --generate-all
    
    # Generate docs for specific model
    python model_docs_generator.py --model CreateCasefileRequest
    
    # Generate index page
    python model_docs_generator.py --index
    
    # Export to specific directory
    python model_docs_generator.py --generate-all --output docs/models/
    
    # Generate with examples
    python model_docs_generator.py --model CreateCasefileRequest --with-examples
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, get_origin, get_args
from dataclasses import dataclass
import inspect


@dataclass
class FieldInfo:
    """Field documentation info."""
    name: str
    type_str: str
    required: bool
    description: str = ""
    default: Any = None
    constraints: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


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
                
    except ImportError:
        print("Error: Could not import Pydantic", file=sys.stderr)
        sys.exit(1)
    
    return models


def get_package_name(model_class: Type) -> str:
    """Get package name for model."""
    module = model_class.__module__
    if 'pydantic_models.' in module:
        return module.split('pydantic_models.')[1].split('.')[0]
    return 'unknown'


def format_type_annotation(annotation: Any) -> str:
    """Format type annotation as readable string."""
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    
    origin = get_origin(annotation)
    args = get_args(annotation)
    
    if origin is None:
        return str(annotation)
    
    if origin is list or origin is List:
        if args:
            return f"List[{format_type_annotation(args[0])}]"
        return "List"
    
    if origin is dict or origin is Dict:
        if args and len(args) == 2:
            return f"Dict[{format_type_annotation(args[0])}, {format_type_annotation(args[1])}]"
        return "Dict"
    
    if origin is tuple:
        if args:
            arg_strs = [format_type_annotation(arg) for arg in args]
            return f"Tuple[{', '.join(arg_strs)}]"
        return "Tuple"
    
    # Handle Optional
    if len(args) == 2 and type(None) in args:
        non_none = args[0] if args[1] is type(None) else args[1]
        return f"Optional[{format_type_annotation(non_none)}]"
    
    return str(annotation)


def extract_field_info(model_class: Type) -> List[FieldInfo]:
    """Extract field information from model."""
    fields = []
    
    try:
        schema = model_class.model_json_schema()
        properties = schema.get('properties', {})
        required_fields = set(schema.get('required', []))
        
        # Get field info from model
        for field_name, field_obj in model_class.model_fields.items():
            prop_schema = properties.get(field_name, {})
            
            # Type
            type_str = format_type_annotation(field_obj.annotation)
            
            # Required
            is_required = field_name in required_fields
            
            # Description
            description = field_obj.description or prop_schema.get('description', '')
            
            # Default
            default_value = None
            if not is_required and field_obj.default is not None:
                default_value = field_obj.default
            elif not is_required and field_obj.default_factory is not None:
                default_value = "<factory>"
            
            # Constraints
            constraints = []
            if 'minLength' in prop_schema:
                constraints.append(f"min length: {prop_schema['minLength']}")
            if 'maxLength' in prop_schema:
                constraints.append(f"max length: {prop_schema['maxLength']}")
            if 'minimum' in prop_schema:
                constraints.append(f"minimum: {prop_schema['minimum']}")
            if 'maximum' in prop_schema:
                constraints.append(f"maximum: {prop_schema['maximum']}")
            if 'pattern' in prop_schema:
                constraints.append(f"pattern: `{prop_schema['pattern']}`")
            if 'format' in prop_schema:
                constraints.append(f"format: {prop_schema['format']}")
            
            fields.append(FieldInfo(
                name=field_name,
                type_str=type_str,
                required=is_required,
                description=description,
                default=default_value,
                constraints=constraints
            ))
    
    except Exception as e:
        print(f"Warning: Could not extract field info for {model_class.__name__}: {e}", file=sys.stderr)
    
    return fields


def generate_model_doc(model_name: str, model_class: Type, with_examples: bool = False) -> str:
    """Generate markdown documentation for a model."""
    package = get_package_name(model_class)
    fields = extract_field_info(model_class)
    
    # Header
    doc = f"# {model_name}\n\n"
    
    # Metadata
    doc += f"**Package:** `pydantic_models.{package}`\n\n"
    
    # Docstring
    if model_class.__doc__:
        doc += f"{model_class.__doc__.strip()}\n\n"
    
    doc += "---\n\n"
    
    # Fields table
    doc += "## Fields\n\n"
    doc += "| Field | Type | Required | Description |\n"
    doc += "|-------|------|----------|-------------|\n"
    
    for field in fields:
        required_marker = "✓" if field.required else ""
        description = field.description.replace('\n', ' ').strip()
        if not description:
            description = "-"
        
        doc += f"| `{field.name}` | {field.type_str} | {required_marker} | {description} |\n"
    
    doc += "\n"
    
    # Field details (if constraints or defaults)
    has_details = any(f.constraints or (not f.required and f.default is not None) for f in fields)
    if has_details:
        doc += "## Field Details\n\n"
        
        for field in fields:
            if field.constraints or (not field.required and field.default is not None):
                doc += f"### `{field.name}`\n\n"
                
                if field.constraints:
                    doc += "**Constraints:**\n"
                    for constraint in field.constraints:
                        doc += f"- {constraint}\n"
                    doc += "\n"
                
                if not field.required and field.default is not None:
                    doc += f"**Default:** `{field.default}`\n\n"
    
    # JSON Schema
    doc += "---\n\n"
    doc += "## JSON Schema\n\n"
    doc += "```json\n"
    try:
        schema = model_class.model_json_schema()
        doc += json.dumps(schema, indent=2)
    except Exception as e:
        doc += f"// Error generating schema: {e}\n"
    doc += "\n```\n\n"
    
    # Example
    if with_examples:
        doc += "---\n\n"
        doc += "## Example\n\n"
        doc += "```json\n"
        doc += "{\n"
        
        example_fields = []
        for field in fields:
            if field.required:
                if 'str' in field.type_str.lower():
                    example_fields.append(f'  "{field.name}": "example_value"')
                elif 'int' in field.type_str.lower():
                    example_fields.append(f'  "{field.name}": 0')
                elif 'bool' in field.type_str.lower():
                    example_fields.append(f'  "{field.name}": true')
                elif 'list' in field.type_str.lower():
                    example_fields.append(f'  "{field.name}": []')
                elif 'dict' in field.type_str.lower():
                    example_fields.append(f'  "{field.name}": {{}}')
                else:
                    example_fields.append(f'  "{field.name}": null')
        
        doc += ",\n".join(example_fields)
        doc += "\n}\n```\n\n"
    
    # Footer
    doc += "---\n\n"
    doc += f"*Generated by model_docs_generator.py*\n"
    
    return doc


def generate_index(models: Dict[str, Type]) -> str:
    """Generate index page for all models."""
    doc = "# Model Documentation Index\n\n"
    doc += f"**Total Models:** {len(models)}\n\n"
    doc += "---\n\n"
    
    # Group by package
    packages: Dict[str, List[str]] = {}
    for model_name, model_class in models.items():
        package = get_package_name(model_class)
        if package not in packages:
            packages[package] = []
        packages[package].append(model_name)
    
    for package in sorted(packages.keys()):
        doc += f"## Package: `pydantic_models.{package}`\n\n"
        
        for model_name in sorted(packages[package]):
            doc += f"- [{model_name}](./{model_name}.md)\n"
        
        doc += "\n"
    
    doc += "---\n\n"
    doc += f"*Generated by model_docs_generator.py*\n"
    
    return doc


def main():
    parser = argparse.ArgumentParser(
        description="Generate markdown documentation for Pydantic models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--generate-all', action='store_true', help='Generate docs for all models')
    parser.add_argument('--model', help='Generate docs for specific model')
    parser.add_argument('--index', action='store_true', help='Generate index page')
    parser.add_argument('--output', default='.tool-outputs/docs/', help='Output directory')
    parser.add_argument('--with-examples', action='store_true', help='Include example JSON')
    parser.add_argument('--stdout', action='store_true', help='Print to stdout instead of file')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    output_dir = Path(args.output)
    
    # Generate all
    if args.generate_all:
        if not args.stdout:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model_class in sorted(models.items()):
            doc = generate_model_doc(model_name, model_class, args.with_examples)
            
            if args.stdout:
                print(f"\n{'='*80}")
                print(f"MODEL: {model_name}")
                print('='*80)
                print(doc)
            else:
                filepath = output_dir / f"{model_name}.md"
                filepath.write_text(doc, encoding='utf-8')
        
        if not args.stdout:
            print(f"\nGenerated documentation for {len(models)} models in {output_dir}")
        
        # Generate index
        index_doc = generate_index(models)
        if args.stdout:
            print(f"\n{'='*80}")
            print("INDEX")
            print('='*80)
            print(index_doc)
        else:
            index_path = output_dir / "index.md"
            index_path.write_text(index_doc, encoding='utf-8')
            print(f"Generated index: {index_path}")
        
        return
    
    # Generate index only
    if args.index:
        doc = generate_index(models)
        
        if args.stdout:
            print(doc)
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            filepath = output_dir / "index.md"
            filepath.write_text(doc, encoding='utf-8')
            print(f"Generated index: {filepath}")
        
        return
    
    # Generate specific model
    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        doc = generate_model_doc(args.model, models[args.model], args.with_examples)
        
        if args.stdout:
            print(doc)
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            filepath = output_dir / f"{args.model}.md"
            filepath.write_text(doc, encoding='utf-8')
            print(f"Generated documentation: {filepath}")
        
        return
    
    # Default - show available models
    print(f"\n{len(models)} models available for documentation")
    print("\nPackage breakdown:")
    
    packages: Dict[str, int] = {}
    for model_name, model_class in models.items():
        package = get_package_name(model_class)
        packages[package] = packages.get(package, 0) + 1
    
    for package, count in sorted(packages.items()):
        print(f"  • pydantic_models.{package}: {count} models")
    
    print("\nUse --generate-all to generate docs for all models")
    print("Use --model <name> to generate docs for specific model")
    print("Use --index to generate index page")


if __name__ == '__main__':
    main()
