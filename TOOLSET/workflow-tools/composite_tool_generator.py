#!/usr/bin/env python3
r"""
Composite Tool Generator

Generate composite tool YAMLs that chain multiple methods together into workflows.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Generate composite tool from method sequence
    python composite_tool_generator.py create_casefile grant_permission --name "Create and Share Casefile"
    
    # Validate composite tool
    python composite_tool_generator.py create_casefile list_casefiles --validate
    
    # Generate with field mapping
    python composite_tool_generator.py create_casefile update_casefile --auto-map
    
    # Output to file
    python composite_tool_generator.py method1 method2 method3 --output composite_workflow.yaml
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field as dc_field


@dataclass
class FieldMapping:
    """Field mapping between methods."""
    source_method: str
    source_field: str
    target_method: str
    target_field: str
    compatible: bool = True
    reason: str = ""


@dataclass
class CompositeStep:
    """Step in composite workflow."""
    method_name: str
    description: str
    input_mappings: List[FieldMapping] = dc_field(default_factory=list)
    output_fields: List[str] = dc_field(default_factory=list)


@dataclass
class CompositeTool:
    """Composite tool definition."""
    name: str
    description: str
    steps: List[CompositeStep]
    parameters: Dict[str, Any] = dc_field(default_factory=dict)
    returns: Dict[str, Any] = dc_field(default_factory=dict)


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
        
        # Trigger imports to populate registry
        import src
        
        return dict(MANAGED_METHODS)
    except ImportError as e:
        print(f"Error: Could not import MANAGED_METHODS: {e}", file=sys.stderr)
        sys.exit(1)


def get_method_fields(method_def: Any) -> tuple[List[str], List[str]]:
    """Extract input/output fields from method definition."""
    input_fields = []
    output_fields = []
    
    try:
        # Input fields from request model
        if hasattr(method_def, 'request_model_class') and method_def.request_model_class:
            request_class = method_def.request_model_class
            if hasattr(request_class, 'model_fields'):
                input_fields = list(request_class.model_fields.keys())
        
        # Output fields from response model
        if hasattr(method_def, 'response_model_class') and method_def.response_model_class:
            response_class = method_def.response_model_class
            if hasattr(response_class, 'model_fields'):
                output_fields = list(response_class.model_fields.keys())
    
    except Exception as e:
        print(f"Warning: Could not extract fields: {e}", file=sys.stderr)
    
    return input_fields, output_fields


def find_field_mappings(source_method: str, target_method: str, registry: Dict[str, Any]) -> List[FieldMapping]:
    """Find compatible field mappings between two methods."""
    mappings = []
    
    if source_method not in registry or target_method not in registry:
        return mappings
    
    source_def = registry[source_method]
    target_def = registry[target_method]
    
    _, source_outputs = get_method_fields(source_def)
    target_inputs, _ = get_method_fields(target_def)
    
    # Find matching fields
    for out_field in source_outputs:
        for in_field in target_inputs:
            # Exact match
            if out_field == in_field:
                mappings.append(FieldMapping(
                    source_method=source_method,
                    source_field=out_field,
                    target_method=target_method,
                    target_field=in_field,
                    compatible=True,
                    reason="Exact field name match"
                ))
            # Semantic match (e.g., casefile_id matches id)
            elif 'id' in out_field.lower() and 'id' in in_field.lower():
                mappings.append(FieldMapping(
                    source_method=source_method,
                    source_field=out_field,
                    target_method=target_method,
                    target_field=in_field,
                    compatible=True,
                    reason="ID field semantic match"
                ))
    
    return mappings


def generate_composite_tool(method_names: List[str], registry: Dict[str, Any], 
                           tool_name: Optional[str] = None,
                           auto_map: bool = False) -> CompositeTool:
    """Generate composite tool from method sequence."""
    
    # Validate methods exist
    for method in method_names:
        if method not in registry:
            print(f"Error: Method '{method}' not found in registry", file=sys.stderr)
            sys.exit(1)
    
    # Generate name
    if not tool_name:
        tool_name = "_".join(method_names) + "_workflow"
    
    # Generate description
    descriptions = []
    for method in method_names:
        method_def = registry[method]
        if hasattr(method_def, 'description'):
            descriptions.append(method_def.description or method)
        else:
            descriptions.append(method)
    
    tool_description = f"Composite workflow: {' → '.join(descriptions)}"
    
    # Build steps
    steps = []
    for i, method_name in enumerate(method_names):
        method_def = registry[method_name]
        
        # Get description
        step_desc = getattr(method_def, 'description', method_name)
        
        # Get fields
        input_fields, output_fields = get_method_fields(method_def)
        
        # Find mappings from previous step
        mappings = []
        if i > 0 and auto_map:
            prev_method = method_names[i-1]
            mappings = find_field_mappings(prev_method, method_name, registry)
        
        steps.append(CompositeStep(
            method_name=method_name,
            description=step_desc,
            input_mappings=mappings,
            output_fields=output_fields
        ))
    
    # Collect parameters (from first method)
    parameters = {}
    if steps:
        first_inputs, _ = get_method_fields(registry[method_names[0]])
        for field in first_inputs:
            parameters[field] = {
                'type': 'string',
                'description': f'Input parameter: {field}'
            }
    
    # Collect returns (from last method)
    returns = {}
    if steps:
        _, last_outputs = get_method_fields(registry[method_names[-1]])
        for field in last_outputs:
            returns[field] = {
                'type': 'string',
                'description': f'Output field: {field}'
            }
    
    return CompositeTool(
        name=tool_name,
        description=tool_description,
        steps=steps,
        parameters=parameters,
        returns=returns
    )


def validate_composite_tool(composite: CompositeTool, registry: Dict[str, Any]) -> List[str]:
    """Validate composite tool for issues."""
    issues = []
    
    # Check each step transition
    for i in range(len(composite.steps) - 1):
        current_step = composite.steps[i]
        next_step = composite.steps[i + 1]
        
        # Get output fields from current, input fields from next
        _, current_outputs = get_method_fields(registry[current_step.method_name])
        next_inputs, _ = get_method_fields(registry[next_step.method_name])
        
        # Check if any fields can map
        if not current_step.input_mappings:
            has_mapping = False
            for out_field in current_outputs:
                if out_field in next_inputs:
                    has_mapping = True
                    break
            
            if not has_mapping:
                issues.append(f"No field mappings found between {current_step.method_name} → {next_step.method_name}")
    
    # Check for required fields
    for step in composite.steps:
        method_def = registry[step.method_name]
        if hasattr(method_def, 'request_model_class') and method_def.request_model_class:
            try:
                schema = method_def.request_model_class.model_json_schema()
                required = schema.get('required', [])
                
                if required and not step.input_mappings:
                    issues.append(f"{step.method_name} has required fields {required} but no input mappings")
            except:
                pass
    
    return issues


def export_to_yaml(composite: CompositeTool) -> str:
    """Export composite tool to YAML format."""
    
    # Build YAML structure
    yaml_data = {
        'name': composite.name,
        'description': composite.description,
        'type': 'composite',
        'steps': []
    }
    
    for i, step in enumerate(composite.steps, 1):
        step_data = {
            'step': i,
            'method': step.method_name,
            'description': step.description
        }
        
        if step.input_mappings:
            step_data['mappings'] = [
                {
                    'from': f'{m.source_method}.{m.source_field}',
                    'to': m.target_field,
                    'compatible': m.compatible
                }
                for m in step.input_mappings
            ]
        
        if step.output_fields:
            step_data['outputs'] = step.output_fields
        
        yaml_data['steps'].append(step_data)
    
    if composite.parameters:
        yaml_data['parameters'] = composite.parameters
    
    if composite.returns:
        yaml_data['returns'] = composite.returns
    
    return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)


def print_composite(composite: CompositeTool, detailed: bool = False):
    """Print composite tool information."""
    print(f"\nComposite Tool: {composite.name}")
    print("=" * 80)
    print(f"Description: {composite.description}")
    print(f"Steps: {len(composite.steps)}")
    print()
    
    for i, step in enumerate(composite.steps, 1):
        print(f"{i}. {step.method_name}")
        print(f"   {step.description}")
        
        if step.input_mappings:
            print(f"   Input mappings: {len(step.input_mappings)}")
            if detailed:
                for mapping in step.input_mappings:
                    status = "✓" if mapping.compatible else "❌"
                    print(f"     {status} {mapping.source_field} → {mapping.target_field} ({mapping.reason})")
        
        if step.output_fields:
            print(f"   Output fields: {', '.join(step.output_fields[:5])}")
            if len(step.output_fields) > 5:
                print(f"                  ... and {len(step.output_fields) - 5} more")
        
        print()
    
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Generate composite tool YAMLs from method sequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('methods', nargs='+', help='Method names in sequence')
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--name', help='Name for composite tool')
    parser.add_argument('--auto-map', action='store_true', help='Automatically map fields between steps')
    parser.add_argument('--validate', action='store_true', help='Validate composite tool')
    parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    parser.add_argument('--output', help='Output YAML file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    registry = load_method_registry()
    
    if not registry:
        print("Error: No methods found in registry", file=sys.stderr)
        sys.exit(1)
    
    # Generate composite tool
    composite = generate_composite_tool(args.methods, registry, args.name, args.auto_map)
    
    # Validate
    if args.validate:
        issues = validate_composite_tool(composite, registry)
        
        if issues:
            print("\nValidation Issues:")
            print("-" * 80)
            for issue in issues:
                print(f"  ❌ {issue}")
            print()
        else:
            print("\n✓ Composite tool validation passed\n")
    
    # Output
    if args.output:
        yaml_content = export_to_yaml(composite)
        output_path = Path(args.output)
        output_path.write_text(yaml_content)
        print(f"\nExported composite tool to {output_path}")
    elif args.json:
        output = {
            'name': composite.name,
            'description': composite.description,
            'steps': [
                {
                    'method': step.method_name,
                    'description': step.description,
                    'mappings': [
                        {
                            'source_field': m.source_field,
                            'target_field': m.target_field,
                            'compatible': m.compatible
                        }
                        for m in step.input_mappings
                    ],
                    'output_fields': step.output_fields
                }
                for step in composite.steps
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print_composite(composite, args.detailed)
        
        if not args.validate:
            print("\nUse --validate to check for issues")
            print("Use --output <file> to export YAML")


if __name__ == '__main__':
    main()
