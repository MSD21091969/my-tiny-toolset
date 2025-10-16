#!/usr/bin/env python3
r"""
JSON Schema Validation Tester

Validate that Pydantic models generate correct JSON schemas and can deserialize from their own schemas.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Test all models
    python schema_validator.py --test-all
    
    # Test specific model
    python schema_validator.py --model CreateCasefileRequest
    
    # Run with examples
    python schema_validator.py --test-all --with-examples
    
    # Export test results
    python schema_validator.py --test-all --export results.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field as dc_field
import inspect


@dataclass
class SchemaTest:
    """Schema validation test result."""
    model_name: str
    passed: bool
    schema_valid: bool = False
    example_valid: bool = False
    roundtrip_valid: bool = False
    errors: List[str] = dc_field(default_factory=list)
    warnings: List[str] = dc_field(default_factory=list)


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


def validate_schema_structure(model_name: str, model_class: Type) -> SchemaTest:
    """Validate that model generates valid JSON schema."""
    result = SchemaTest(model_name=model_name, passed=False)
    
    try:
        # Get schema
        schema = model_class.model_json_schema()
        
        # Check required fields
        if 'type' not in schema:
            result.errors.append("Missing 'type' in schema")
        elif schema['type'] != 'object':
            result.warnings.append(f"Schema type is '{schema['type']}', expected 'object'")
        
        if 'properties' not in schema:
            result.errors.append("Missing 'properties' in schema")
        else:
            # Check property structure
            for prop_name, prop_schema in schema['properties'].items():
                if 'type' not in prop_schema and '$ref' not in prop_schema and 'anyOf' not in prop_schema and 'allOf' not in prop_schema:
                    result.warnings.append(f"Property '{prop_name}' missing type information")
        
        # Check for examples
        if 'examples' in schema:
            result.warnings.append("Schema has examples at root level")
        
        result.schema_valid = len(result.errors) == 0
        
    except Exception as e:
        result.errors.append(f"Schema generation failed: {str(e)}")
    
    return result


def validate_example_roundtrip(model_name: str, model_class: Type, test_examples: bool = False) -> SchemaTest:
    """Validate model can serialize/deserialize correctly."""
    result = SchemaTest(model_name=model_name, passed=False)
    
    try:
        schema = model_class.model_json_schema()
        result.schema_valid = True
        
        # Check if model has example data
        if test_examples:
            # Try to create instance with minimal data
            try:
                # Get required fields
                required = schema.get('required', [])
                properties = schema.get('properties', {})
                
                # Build minimal example
                example_data = {}
                for field in required:
                    prop = properties.get(field, {})
                    prop_type = prop.get('type', 'string')
                    
                    if prop_type == 'string':
                        example_data[field] = 'test_value'
                    elif prop_type == 'integer':
                        example_data[field] = 0
                    elif prop_type == 'number':
                        example_data[field] = 0.0
                    elif prop_type == 'boolean':
                        example_data[field] = True
                    elif prop_type == 'array':
                        example_data[field] = []
                    elif prop_type == 'object':
                        example_data[field] = {}
                
                # Try roundtrip
                instance = model_class(**example_data)
                json_str = instance.model_dump_json()
                parsed = json.loads(json_str)
                reconstructed = model_class(**parsed)
                
                result.example_valid = True
                result.roundtrip_valid = True
                
            except Exception as e:
                result.errors.append(f"Example roundtrip failed: {str(e)}")
        else:
            result.example_valid = True
            result.roundtrip_valid = True
        
        result.passed = result.schema_valid and result.roundtrip_valid
        
    except Exception as e:
        result.errors.append(f"Validation failed: {str(e)}")
    
    return result


def test_model(model_name: str, model_class: Type, with_examples: bool = False) -> SchemaTest:
    """Run all validation tests on a model."""
    # Schema structure test
    structure_result = validate_schema_structure(model_name, model_class)
    
    # Roundtrip test
    roundtrip_result = validate_example_roundtrip(model_name, model_class, with_examples)
    
    # Merge results
    result = SchemaTest(
        model_name=model_name,
        passed=structure_result.schema_valid and roundtrip_result.roundtrip_valid,
        schema_valid=structure_result.schema_valid,
        example_valid=roundtrip_result.example_valid,
        roundtrip_valid=roundtrip_result.roundtrip_valid,
        errors=structure_result.errors + roundtrip_result.errors,
        warnings=structure_result.warnings + roundtrip_result.warnings
    )
    
    return result


def test_all_models(models: Dict[str, Type], with_examples: bool = False) -> List[SchemaTest]:
    """Test all models."""
    results = []
    
    for model_name, model_class in sorted(models.items()):
        result = test_model(model_name, model_class, with_examples)
        results.append(result)
    
    return results


def print_results(results: List[SchemaTest], detailed: bool = False):
    """Print test results."""
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    
    print("\nJSON Schema Validation Results")
    print("=" * 80)
    print(f"\nTotal models: {len(results)}")
    print(f"Passed: {len(passed)} ({len(passed)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    if failed:
        print(f"\nFailed Models ({len(failed)}):")
        print("-" * 80)
        for result in failed:
            print(f"\n❌ {result.model_name}")
            print(f"   Schema valid: {result.schema_valid}")
            print(f"   Example valid: {result.example_valid}")
            print(f"   Roundtrip valid: {result.roundtrip_valid}")
            
            if result.errors:
                for error in result.errors:
                    print(f"   ERROR: {error}")
            
            if result.warnings and detailed:
                for warning in result.warnings:
                    print(f"   WARNING: {warning}")
    
    if detailed and passed:
        print(f"\n✓ Passed Models ({len(passed)}):")
        for result in passed:
            status = "✓"
            if result.warnings:
                status = "⚠"
            print(f"  {status} {result.model_name}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"     WARNING: {warning}")
    
    print("\n" + "=" * 80)


def export_results(results: List[SchemaTest], filepath: Path):
    """Export results to JSON."""
    output = {
        'total': len(results),
        'passed': len([r for r in results if r.passed]),
        'failed': len([r for r in results if not r.passed]),
        'results': [
            {
                'model': r.model_name,
                'passed': r.passed,
                'schema_valid': r.schema_valid,
                'example_valid': r.example_valid,
                'roundtrip_valid': r.roundtrip_valid,
                'errors': r.errors,
                'warnings': r.warnings
            }
            for r in results
        ]
    }
    
    filepath.write_text(json.dumps(output, indent=2))
    print(f"\nExported results to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSON schemas for Pydantic models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--test-all', action='store_true', help='Test all models')
    parser.add_argument('--model', help='Test specific model')
    parser.add_argument('--with-examples', action='store_true', help='Test with example data generation')
    parser.add_argument('--detailed', action='store_true', help='Show detailed output including warnings')
    parser.add_argument('--export', help='Export results to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    # Test all
    if args.test_all:
        results = test_all_models(models, args.with_examples)
        
        if args.export:
            export_results(results, Path(args.export))
        
        if args.json:
            output = {
                'total': len(results),
                'passed': len([r for r in results if r.passed]),
                'failed': len([r for r in results if not r.passed]),
                'results': [
                    {
                        'model': r.model_name,
                        'passed': r.passed,
                        'schema_valid': r.schema_valid,
                        'errors': r.errors,
                        'warnings': r.warnings
                    }
                    for r in results
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            print_results(results, args.detailed)
        
        sys.exit(0 if all(r.passed for r in results) else 1)
    
    # Test specific model
    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        result = test_model(args.model, models[args.model], args.with_examples)
        
        if args.json:
            output = {
                'model': result.model_name,
                'passed': result.passed,
                'schema_valid': result.schema_valid,
                'example_valid': result.example_valid,
                'roundtrip_valid': result.roundtrip_valid,
                'errors': result.errors,
                'warnings': result.warnings
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nValidation Results for {args.model}")
            print("=" * 80)
            print(f"Status: {'✓ PASS' if result.passed else '❌ FAIL'}")
            print(f"Schema valid: {result.schema_valid}")
            print(f"Example valid: {result.example_valid}")
            print(f"Roundtrip valid: {result.roundtrip_valid}")
            
            if result.errors:
                print("\nErrors:")
                for error in result.errors:
                    print(f"  • {error}")
            
            if result.warnings:
                print("\nWarnings:")
                for warning in result.warnings:
                    print(f"  • {warning}")
            
            print("=" * 80)
        
        sys.exit(0 if result.passed else 1)
    
    # Default - show help
    print(f"\n{len(models)} models available for testing")
    print("\nUse --test-all to test all models or --model <name> to test specific model")
    parser.print_help()


if __name__ == '__main__':
    main()
