#!/usr/bin/env python3
r"""
Response Model Variation Analyzer

Analyze response models and suggest variations for different use cases (success, error, partial, etc.).

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Analyze all response models
    python response_variations.py --analyze
    
    # Suggest variations for specific model
    python response_variations.py --model CreateCasefileResponse --suggest
    
    # Check coverage (models with/without variations)
    python response_variations.py --coverage
    
    # Generate variation templates
    python response_variations.py --model CreateCasefileResponse --generate-templates
    
    # Export analysis
    python response_variations.py --export variations.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Set
from dataclasses import dataclass, field as dc_field
import inspect


@dataclass
class ResponseVariation:
    """Suggested response variation."""
    base_model: str
    variation_name: str
    use_case: str
    fields_to_add: List[str] = dc_field(default_factory=list)
    fields_to_remove: List[str] = dc_field(default_factory=list)
    fields_to_make_optional: List[str] = dc_field(default_factory=list)
    description: str = ""


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


def get_response_models(models: Dict[str, Type]) -> Dict[str, Type]:
    """Filter for response models only."""
    return {name: model for name, model in models.items() if 'Response' in name}


def has_variations(model_name: str, models: Dict[str, Type]) -> List[str]:
    """Check if model has existing variations."""
    base_name = model_name.replace('Response', '')
    variations = []
    
    for name in models.keys():
        if name.startswith(base_name) and name != model_name and 'Response' in name:
            variations.append(name)
    
    return variations


def suggest_variations(model_name: str, model_class: Type) -> List[ResponseVariation]:
    """Suggest response variations for a model."""
    variations = []
    base_name = model_name.replace('Response', '')
    
    # Get model fields
    fields = list(model_class.model_fields.keys())
    required_fields = [f for f, info in model_class.model_fields.items() if info.is_required()]
    optional_fields = [f for f, info in model_class.model_fields.items() if not info.is_required()]
    
    # Standard variations to suggest
    
    # 1. Summary/List variant (minimal fields for list views)
    if len(fields) > 4:
        summary_fields = []
        if 'payload' in fields:
            summary_fields.append('payload')
        variations.append(ResponseVariation(
            base_model=model_name,
            variation_name=f"{base_name}SummaryResponse",
            use_case="List views, bulk operations",
            fields_to_remove=[f for f in fields if f not in ['request_id', 'timestamp', 'status', 'payload']],
            description="Lightweight version for list endpoints"
        ))
    
    # 2. Detailed variant (includes extra metadata)
    if 'metadata' in fields or len(optional_fields) > 2:
        variations.append(ResponseVariation(
            base_model=model_name,
            variation_name=f"{base_name}DetailedResponse",
            use_case="Single resource GET, detailed views",
            fields_to_add=['execution_time_ms', 'cache_status', 'api_version'],
            description="Extended version with performance and system metadata"
        ))
    
    # 3. Error variant
    variations.append(ResponseVariation(
        base_model=model_name,
        variation_name=f"{base_name}ErrorResponse",
        use_case="Error handling",
        fields_to_add=['error_code', 'error_details', 'retry_after'],
        fields_to_make_optional=['payload'],
        description="Error-specific response with debugging information"
    ))
    
    # 4. Async/Pending variant (for long-running operations)
    if 'casefile' in base_name.lower() or 'session' in base_name.lower():
        variations.append(ResponseVariation(
            base_model=model_name,
            variation_name=f"{base_name}PendingResponse",
            use_case="Async operations",
            fields_to_add=['job_id', 'status_url', 'estimated_completion'],
            fields_to_make_optional=['payload'],
            description="Response for operations that complete asynchronously"
        ))
    
    # 5. Partial variant (for partial success scenarios)
    if 'batch' in base_name.lower() or 'bulk' in base_name.lower() or 'list' in base_name.lower():
        variations.append(ResponseVariation(
            base_model=model_name,
            variation_name=f"{base_name}PartialResponse",
            use_case="Partial success in batch operations",
            fields_to_add=['succeeded_items', 'failed_items', 'partial_errors'],
            description="Response when some items succeed and others fail"
        ))
    
    return variations


def analyze_response_coverage(models: Dict[str, Type]) -> Dict[str, Any]:
    """Analyze response model variation coverage."""
    response_models = get_response_models(models)
    
    analysis = {
        'summary': {
            'total_response_models': len(response_models),
            'with_variations': 0,
            'without_variations': 0,
            'suggested_variations': 0
        },
        'by_model': {},
        'recommendations': []
    }
    
    for model_name, model_class in sorted(response_models.items()):
        existing_variations = has_variations(model_name, models)
        suggested = suggest_variations(model_name, model_class)
        
        has_vars = len(existing_variations) > 0
        if has_vars:
            analysis['summary']['with_variations'] += 1
        else:
            analysis['summary']['without_variations'] += 1
        
        analysis['summary']['suggested_variations'] += len(suggested)
        
        analysis['by_model'][model_name] = {
            'existing_variations': existing_variations,
            'suggested_variations': [
                {
                    'name': v.variation_name,
                    'use_case': v.use_case,
                    'description': v.description
                }
                for v in suggested
            ]
        }
        
        # Add recommendations for models without variations
        if not has_vars and len(suggested) > 0:
            analysis['recommendations'].append({
                'model': model_name,
                'priority': 'high' if len(model_class.model_fields) > 5 else 'medium',
                'suggested_count': len(suggested),
                'top_suggestion': suggested[0].variation_name if suggested else None
            })
    
    return analysis


def generate_variation_template(model_name: str, variation: ResponseVariation) -> str:
    """Generate Python code template for a response variation."""
    template = f'''
from pydantic import BaseModel, Field
from typing import Optional
from .{model_name.lower().replace('response', '')} import {model_name}

class {variation.variation_name}(BaseModel):
    """
    {variation.description}
    
    Use case: {variation.use_case}
    """
'''
    
    # Add field examples
    if variation.fields_to_add:
        template += "\n    # Additional fields for this variation\n"
        for field in variation.fields_to_add:
            template += f'    {field}: Optional[str] = Field(None, description="TODO: Add description")\n'
    
    if variation.fields_to_make_optional:
        template += "\n    # Fields made optional in this variation\n"
        for field in variation.fields_to_make_optional:
            template += f"    # {field}: Optional[...] = None\n"
    
    template += "\n    # Inherit other fields from " + model_name + "\n"
    
    return template


def print_analysis(analysis: Dict[str, Any]):
    """Print analysis in human-readable format."""
    print("\nResponse Model Variation Analysis")
    print("=" * 80)
    
    summary = analysis['summary']
    print(f"\nSummary:")
    print(f"  Total response models: {summary['total_response_models']}")
    print(f"  With variations: {summary['with_variations']}")
    print(f"  Without variations: {summary['without_variations']}")
    print(f"  Suggested new variations: {summary['suggested_variations']}")
    
    coverage = summary['with_variations'] / summary['total_response_models'] * 100 if summary['total_response_models'] > 0 else 0
    print(f"  Coverage: {coverage:.1f}%")
    
    if analysis['recommendations']:
        print(f"\nTop Recommendations ({len(analysis['recommendations'])} models):")
        for rec in analysis['recommendations'][:5]:
            print(f"  • {rec['model']} ({rec['priority']} priority)")
            print(f"    → Suggest {rec['suggested_count']} variation(s), starting with {rec['top_suggestion']}")
    
    print("\n" + "=" * 80 + "\n")


def print_suggestions(model_name: str, variations: List[ResponseVariation], detailed: bool = False):
    """Print suggested variations for a model."""
    print(f"\nSuggested variations for {model_name}:\n")
    print("=" * 80)
    
    for i, var in enumerate(variations, 1):
        print(f"\n{i}. {var.variation_name}")
        print(f"   Use case: {var.use_case}")
        print(f"   Description: {var.description}")
        
        if detailed:
            if var.fields_to_add:
                print(f"   Fields to add: {', '.join(var.fields_to_add)}")
            if var.fields_to_remove:
                print(f"   Fields to remove: {', '.join(var.fields_to_remove)}")
            if var.fields_to_make_optional:
                print(f"   Fields to make optional: {', '.join(var.fields_to_make_optional)}")
    
    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and suggest response model variations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--analyze', action='store_true', help='Analyze all response models')
    parser.add_argument('--coverage', action='store_true', help='Show variation coverage')
    parser.add_argument('--model', help='Analyze specific model')
    parser.add_argument('--suggest', action='store_true', help='Suggest variations for model')
    parser.add_argument('--template', choices=['summary', 'detailed', 'error', 'pending', 'partial'], help='Generate specific template type')
    parser.add_argument('--generate-templates', action='store_true', help='Generate all code templates')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--export', help='Export analysis to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    models = load_pydantic_models()
    
    if not models:
        print("Error: No models found", file=sys.stderr)
        sys.exit(1)
    
    # Analyze all
    if args.analyze or args.coverage:
        analysis = analyze_response_coverage(models)
        
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            print_analysis(analysis)
        return
    
    # Export
    if args.export:
        analysis = analyze_response_coverage(models)
        export_path = Path(args.export)
        export_path.write_text(json.dumps(analysis, indent=2))
        print(f"Exported analysis to {export_path}")
        return
    
    # Specific model
    if args.model:
        if args.model not in models:
            print(f"Error: Model '{args.model}' not found", file=sys.stderr)
            sys.exit(1)
        
        variations = suggest_variations(args.model, models[args.model])
        
        # Generate specific template type
        if args.template:
            template_map = {
                'summary': 'summary',
                'detailed': 'detailed',
                'error': 'error',
                'pending': 'pending',
                'partial': 'partial'
            }
            var_type = template_map[args.template]
            matching = [v for v in variations if var_type.lower() in v.variation_name.lower()]
            if matching:
                print(generate_variation_template(args.model, matching[0]))
            else:
                print(f"No {var_type} variation found for {args.model}", file=sys.stderr)
            return
        
        # Generate all templates
        if args.generate_templates:
            for var in variations:
                print(generate_variation_template(args.model, var))
                print("\n" + "-" * 80 + "\n")
        elif args.json:
            output = [
                {
                    'name': v.variation_name,
                    'use_case': v.use_case,
                    'description': v.description,
                    'fields_to_add': v.fields_to_add,
                    'fields_to_remove': v.fields_to_remove,
                    'fields_to_make_optional': v.fields_to_make_optional
                }
                for v in variations
            ]
            print(json.dumps(output, indent=2))
        else:
            print_suggestions(args.model, variations, args.detailed)
        return
    
    # Default - show coverage
    analysis = analyze_response_coverage(models)
    
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print_analysis(analysis)


if __name__ == '__main__':
    main()
