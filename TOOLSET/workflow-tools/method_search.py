#!/usr/bin/env python3
r"""
Method Search Tool - Search registered service methods by query/domain/capability.

This tool searches the MANAGED_METHODS registry from my-tiny-data-collider
to help discover methods for workflow composition.

Usage:
    python method_search.py "gmail"                           # Search by keyword
    python method_search.py --domain workspace                # Filter by domain
    python method_search.py --capability create               # Filter by capability
    python method_search.py "casefile" --domain workspace     # Combined search
    python method_search.py --list-all                        # List all methods
    python method_search.py --json                            # JSON output
    
Requirements:
    - my-tiny-data-collider repository accessible
    - Set COLLIDER_PATH environment variable or use --collider-path
    
Example:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    python method_search.py "gmail" --domain workspace --json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def load_managed_methods() -> Dict[str, Any]:
    """Load MANAGED_METHODS registry from collider."""
    try:
        # Import registry infrastructure
        from pydantic_ai_integration.method_registry import MANAGED_METHODS
        
        # Trigger imports to populate registry
        import src
        
        return dict(MANAGED_METHODS)
    except ImportError as e:
        print(f"Error: Could not import from collider: {e}", file=sys.stderr)
        print("Make sure my-tiny-data-collider is installed or accessible", file=sys.stderr)
        sys.exit(1)


def search_methods(
    query: Optional[str] = None,
    domain: Optional[str] = None,
    subdomain: Optional[str] = None,
    capability: Optional[str] = None,
    complexity: Optional[str] = None,
    maturity: Optional[str] = None,
    integration_tier: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search methods in MANAGED_METHODS registry.
    
    Args:
        query: Keyword search (searches name, description)
        domain: Filter by domain
        subdomain: Filter by subdomain
        capability: Filter by capability (create, read, update, delete, etc.)
        complexity: Filter by complexity (atomic, composite, pipeline)
        maturity: Filter by maturity (stable, beta, experimental)
        integration_tier: Filter by integration tier (internal, external)
    
    Returns:
        List of matching method definitions
    """
    methods = load_managed_methods()
    results = []
    
    for method_name, method_def in methods.items():
        # Start with match = True, filter down
        match = True
        
        # Keyword search in name and description
        if query:
            query_lower = query.lower()
            name_match = query_lower in method_name.lower()
            desc_match = query_lower in (method_def.description or "").lower()
            match = match and (name_match or desc_match)
        
        # Classification filters
        if domain:
            match = match and (method_def.domain == domain)
        if subdomain:
            match = match and (method_def.subdomain == subdomain)
        if capability:
            match = match and (method_def.capability == capability)
        if complexity:
            match = match and (method_def.complexity == complexity)
        if maturity:
            match = match and (method_def.maturity == maturity)
        if integration_tier:
            match = match and (method_def.integration_tier == integration_tier)
        
        if match:
            # Extract method info
            result = {
                "name": method_name,
                "description": method_def.description,
                "version": method_def.version,
                "classification": {
                    "domain": method_def.domain,
                    "subdomain": method_def.subdomain,
                    "capability": method_def.capability,
                    "complexity": method_def.complexity,
                    "maturity": method_def.maturity,
                    "integration_tier": method_def.integration_tier,
                },
                "implementation": {
                    "class": method_def.implementation_class,
                    "method": method_def.implementation_method,
                },
                "models": {
                    "request": method_def.request_model_class.__name__ if method_def.request_model_class else None,
                    "response": method_def.response_model_class.__name__ if method_def.response_model_class else None,
                },
            }
            results.append(result)
    
    return results


def print_results(results: List[Dict[str, Any]], output_format: str = "text") -> None:
    """Print search results."""
    if output_format == "json":
        print(json.dumps(results, indent=2))
        return
    
    if not results:
        print("No methods found matching criteria.")
        return
    
    print(f"\nFound {len(results)} method(s):\n")
    print("=" * 80)
    
    for i, method in enumerate(results, 1):
        print(f"\n{i}. {method['name']}")
        print(f"   Description: {method['description']}")
        print(f"   Version: {method['version']}")
        print(f"   Classification:")
        print(f"     Domain: {method['classification']['domain']}")
        print(f"     Subdomain: {method['classification']['subdomain']}")
        print(f"     Capability: {method['classification']['capability']}")
        print(f"     Complexity: {method['classification']['complexity']}")
        print(f"     Maturity: {method['classification']['maturity']}")
        print(f"     Integration: {method['classification']['integration_tier']}")
        print(f"   Implementation:")
        print(f"     Class: {method['implementation']['class']}")
        print(f"     Method: {method['implementation']['method']}")
        print(f"   Models:")
        print(f"     Request: {method['models']['request']}")
        print(f"     Response: {method['models']['response']}")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search service methods in MANAGED_METHODS registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python method_search.py "gmail"                           # Search by keyword
  python method_search.py --domain workspace                # Filter by domain
  python method_search.py --capability create               # Filter by capability
  python method_search.py "casefile" --domain workspace     # Combined search
  python method_search.py --list-all                        # List all methods
  python method_search.py --json                            # JSON output
        """,
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query (searches method name and description)",
    )
    
    parser.add_argument(
        "--domain",
        help="Filter by domain (workspace, communication, automation)",
    )
    
    parser.add_argument(
        "--subdomain",
        help="Filter by subdomain (casefile, tool_session, chat_session, etc.)",
    )
    
    parser.add_argument(
        "--capability",
        help="Filter by capability (create, read, update, delete, search, process)",
    )
    
    parser.add_argument(
        "--complexity",
        help="Filter by complexity (atomic, composite, pipeline)",
    )
    
    parser.add_argument(
        "--maturity",
        help="Filter by maturity (stable, beta, experimental)",
    )
    
    parser.add_argument(
        "--integration-tier",
        help="Filter by integration tier (internal, external)",
    )
    
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all registered methods",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    parser.add_argument(
        "--collider-path",
        help="Path to my-tiny-data-collider repository",
    )
    
    args = parser.parse_args()
    
    # Set up collider path
    setup_collider_path(args.collider_path)
    
    # Perform search
    results = search_methods(
        query=args.query,
        domain=args.domain,
        subdomain=args.subdomain,
        capability=args.capability,
        complexity=args.complexity,
        maturity=args.maturity,
        integration_tier=args.integration_tier,
    )
    
    # Print results
    output_format = "json" if args.json else "text"
    print_results(results, output_format)
    
    # Exit code: 0 if results found, 1 if no results
    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
