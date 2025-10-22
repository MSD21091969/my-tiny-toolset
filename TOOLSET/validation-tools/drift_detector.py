"""
Drift Detector

Detects drift between methods_inventory_v1.yaml and current code state.
Flags: new methods, changed signatures, deleted methods, model changes.

Usage:
    python drift_detector.py --inventory path/to/methods_inventory_v1.yaml
    python drift_detector.py --inventory path/to/inventory.yaml --json
    python drift_detector.py --inventory path/to/inventory.yaml --ci-mode  # Exit 1 if drift
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

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


def get_code_methods() -> Dict[str, Dict[str, Any]]:
    """Get all methods from current codebase."""
    try:
        from src.methodregistryservice import MANAGED_METHODS
        
        methods = {}
        for method_key, method_def in MANAGED_METHODS.items():
            methods[method_def.method_name] = {
                "service_class": method_def.service_class,
                "request_model": method_def.request_model_class.__name__,
                "response_model": method_def.response_model_class.__name__,
                "classification": method_def.classification,
                "version": method_def.version,
            }
        return methods
    except Exception as e:
        print(f"Warning: Could not load code methods: {e}")
        return {}


def detect_drift(
    inventory: Dict[str, Any],
    code_methods: Dict[str, Dict[str, Any]]
) -> Dict[str, List[Dict]]:
    """
    Detect drift between inventory and code.
    
    Returns dict with:
        - new_methods: Methods in code but not inventory
        - deleted_methods: Methods in inventory but not code
        - changed_signatures: Methods with model changes
        - changed_classification: Methods with classification changes
    """
    inventory_names = set(inventory.keys())
    code_names = set(code_methods.keys())
    
    drift = {
        "new_methods": [],
        "deleted_methods": [],
        "changed_signatures": [],
        "changed_classification": [],
        "version_changes": [],
    }
    
    # New methods (in code, not inventory)
    for method_name in code_names - inventory_names:
        code_method = code_methods[method_name]
        drift["new_methods"].append({
            "method": method_name,
            "request_model": code_method["request_model"],
            "response_model": code_method["response_model"],
            "classification": code_method["classification"],
        })
    
    # Deleted methods (in inventory, not code)
    # Only check internal methods (external may not be in MANAGED_METHODS)
    for method_name in inventory_names:
        tier = inventory[method_name].get("classification", {}).get("integration_tier")
        if tier == "internal" and method_name not in code_names:
            drift["deleted_methods"].append({
                "method": method_name,
                "was_internal": True,
            })
    
    # Changed methods (in both, but different)
    for method_name in inventory_names & code_names:
        inv_method = inventory[method_name]
        code_method = code_methods[method_name]
        
        # Check model changes
        inv_req = inv_method.get("models", {}).get("request")
        inv_res = inv_method.get("models", {}).get("response")
        code_req = code_method["request_model"]
        code_res = code_method["response_model"]
        
        if inv_req != code_req or inv_res != code_res:
            drift["changed_signatures"].append({
                "method": method_name,
                "inventory": {"request": inv_req, "response": inv_res},
                "code": {"request": code_req, "response": code_res},
            })
        
        # Check classification changes
        inv_class = inv_method.get("classification", {})
        code_class = code_method.get("classification", {})
        
        changes = []
        for key in ["domain", "subdomain", "capability", "complexity", "maturity"]:
            if inv_class.get(key) != code_class.get(key):
                changes.append({
                    "field": key,
                    "inventory": inv_class.get(key),
                    "code": code_class.get(key),
                })
        
        if changes:
            drift["changed_classification"].append({
                "method": method_name,
                "changes": changes,
            })
        
        # Check version changes
        inv_ver = inv_method.get("version")
        code_ver = code_method.get("version")
        if inv_ver and code_ver and inv_ver != code_ver:
            drift["version_changes"].append({
                "method": method_name,
                "inventory": inv_ver,
                "code": code_ver,
            })
    
    return drift


def calculate_drift_score(drift: Dict[str, List]) -> Dict[str, Any]:
    """Calculate drift severity score."""
    weights = {
        "new_methods": 1,
        "deleted_methods": 3,  # High severity
        "changed_signatures": 2,  # Medium severity
        "changed_classification": 1,
        "version_changes": 1,
    }
    
    score = 0
    for category, items in drift.items():
        score += len(items) * weights.get(category, 1)
    
    total_changes = sum(len(items) for items in drift.values())
    
    if score == 0:
        severity = "none"
    elif score <= 3:
        severity = "low"
    elif score <= 10:
        severity = "medium"
    else:
        severity = "high"
    
    return {
        "total_changes": total_changes,
        "drift_score": score,
        "severity": severity,
        "requires_update": total_changes > 0,
    }


def print_drift_report(
    drift: Dict[str, List],
    score: Dict[str, Any],
    output_json: bool = False
):
    """Print drift detection report."""
    if output_json:
        print(json.dumps({
            "drift": drift,
            "score": score,
            "timestamp": datetime.now().isoformat(),
        }, indent=2))
    else:
        print("=" * 80)
        print("DRIFT DETECTION REPORT")
        print("=" * 80)
        
        print(f"\nSeverity: {score['severity'].upper()}")
        print(f"Drift Score: {score['drift_score']}")
        print(f"Total Changes: {score['total_changes']}")
        
        if drift["new_methods"]:
            print(f"\n✚ NEW METHODS: {len(drift['new_methods'])}")
            for item in drift["new_methods"]:
                print(f"  + {item['method']}")
                print(f"    Request: {item['request_model']}")
                print(f"    Response: {item['response_model']}")
        
        if drift["deleted_methods"]:
            print(f"\n✖ DELETED METHODS: {len(drift['deleted_methods'])}")
            for item in drift["deleted_methods"]:
                print(f"  - {item['method']} (was internal)")
        
        if drift["changed_signatures"]:
            print(f"\n⚠ CHANGED SIGNATURES: {len(drift['changed_signatures'])}")
            for item in drift["changed_signatures"]:
                print(f"  ~ {item['method']}")
                inv = item["inventory"]
                code = item["code"]
                if inv["request"] != code["request"]:
                    print(f"    Request: {inv['request']} → {code['request']}")
                if inv["response"] != code["response"]:
                    print(f"    Response: {inv['response']} → {code['response']}")
        
        if drift["changed_classification"]:
            print(f"\n↻ CHANGED CLASSIFICATION: {len(drift['changed_classification'])}")
            for item in drift["changed_classification"]:
                print(f"  ~ {item['method']}")
                for change in item["changes"]:
                    print(f"    {change['field']}: {change['inventory']} → {change['code']}")
        
        if drift["version_changes"]:
            print(f"\n⬆ VERSION CHANGES: {len(drift['version_changes'])}")
            for item in drift["version_changes"]:
                print(f"  {item['method']}: {item['inventory']} → {item['code']}")
        
        if score["total_changes"] == 0:
            print("\n✓ No drift detected - inventory is synchronized with code")
        else:
            print(f"\n⚠ Inventory requires update ({score['total_changes']} changes detected)")
        
        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Detect drift between inventory and code"
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
        "--ci-mode",
        action="store_true",
        help="Exit with code 1 if drift detected (for CI/CD)"
    )
    
    args = parser.parse_args()
    
    try:
        # Setup
        collider_path = setup_collider_path()
        inventory_path = Path(args.inventory)
        
        # Load data
        if not args.json:
            print(f"Loading inventory from {inventory_path}...")
        inventory = load_inventory(inventory_path)
        
        if not args.json:
            print("Loading code methods...")
        code_methods = get_code_methods()
        
        if not args.json:
            print(f"\nAnalyzing drift...\n")
        
        # Detect drift
        drift = detect_drift(inventory, code_methods)
        score = calculate_drift_score(drift)
        
        # Report
        print_drift_report(drift, score, args.json)
        
        # Exit code for CI mode
        if args.ci_mode and score["requires_update"]:
            sys.exit(1)
        else:
            sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
