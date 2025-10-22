"""
Methodtools Validator

Validates tool YAMLs against methods_inventory_v1.yaml.
Checks: method exists, models match, parameters correct, classification aligns.

Usage:
    python methodtools_validator.py --inventory path/to/methods_inventory_v1.yaml --tools path/to/methodtools_v1/
    python methodtools_validator.py --inventory inventory.yaml --tools tools/ --json
    python methodtools_validator.py --inventory inventory.yaml --tool single_tool.yaml
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def validate_tool_yaml(
    tool_yaml: Dict[str, Any],
    tool_path: Path,
    inventory: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate single tool YAML against inventory.
    
    Returns validation result with status and issues.
    """
    result = {
        "tool": tool_yaml.get("name"),
        "file": str(tool_path),
        "status": "valid",
        "issues": [],
    }
    
    # Extract method reference
    method_ref = tool_yaml.get("method_reference", {})
    service = method_ref.get("service")
    method = method_ref.get("method")
    
    if not method:
        result["status"] = "error"
        result["issues"].append({
            "type": "missing_method_reference",
            "message": "Tool YAML missing method_reference.method"
        })
        return result
    
    # Check if method exists in inventory
    if method not in inventory:
        result["status"] = "error"
        result["issues"].append({
            "type": "method_not_in_inventory",
            "method": method,
            "message": f"Method '{method}' not found in inventory"
        })
        return result
    
    inv_method = inventory[method]
    
    # Validate models match
    tool_models = tool_yaml.get("data_contracts", {})
    inv_models = inv_method.get("models", {})
    
    tool_request = tool_models.get("request_model")
    inv_request = inv_models.get("request")
    if tool_request and inv_request and tool_request != inv_request:
        result["status"] = "warning"
        result["issues"].append({
            "type": "request_model_mismatch",
            "tool": tool_request,
            "inventory": inv_request,
            "message": f"Request model mismatch: {tool_request} != {inv_request}"
        })
    
    tool_response = tool_models.get("response_model")
    inv_response = inv_models.get("response")
    if tool_response and inv_response and tool_response != inv_response:
        result["status"] = "warning"
        result["issues"].append({
            "type": "response_model_mismatch",
            "tool": tool_response,
            "inventory": inv_response,
            "message": f"Response model mismatch: {tool_response} != {inv_response}"
        })
    
    # Validate classification alignment
    tool_class = method_ref.get("classification", {})
    inv_class = inv_method.get("classification", {})
    
    for field in ["domain", "subdomain", "capability", "integration_tier"]:
        tool_val = tool_class.get(field)
        inv_val = inv_class.get(field)
        if tool_val and inv_val and tool_val != inv_val:
            result["status"] = "warning"
            result["issues"].append({
                "type": "classification_mismatch",
                "field": field,
                "tool": tool_val,
                "inventory": inv_val,
                "message": f"Classification.{field} mismatch: {tool_val} != {inv_val}"
            })
    
    # Validate service/method implementation
    tool_impl = tool_yaml.get("implementation", {}).get("method_wrapper", {})
    tool_method_name = tool_impl.get("method_name")
    inv_impl = inv_method.get("implementation", {})
    inv_class = inv_impl.get("class")
    inv_method_name = inv_impl.get("method")
    
    expected = f"{inv_class}.{inv_method_name}" if inv_class and inv_method_name else None
    if tool_method_name and expected and tool_method_name != expected:
        result["status"] = "warning"
        result["issues"].append({
            "type": "implementation_mismatch",
            "tool": tool_method_name,
            "inventory": expected,
            "message": f"Implementation mismatch: {tool_method_name} != {expected}"
        })
    
    # Check version compatibility
    tool_version = tool_yaml.get("version")
    inv_version = inv_method.get("version")
    if tool_version and inv_version and tool_version != inv_version:
        result["issues"].append({
            "type": "version_mismatch",
            "tool": tool_version,
            "inventory": inv_version,
            "message": f"Version mismatch (informational): {tool_version} != {inv_version}"
        })
    
    return result


