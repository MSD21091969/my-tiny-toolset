#!/usr/bin/env python3
r"""
Field Usage Analyzer

Analyze field usage patterns across models and methods to identify:
- Most/least used fields
- Unused fields (dead code)
- Frequently co-occurring fields
- Field coverage across methods

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Analyze all field usage
    python field_usage_analyzer.py --analyze
    
    # Find unused fields
    python field_usage_analyzer.py --unused
    
    # Field co-occurrence analysis
    python field_usage_analyzer.py --co-occurrence
    
    # Coverage report
    python field_usage_analyzer.py --coverage
    
    # Export analysis
    python field_usage_analyzer.py --analyze --export usage.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field as dc_field
from collections import Counter, defaultdict


@dataclass
class FieldUsage:
    """Field usage statistics."""
    field_name: str
    total_uses: int = 0
    input_uses: int = 0
    output_uses: int = 0
    methods: Set[str] = dc_field(default_factory=set)
    models: Set[str] = dc_field(default_factory=set)
    co_occurs_with: Counter = dc_field(default_factory=Counter)


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


def load_resources() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load method registry and model registry."""
    try:
        from pydantic_ai_integration.method_registry import MANAGED_METHODS
        from pydantic import BaseModel
        import src
        import inspect
        
        methods = dict(MANAGED_METHODS)
        
        # Load models
        models = {}
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
        
        return methods, models
    
    except ImportError as e:
        print(f"Error: Could not import resources: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_field_usage(methods: Dict[str, Any], models: Dict[str, Any]) -> Dict[str, FieldUsage]:
    """Analyze field usage across methods and models."""
    usage = {}
    
    # Analyze methods
    for method_name, method_def in methods.items():
        # Input fields
        if hasattr(method_def, 'request_model_class') and method_def.request_model_class:
            request_class = method_def.request_model_class
            model_name = request_class.__name__
            
            if hasattr(request_class, 'model_fields'):
                fields_in_model = list(request_class.model_fields.keys())
                
                for field_name in fields_in_model:
                    if field_name not in usage:
                        usage[field_name] = FieldUsage(field_name=field_name)
                    
                    usage[field_name].total_uses += 1
                    usage[field_name].input_uses += 1
                    usage[field_name].methods.add(method_name)
                    usage[field_name].models.add(model_name)
                    
                    # Track co-occurrence with other fields in same model
                    for other_field in fields_in_model:
                        if other_field != field_name:
                            usage[field_name].co_occurs_with[other_field] += 1
        
        # Output fields
        if hasattr(method_def, 'response_model_class') and method_def.response_model_class:
            response_class = method_def.response_model_class
            model_name = response_class.__name__
            
            if hasattr(response_class, 'model_fields'):
                fields_in_model = list(response_class.model_fields.keys())
                
                for field_name in fields_in_model:
                    if field_name not in usage:
                        usage[field_name] = FieldUsage(field_name=field_name)
                    
                    usage[field_name].total_uses += 1
                    usage[field_name].output_uses += 1
                    usage[field_name].methods.add(method_name)
                    usage[field_name].models.add(model_name)
                    
                    for other_field in fields_in_model:
                        if other_field != field_name:
                            usage[field_name].co_occurs_with[other_field] += 1
    
    # Check models for unused fields
    for model_name, model_class in models.items():
        if hasattr(model_class, 'model_fields'):
            for field_name in model_class.model_fields.keys():
                if field_name not in usage:
                    usage[field_name] = FieldUsage(field_name=field_name)
                    usage[field_name].models.add(model_name)
    
    return usage


def find_unused_fields(usage: Dict[str, FieldUsage]) -> List[Tuple[str, Set[str]]]:
    """Find fields that are never used in methods."""
    unused = []
    
    for field_name, stats in usage.items():
        if stats.total_uses == 0:
            unused.append((field_name, stats.models))
    
    return unused


def find_rarely_used_fields(usage: Dict[str, FieldUsage], threshold: int = 2) -> List[Tuple[str, int, Set[str]]]:
    """Find fields used less than threshold times."""
    rarely_used = []
    
    for field_name, stats in usage.items():
        if 0 < stats.total_uses < threshold:
            rarely_used.append((field_name, stats.total_uses, stats.methods))
    
    return sorted(rarely_used, key=lambda x: x[1])


def find_co_occurrence_patterns(usage: Dict[str, FieldUsage], min_count: int = 5) -> List[Tuple[str, str, int]]:
    """Find fields that frequently co-occur."""
    patterns = []
    seen = set()
    
    for field_name, stats in usage.items():
        for other_field, count in stats.co_occurs_with.most_common(10):
            if count >= min_count:
                pair = tuple(sorted([field_name, other_field]))
                if pair not in seen:
                    seen.add(pair)
                    patterns.append((field_name, other_field, count))
    
    return sorted(patterns, key=lambda x: x[2], reverse=True)


def calculate_coverage(usage: Dict[str, FieldUsage], total_methods: int) -> Dict[str, float]:
    """Calculate field coverage across methods."""
    coverage = {}
    
    for field_name, stats in usage.items():
        if stats.total_uses > 0:
            coverage[field_name] = len(stats.methods) / total_methods * 100
    
    return coverage


def print_analysis(usage: Dict[str, FieldUsage], total_methods: int):
    """Print comprehensive usage analysis."""
    print("\nField Usage Analysis")
    print("=" * 80)
    print(f"Total unique fields: {len(usage)}")
    print(f"Total methods analyzed: {total_methods}")
    print()
    
    # Top used fields
    top_fields = sorted(usage.items(), key=lambda x: x[1].total_uses, reverse=True)[:10]
    print("Top 10 Most Used Fields:")
    print("-" * 80)
    for field_name, stats in top_fields:
        print(f"{field_name:25} {stats.total_uses:3} uses ({stats.input_uses} input, {stats.output_uses} output)")
        print(f"{'':25} Methods: {len(stats.methods)}, Models: {len(stats.models)}")
    print()
    
    # Unused fields
    unused = find_unused_fields(usage)
    if unused:
        print(f"Unused Fields ({len(unused)}):")
        print("-" * 80)
        for field_name, models in unused[:10]:
            print(f"• {field_name} (in {', '.join(list(models)[:3])})")
        if len(unused) > 10:
            print(f"  ... and {len(unused) - 10} more")
        print()
    
    # Rarely used
    rarely_used = find_rarely_used_fields(usage, threshold=3)
    if rarely_used:
        print(f"Rarely Used Fields (<3 uses, {len(rarely_used)} total):")
        print("-" * 80)
        for field_name, count, methods in rarely_used[:10]:
            print(f"• {field_name} ({count} uses in {', '.join(list(methods))})")
        print()


def print_co_occurrence(usage: Dict[str, FieldUsage]):
    """Print co-occurrence patterns."""
    patterns = find_co_occurrence_patterns(usage, min_count=5)
    
    print("\nField Co-Occurrence Patterns")
    print("=" * 80)
    print(f"Found {len(patterns)} patterns (≥5 co-occurrences)")
    print()
    
    for field1, field2, count in patterns[:20]:
        print(f"{field1:20} ↔ {field2:20} ({count} times)")
    
    if len(patterns) > 20:
        print(f"\n... and {len(patterns) - 20} more patterns")
    print()


def print_coverage(usage: Dict[str, FieldUsage], total_methods: int):
    """Print coverage report."""
    coverage = calculate_coverage(usage, total_methods)
    
    print("\nField Coverage Report")
    print("=" * 80)
    print(f"Coverage = (methods using field) / (total methods) * 100%")
    print()
    
    # High coverage
    high_coverage = sorted([(f, c) for f, c in coverage.items() if c >= 50], key=lambda x: x[1], reverse=True)
    if high_coverage:
        print(f"High Coverage Fields (≥50%, {len(high_coverage)} fields):")
        print("-" * 80)
        for field, cov in high_coverage[:10]:
            print(f"{field:25} {cov:5.1f}% ({len(usage[field].methods)} methods)")
        print()
    
    # Low coverage
    low_coverage = sorted([(f, c) for f, c in coverage.items() if c < 10], key=lambda x: x[1])
    if low_coverage:
        print(f"Low Coverage Fields (<10%, {len(low_coverage)} fields):")
        print("-" * 80)
        for field, cov in low_coverage[:10]:
            print(f"{field:25} {cov:5.1f}% ({len(usage[field].methods)} methods)")
        print()


def export_analysis(usage: Dict[str, FieldUsage], filepath: Path):
    """Export analysis to JSON."""
    output = {
        'total_fields': len(usage),
        'fields': {
            field_name: {
                'total_uses': stats.total_uses,
                'input_uses': stats.input_uses,
                'output_uses': stats.output_uses,
                'methods': list(stats.methods),
                'models': list(stats.models),
                'top_co_occurrences': [
                    {'field': f, 'count': c}
                    for f, c in stats.co_occurs_with.most_common(5)
                ]
            }
            for field_name, stats in usage.items()
        }
    }
    
    filepath.write_text(json.dumps(output, indent=2))
    print(f"\nExported analysis to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze field usage patterns across models and methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--analyze', action='store_true', help='Run full usage analysis')
    parser.add_argument('--unused', action='store_true', help='Show unused fields only')
    parser.add_argument('--co-occurrence', action='store_true', help='Show co-occurrence patterns')
    parser.add_argument('--coverage', action='store_true', help='Show coverage report')
    parser.add_argument('--export', help='Export analysis to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    methods, models = load_resources()
    
    print(f"Loaded {len(methods)} methods and {len(models)} models")
    
    # Analyze
    usage = analyze_field_usage(methods, models)
    
    # Export
    if args.export:
        export_analysis(usage, Path(args.export))
        return
    
    # Output
    if args.unused:
        unused = find_unused_fields(usage)
        print(f"\nUnused Fields ({len(unused)}):")
        print("=" * 80)
        for field_name, models_set in unused:
            print(f"• {field_name}")
            print(f"  Models: {', '.join(models_set)}")
        return
    
    if args.co_occurrence:
        print_co_occurrence(usage)
        return
    
    if args.coverage:
        print_coverage(usage, len(methods))
        return
    
    if args.analyze or not any([args.unused, args.co_occurrence, args.coverage]):
        print_analysis(usage, len(methods))


if __name__ == '__main__':
    main()
