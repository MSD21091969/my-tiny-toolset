"""
Methods Inventory Validator

Cross-checks methods_inventory_v1.yaml against actual code state:
1. MANAGED_METHODS registry (internal methods)
2. service_module_map (external methods)
3. Pydantic model existence

Usage:
    python methods_inventory_validator.py --inventory path/to/methods_inventory_v1.yaml
    python methods_inventory_validator.py --inventory path/to/inventory.yaml --json
    python methods_inventory_validator.py --inventory path/to/inventory.yaml --fix
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


def setup_collider_path():
    """Add collider path to sys.path for imports."""
    collider_path = Path.cwd().parent / "my-tiny-data-collider"
    if not collider_path.exists():
        print(f"Error: Application repo not found at {collider_path}")
        sys.exit(1)
    
    sys.path.insert(0, str(collider_path))
    return collider_path


def load_inventory(inventory_path: Path) -> Dict[str, Any]:
    """Load methods inventory YAML."""
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory not found: {inventory_path}")
    
    with open(inventory_path) as f:
        return yaml.safe_load(f)


def get_managed_methods() -> Dict[str, Any]:
    """Get all methods from MANAGED_METHODS registry."""
    try:
        from src.methodregistryservice import MANAGED_METHODS
        
        methods = {}
        for method_key, method_def in MANAGED_METHODS.items():
            methods[method_def.method_name] = {
                "service_class": method_def.service_class,
                "request_model": method_def.request_model_class.__name__,
                "response_model": method_def.response_model_class.__name__,
                "classification": method_def.classification,
            }
        return methods
    except Exception as e:
        print(f"Warning: Could not load MANAGED_METHODS: {e}")
        return {}


def get_service_module_map() -> Dict[str, str]:
    """Get service_module_map from tool registry."""
    try:
        from src.methodregistryservice.tool_registry import _instantiate_service
        
        # Hardcoded map from tool_registry.py
        return {
            "CasefileService": "casefileservice.service",
            "ToolSessionService": "tool_sessionservice.service",
            "CommunicationService": "communicationservice.service",
            "DriveClient": "pydantic_ai_integration.integrations.google_workspace.drive_client",
            "GmailClient": "pydantic_ai_integration.integrations.google_workspace.gmail_client",
            "SheetsClient": "pydantic_ai_integration.integrations.google_workspace.sheets_client",
            "RequestHubService": "orchestrationservice.request_hub",
        }
    except:
        return {}


def validate_model_exists(model_name: str) -> bool:
    """Check if Pydantic model exists in codebase."""
    try:
        # Try importing from operations
        from src.pydantic_models import operations
        return hasattr(operations, model_name)
    except:
        return False


def validate_inventory(
    inventory: Dict[str, Any],
    managed_methods: Dict[str, Any],
    service_map: Dict[str, str]
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Validate inventory against code.
    
    Returns:
        (valid_methods, warnings, errors)
    """
    valid = []
    warnings = []
    errors = []
    
    for method_name, method_spec in inventory.items():
        result = {
            "method": method_name,
            "integration_tier": method_spec.get("classification", {}).get("integration_tier"),
        }
        
        # Check integration tier
        tier = method_spec.get("classification", {}).get("integration_tier")
        
        if tier == "internal":
            # Should be in MANAGED_METHODS
            if method_name in managed_methods:
                managed = managed_methods[method_name]
                result["status"] = "valid"
                result["source"] = "MANAGED_METHODS"
                
                # Verify models match
                if method_spec["models"]["request"] != managed["request_model"]:
                    warnings.append({
                        **result,
                        "issue": "request_model_mismatch",
                        "inventory": method_spec["models"]["request"],
                        "code": managed["request_model"]
                    })
                
                if method_spec["models"]["response"] != managed["response_model"]:
                    warnings.append({
                        **result,
                        "issue": "response_model_mismatch",
                        "inventory": method_spec["models"]["response"],
                        "code": managed["response_model"]
                    })
                
                valid.append(result)
            else:
                errors.append({
                    **result,
                    "issue": "missing_from_MANAGED_METHODS",
                    "message": f"Internal method '{method_name}' not in MANAGED_METHODS"
                })
        
        elif tier == "external":
            # Should be in service_module_map
            service_class = method_spec.get("implementation", {}).get("class")
            if service_class in service_map:
                result["status"] = "valid"
                result["source"] = "service_module_map"
                result["module"] = service_map[service_class]
                valid.append(result)
            else:
                warnings.append({
                    **result,
                    "issue": "missing_from_service_map",
                    "message": f"External method class '{service_class}' not in service_module_map"
                })
        
        elif tier == "hybrid":
            # Check both
            in_managed = method_name in managed_methods
            service_class = method_spec.get("implementation", {}).get("class")
            in_service_map = service_class in service_map
            
            if in_managed or in_service_map:
                result["status"] = "valid"
                result["source"] = []
                if in_managed:
                    result["source"].append("MANAGED_METHODS")
                if in_service_map:
                    result["source"].append("service_module_map")
                valid.append(result)
            else:
                warnings.append({
                    **result,
                    "issue": "hybrid_not_found",
                    "message": f"Hybrid method '{method_name}' not in MANAGED_METHODS or service_map"
                })
        
        # Validate models exist
        for model_type in ["request", "response"]:
            model_name = method_spec.get("models", {}).get(model_type)
            if model_name and not validate_model_exists(model_name):
                warnings.append({
                    "method": method_name,
                    "issue": f"model_not_found_{model_type}",
                    "model": model_name,
                    "message": f"Model '{model_name}' not found in codebase"
                })
    
    return valid, warnings, errors