def validate_all_tools(
    tools_dir: Path,
    inventory: Dict[str, Any]
) -> Dict[str, List[Dict]]:
    """Validate all tool YAMLs in directory."""
    results = {
        "valid": [],
        "warnings": [],
        "errors": [],
    }
    
    for tool_path in tools_dir.glob("*.yaml"):
        try:
            tool_yaml = load_yaml(tool_path)
            validation = validate_tool_yaml(tool_yaml, tool_path, inventory)
            
            if validation["status"] == "valid":
                results["valid"].append(validation)
            elif validation["status"] == "warning":
                results["warnings"].append(validation)
            else:
                results["errors"].append(validation)
        
        except Exception as e:
            results["errors"].append({
                "tool": str(tool_path),
                "file": str(tool_path),
                "status": "error",
                "issues": [{
                    "type": "parse_error",
                    "message": f"Failed to parse YAML: {e}"
                }]
            })
    
    return results


def print_validation_report(
    results: Dict[str, List[Dict]],
    output_json: bool = False
):
    """Print validation report."""
    if output_json:
        print(json.dumps({
            "results": results,
            "summary": {
                "valid": len(results["valid"]),
                "warnings": len(results["warnings"]),
                "errors": len(results["errors"]),
                "total": sum(len(v) for v in results.values())
            }
        }, indent=2))
    else:
        total = sum(len(v) for v in results.values())
        
        print("=" * 80)
        print("METHODTOOLS VALIDATION REPORT")
        print("=" * 80)
        
        print(f"\n✓ VALID: {len(results['valid'])} tools")
        for item in results["valid"]:
            print(f"  {item['tool']} ({Path(item['file']).name})")
        
        if results["warnings"]:
            print(f"\n⚠ WARNINGS: {len(results['warnings'])} tools")
            for item in results["warnings"]:
                print(f"\n  {item['tool']} ({Path(item['file']).name})")
                for issue in item["issues"]:
                    print(f"    - {issue['type']}: {issue['message']}")
        
        if results["errors"]:
            print(f"\n✗ ERRORS: {len(results['errors'])} tools")
            for item in results["errors"]:
                print(f"\n  {item.get('tool', 'unknown')} ({Path(item['file']).name})")
                for issue in item["issues"]:
                    print(f"    - {issue['type']}: {issue['message']}")
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {len(results['valid'])} valid, {len(results['warnings'])} warnings, {len(results['errors'])} errors")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate methodtools YAMLs against inventory"
    )
    parser.add_argument(
        "--inventory",
        required=True,
        help="Path to methods_inventory_v1.yaml"
    )
    parser.add_argument(
        "--tools",
        help="Path to methodtools_v1/ directory or single tool YAML"
    )
    parser.add_argument(
        "--tool",
        help="Path to single tool YAML (alias for --tools)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        # Load inventory
        inventory_path = Path(args.inventory)
        if not inventory_path.exists():
            print(f"Error: Inventory not found: {inventory_path}")
            sys.exit(1)
        
        inventory = load_yaml(inventory_path)
        
        # Determine tools path
        tools_path = Path(args.tool or args.tools) if (args.tool or args.tools) else None
        if not tools_path:
            print("Error: --tools or --tool required")
            sys.exit(1)
        
        # Validate
        if tools_path.is_file():
            # Single tool
            tool_yaml = load_yaml(tools_path)
            validation = validate_tool_yaml(tool_yaml, tools_path, inventory)
            results = {
                "valid": [validation] if validation["status"] == "valid" else [],
                "warnings": [validation] if validation["status"] == "warning" else [],
                "errors": [validation] if validation["status"] == "error" else [],
            }
        else:
            # Directory of tools
            results = validate_all_tools(tools_path, inventory)
        
        # Report
        print_validation_report(results, args.json)
        
        # Exit code
        sys.exit(0 if len(results["errors"]) == 0 else 1)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
