#!/usr/bin/env python3
r"""
Interactive Workflow Builder

Interactive CLI to build workflows from user goals: goal → suggest methods → build workflow → generate YAML.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Interactive mode
    python workflow_builder.py
    
    # Quick build from goal
    python workflow_builder.py --goal "Create casefile and grant permission"
    
    # Non-interactive with preset methods
    python workflow_builder.py --methods create_casefile grant_permission --output workflow.yaml
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set


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
        import src
        return dict(MANAGED_METHODS)
    except ImportError as e:
        print(f"Error: Could not import MANAGED_METHODS: {e}", file=sys.stderr)
        sys.exit(1)


def suggest_methods_for_goal(goal: str, registry: Dict[str, Any]) -> List[tuple[str, str, float]]:
    """Suggest methods that match the goal."""
    suggestions = []
    goal_lower = goal.lower()
    
    # Keywords to look for
    keywords = [word for word in goal_lower.split() if len(word) > 3]
    
    for method_name, method_def in registry.items():
        score = 0.0
        
        # Check method name
        if any(kw in method_name.lower() for kw in keywords):
            score += 2.0
        
        # Check description
        if hasattr(method_def, 'description') and method_def.description:
            desc_lower = method_def.description.lower()
            for kw in keywords:
                if kw in desc_lower:
                    score += 1.0
        
        # Check classification
        if hasattr(method_def, 'classification'):
            classification = method_def.classification
            
            if hasattr(classification, 'domain') and classification.domain:
                if any(kw in classification.domain.lower() for kw in keywords):
                    score += 1.5
            
            if hasattr(classification, 'capability') and classification.capability:
                if any(kw in classification.capability.lower() for kw in keywords):
                    score += 1.5
        
        if score > 0:
            desc = getattr(method_def, 'description', method_name)
            suggestions.append((method_name, desc, score))
    
    # Sort by score descending
    suggestions.sort(key=lambda x: x[2], reverse=True)
    
    return suggestions


def interactive_mode(registry: Dict[str, Any]):
    """Run interactive workflow builder."""
    print("\n" + "=" * 80)
    print("Interactive Workflow Builder")
    print("=" * 80)
    print()
    
    # Get goal
    goal = input("What do you want to achieve? (e.g., 'Create casefile and share with user')\n> ").strip()
    
    if not goal:
        print("No goal provided. Exiting.")
        return
    
    print(f"\nSearching for methods matching: '{goal}'...")
    
    # Suggest methods
    suggestions = suggest_methods_for_goal(goal, registry)
    
    if not suggestions:
        print("No matching methods found.")
        return
    
    print(f"\nFound {len(suggestions)} matching methods:")
    print("-" * 80)
    
    # Show top 10
    for i, (method_name, desc, score) in enumerate(suggestions[:10], 1):
        print(f"{i}. {method_name} (score: {score:.1f})")
        print(f"   {desc}")
        print()
    
    # Select methods
    print("Select methods to include in workflow (comma-separated numbers, e.g., '1,3,5'):")
    selection = input("> ").strip()
    
    if not selection:
        print("No selection made. Exiting.")
        return
    
    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        selected_methods = [suggestions[i][0] for i in indices if 0 <= i < len(suggestions)]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return
    
    if not selected_methods:
        print("No valid methods selected. Exiting.")
        return
    
    print(f"\nSelected methods: {', '.join(selected_methods)}")
    print()
    
    # Ask for name
    workflow_name = input("Workflow name (press Enter for default): ").strip()
    if not workflow_name:
        workflow_name = "_".join(selected_methods[:3]) + "_workflow"
    
    print(f"\nWorkflow name: {workflow_name}")
    
    # Generate composite tool
    print("\nGenerating composite tool...")
    
    try:
        # Import composite generator logic
        from pathlib import Path
        import subprocess
        
        # Call composite_tool_generator.py
        toolset_dir = Path(__file__).parent
        cmd = [
            sys.executable,
            str(toolset_dir / "composite_tool_generator.py"),
            *selected_methods,
            "--name", workflow_name,
            "--auto-map",
            "--validate"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env={'COLLIDER_PATH': str(setup_collider_path())})
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        # Ask to save
        save = input("\nSave workflow to file? (y/n): ").strip().lower()
        
        if save == 'y':
            filename = input("Filename (press Enter for default): ").strip()
            if not filename:
                filename = f"{workflow_name}.yaml"
            
            # Generate YAML
            cmd_yaml = cmd + ["--output", filename]
            subprocess.run(cmd_yaml, env={'COLLIDER_PATH': str(setup_collider_path())})
            
            print(f"\n✓ Saved workflow to {filename}")
    
    except Exception as e:
        print(f"Error generating workflow: {e}", file=sys.stderr)


def quick_build(goal: str, registry: Dict[str, Any], top_n: int = 5):
    """Quick build workflow from goal (non-interactive)."""
    print(f"\nGoal: {goal}")
    print("=" * 80)
    
    suggestions = suggest_methods_for_goal(goal, registry)
    
    if not suggestions:
        print("No matching methods found.")
        return
    
    print(f"\nTop {top_n} suggested methods:")
    print("-" * 80)
    
    for i, (method_name, desc, score) in enumerate(suggestions[:top_n], 1):
        print(f"{i}. {method_name} (score: {score:.1f})")
        print(f"   {desc}")
        print()
    
    selected_methods = [s[0] for s in suggestions[:top_n]]
    workflow_name = "_".join(selected_methods[:3]) + "_workflow"
    
    print(f"Auto-selected workflow: {', '.join(selected_methods)}")
    print(f"Workflow name: {workflow_name}")
    print()
    
    # Generate composite tool
    try:
        from pathlib import Path
        import subprocess
        
        toolset_dir = Path(__file__).parent
        cmd = [
            sys.executable,
            str(toolset_dir / "composite_tool_generator.py"),
            *selected_methods,
            "--name", workflow_name,
            "--auto-map",
            "--validate"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env={'COLLIDER_PATH': str(setup_collider_path())})
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    
    except Exception as e:
        print(f"Error generating workflow: {e}", file=sys.stderr)


def preset_build(methods: List[str], registry: Dict[str, Any], output: Optional[str] = None):
    """Build workflow from preset methods."""
    print(f"\nBuilding workflow from: {', '.join(methods)}")
    print("=" * 80)
    
    # Validate methods
    for method in methods:
        if method not in registry:
            print(f"Error: Method '{method}' not found in registry", file=sys.stderr)
            sys.exit(1)
    
    workflow_name = "_".join(methods[:3]) + "_workflow"
    
    # Generate composite tool
    try:
        from pathlib import Path
        import subprocess
        
        toolset_dir = Path(__file__).parent
        cmd = [
            sys.executable,
            str(toolset_dir / "composite_tool_generator.py"),
            *methods,
            "--name", workflow_name,
            "--auto-map",
            "--validate"
        ]
        
        if output:
            cmd.extend(["--output", output])
        
        result = subprocess.run(cmd, capture_output=True, text=True, env={'COLLIDER_PATH': str(setup_collider_path())})
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        if output and result.returncode != 0:
            print(f"\n✓ Workflow saved to {output}")
    
    except Exception as e:
        print(f"Error generating workflow: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive workflow builder: goal → methods → YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--goal', help='Goal description for quick build')
    parser.add_argument('--methods', nargs='+', help='Preset methods for workflow')
    parser.add_argument('--output', help='Output YAML file')
    parser.add_argument('--top-n', type=int, default=5, help='Number of methods to suggest (default: 5)')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    registry = load_method_registry()
    
    if not registry:
        print("Error: No methods found in registry", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(registry)} methods from registry")
    
    # Preset build
    if args.methods:
        preset_build(args.methods, registry, args.output)
        return
    
    # Quick build
    if args.goal:
        quick_build(args.goal, registry, args.top_n)
        return
    
    # Interactive mode
    interactive_mode(registry)


if __name__ == '__main__':
    main()
