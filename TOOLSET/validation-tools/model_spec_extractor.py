"""
Model Specification Extractor

Extracts field specifications from Pydantic models and generates models_specification_v1.yaml.
Leverages existing model documentation to create versioned model spec contract.

Usage:
    python model_spec_extractor.py --output models_specification_v1.yaml
    python model_spec_extractor.py --json  # Output as JSON
    python model_spec_extractor.py --model CreateCasefileRequest  # Single model
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def setup_collider_path():
    """Add collider path to sys.path for imports."""
    collider_path = Path.cwd().parent / "my-tiny-data-collider"
    if not collider_path.exists():
        print(f"Error: Application repo not found at {collider_path}")
        print("Set COLLIDER_PATH environment variable or run from correct location")
        sys.exit(1)
    
    sys.path.insert(0, str(collider_path))
    return collider_path


def extract_field_spec(field_name: str, field_info: Any) -> Dict[str, Any]:
    """Extract field specification from Pydantic field info."""
    spec = {
        "name": field_name,
        "type": str(field_info.annotation).replace("typing.", ""),
        "required": field_info.is_required(),
    }
    
    # Add description if available
    if field_info.description:
        spec["description"] = field_info.description
    
    # Add default if not required
    if not field_info.is_required() and field_info.default is not None:
        try:
            spec["default"] = field_info.default
        except:
            spec["default"] = str(field_info.default)
    
    # Extract constraints from metadata
    constraints = {}
    if hasattr(field_info, 'metadata'):
        for metadata_item in field_info.metadata:
            if hasattr(metadata_item, 'ge'):
                constraints['min_value'] = metadata_item.ge
            if hasattr(metadata_item, 'le'):
                constraints['max_value'] = metadata_item.le
            if hasattr(metadata_item, 'min_length'):
                constraints['min_length'] = metadata_item.min_length
            if hasattr(metadata_item, 'max_length'):
                constraints['max_length'] = metadata_item.max_length
            if hasattr(metadata_item, 'pattern'):
                constraints['pattern'] = metadata_item.pattern
    
    if constraints:
        spec["constraints"] = constraints
    
    return spec


def extract_model_spec(model_class: Any) -> Dict[str, Any]:
    """Extract complete specification for a Pydantic model."""
    spec = {
        "model_name": model_class.__name__,
        "module": model_class.__module__,
        "fields": []
    }
    
    # Add docstring if available
    if model_class.__doc__:
        spec["description"] = model_class.__doc__.strip()
    
    # Extract field specifications
    for field_name, field_info in model_class.model_fields.items():
        field_spec = extract_field_spec(field_name, field_info)
        spec["fields"].append(field_spec)
    
    return spec


def get_method_models() -> Dict[str, Dict[str, str]]:
    """Get request/response models for all registered methods."""
    try:
        from src.methodregistryservice import MANAGED_METHODS
        
        method_models = {}
        for method_key, method_def in MANAGED_METHODS.items():
            method_name = method_def.method_name
            method_models[method_name] = {
                "request_model": method_def.request_model_class.__name__,
                "response_model": method_def.response_model_class.__name__,
                "request_class": method_def.request_model_class,
                "response_class": method_def.response_model_class,
            }
        
        return method_models
    except Exception as e:
        print(f"Warning: Could not load MANAGED_METHODS: {e}")
        return {}


def generate_models_specification(
    output_format: str = "yaml",
    specific_model: Optional[str] = None
) -> Dict[str, Any]:
    """Generate complete models specification document."""
    
    # Setup imports
    collider_path = setup_collider_path()
    
    # Get method models
    method_models = get_method_models()
    
    # Build specification
    spec = {
        "version": "1.0.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Code-fresh model specifications for all service methods",
        "methods": {}
    }
    
    # Extract specs for each method
    for method_name, models in method_models.items():
        method_spec = {
            "request_model": models["request_model"],
            "response_model": models["response_model"],
        }
        
        # Extract request fields
        if specific_model is None or specific_model == models["request_model"]:
            request_spec = extract_model_spec(models["request_class"])
            method_spec["request_fields"] = request_spec["fields"]
        
        # Extract response fields
        if specific_model is None or specific_model == models["response_model"]:
            response_spec = extract_model_spec(models["response_class"])
            method_spec["response_fields"] = response_spec["fields"]
        
        spec["methods"][method_name] = method_spec
    
    return spec


def main():
    parser = argparse.ArgumentParser(
        description="Extract field specifications from Pydantic models"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of YAML"
    )
    parser.add_argument(
        "--model",
        help="Extract specific model only"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate specification
        spec = generate_models_specification(
            output_format="json" if args.json else "yaml",
            specific_model=args.model
        )
        
        # Format output
        if args.json:
            output = json.dumps(spec, indent=2)
        else:
            output = yaml.dump(spec, sort_keys=False, allow_unicode=True)
        
        # Write or print
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output)
            print(f"✓ Model specification written to {output_path}")
            print(f"  Methods: {len(spec['methods'])}")
            print(f"  Version: {spec['version']}")
            print(f"  Date: {spec['date']}")
        else:
            print(output)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