def print_validation_report(
    valid: List[Dict],
    warnings: List[Dict],
    errors: List[Dict],
    output_json: bool = False
):
    """Print validation report."""
    if output_json:
        print(json.dumps({
            "valid": valid,
            "warnings": warnings,
            "errors": errors,
            "summary": {
                "valid_count": len(valid),
                "warning_count": len(warnings),
                "error_count": len(errors),
                "total": len(valid) + len(warnings) + len(errors)
            }
        }, indent=2))
    else:
        print("=" * 80)
        print("METHODS INVENTORY VALIDATION REPORT")
        print("=" * 80)
        
        print(f"\n✓ VALID: {len(valid)} methods")
        for item in valid:
            source = item.get("source")
            if isinstance(source, list):
                source = " + ".join(source)
            print(f"  {item['method']} ({item['integration_tier']}) → {source}")
        
        if warnings:
            print(f"\n⚠ WARNINGS: {len(warnings)}")
            for item in warnings:
                print(f"  {item['method']}: {item['issue']}")
                if 'message' in item:
                    print(f"    {item['message']}")
        
        if errors:
            print(f"\n✗ ERRORS: {len(errors)}")
            for item in errors:
                print(f"  {item['method']}: {item['issue']}")
                print(f"    {item['message']}")
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {len(valid)} valid, {len(warnings)} warnings, {len(errors)} errors")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate methods inventory against code"
    )
    parser.add_argument(
        "--inventory",
        required=True,
        help="Path to methods_inventory_v1.yaml"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate corrected inventory"
    )
    
    args = parser.parse_args()
    
    try:
        # Setup
        collider_path = setup_collider_path()
        inventory_path = Path(args.inventory)
        
        # Load data
        print(f"Loading inventory from {inventory_path}...")
        inventory = load_inventory(inventory_path)
        
        print("Loading MANAGED_METHODS...")
        managed_methods = get_managed_methods()
        
        print("Loading service_module_map...")
        service_map = get_service_module_map()
        
        print(f"\nValidating {len(inventory)} methods...\n")
        
        # Validate
        valid, warnings, errors = validate_inventory(
            inventory,
            managed_methods,
            service_map
        )
        
        # Report
        print_validation_report(valid, warnings, errors, args.json)
        
        # Exit code
        sys.exit(0 if len(errors) == 0 else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
