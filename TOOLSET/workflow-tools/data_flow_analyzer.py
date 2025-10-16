#!/usr/bin/env python3
r"""
Data Flow Analyzer

Track data lineage and flow across tools and methods in workflows.

Usage:
    $env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"
    
    # Analyze data flow for workflow
    python data_flow_analyzer.py create_casefile grant_permission
    
    # Show full lineage
    python data_flow_analyzer.py method1 method2 method3 --full-lineage
    
    # Export flow diagram
    python data_flow_analyzer.py create_casefile list_casefiles --export flow.json
    
    # Visualize flow
    python data_flow_analyzer.py method1 method2 --visualize
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field as dc_field
from collections import defaultdict


@dataclass
class DataNode:
    """Node in data flow graph."""
    name: str
    type: str  # 'input', 'output', 'intermediate'
    source_method: Optional[str] = None
    target_methods: List[str] = dc_field(default_factory=list)
    field_type: str = "unknown"
    transformations: List[str] = dc_field(default_factory=list)


@dataclass
class DataFlow:
    """Data flow between methods."""
    source_method: str
    source_field: str
    target_method: str
    target_field: str
    flow_type: str  # 'direct', 'transformed', 'split', 'merged'
    confidence: float = 1.0


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


def get_method_fields(method_def: Any) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Extract input/output fields with types from method definition."""
    input_fields = {}
    output_fields = {}
    
    try:
        # Input fields from request model
        if hasattr(method_def, 'request_model_class') and method_def.request_model_class:
            request_class = method_def.request_model_class
            if hasattr(request_class, 'model_fields'):
                for field_name, field_info in request_class.model_fields.items():
                    field_type = str(field_info.annotation)
                    input_fields[field_name] = field_type
        
        # Output fields from response model
        if hasattr(method_def, 'response_model_class') and method_def.response_model_class:
            response_class = method_def.response_model_class
            if hasattr(response_class, 'model_fields'):
                for field_name, field_info in response_class.model_fields.items():
                    field_type = str(field_info.annotation)
                    output_fields[field_name] = field_type
    
    except Exception as e:
        print(f"Warning: Could not extract fields: {e}", file=sys.stderr)
    
    return input_fields, output_fields


def analyze_data_flow(method_names: List[str], registry: Dict[str, Any]) -> Tuple[List[DataNode], List[DataFlow]]:
    """Analyze data flow across method sequence."""
    
    # Validate methods
    for method in method_names:
        if method not in registry:
            print(f"Error: Method '{method}' not found in registry", file=sys.stderr)
            sys.exit(1)
    
    nodes = []
    flows = []
    all_fields = {}  # Track all fields and their sources
    
    # Build nodes and track fields
    for method_name in method_names:
        method_def = registry[method_name]
        input_fields, output_fields = get_method_fields(method_def)
        
        # Create input nodes
        for field_name, field_type in input_fields.items():
            node_id = f"{method_name}.input.{field_name}"
            if node_id not in [n.name for n in nodes]:
                nodes.append(DataNode(
                    name=field_name,
                    type='input',
                    source_method=method_name,
                    field_type=field_type
                ))
        
        # Create output nodes
        for field_name, field_type in output_fields.items():
            node_id = f"{method_name}.output.{field_name}"
            if node_id not in [n.name for n in nodes]:
                node = DataNode(
                    name=field_name,
                    type='output',
                    source_method=method_name,
                    field_type=field_type
                )
                nodes.append(node)
                
                # Track as potential source for next methods
                if field_name not in all_fields:
                    all_fields[field_name] = []
                all_fields[field_name].append((method_name, field_type))
    
    # Detect flows between methods
    for i, method_name in enumerate(method_names):
        if i == 0:
            continue  # Skip first method (no previous source)
        
        method_def = registry[method_name]
        input_fields, _ = get_method_fields(method_def)
        
        # Check which inputs can be satisfied by previous outputs
        for field_name, field_type in input_fields.items():
            # Look for matching field in previous methods
            if field_name in all_fields:
                for source_method, source_type in all_fields[field_name]:
                    if source_method in method_names[:i]:  # Only previous methods
                        flow_type = 'direct' if source_type == field_type else 'transformed'
                        confidence = 1.0 if field_name == field_name else 0.8
                        
                        flows.append(DataFlow(
                            source_method=source_method,
                            source_field=field_name,
                            target_method=method_name,
                            target_field=field_name,
                            flow_type=flow_type,
                            confidence=confidence
                        ))
            
            # Check for semantic matches (e.g., casefile_id -> id)
            for source_field, sources in all_fields.items():
                if source_field != field_name and 'id' in field_name.lower() and 'id' in source_field.lower():
                    for source_method, source_type in sources:
                        if source_method in method_names[:i]:
                            flows.append(DataFlow(
                                source_method=source_method,
                                source_field=source_field,
                                target_method=method_name,
                                target_field=field_name,
                                flow_type='transformed',
                                confidence=0.6
                            ))
    
    return nodes, flows


def build_lineage_graph(flows: List[DataFlow]) -> Dict[str, List[str]]:
    """Build lineage graph showing field dependencies."""
    lineage = defaultdict(list)
    
    for flow in flows:
        source_key = f"{flow.source_method}.{flow.source_field}"
        target_key = f"{flow.target_method}.{flow.target_field}"
        lineage[target_key].append(source_key)
    
    return dict(lineage)


def find_data_sources(field: str, method: str, lineage: Dict[str, List[str]], visited: Set[str] = None) -> List[str]:
    """Recursively find all data sources for a field."""
    if visited is None:
        visited = set()
    
    key = f"{method}.{field}"
    if key in visited:
        return []
    
    visited.add(key)
    sources = []
    
    if key in lineage:
        for source in lineage[key]:
            sources.append(source)
            # Recursively find sources of sources
            source_method, source_field = source.split('.', 1)
            deep_sources = find_data_sources(source_field, source_method, lineage, visited)
            sources.extend(deep_sources)
    
    return sources


def visualize_flow(nodes: List[DataNode], flows: List[DataFlow], method_names: List[str]) -> str:
    """Generate ASCII visualization of data flow."""
    output = []
    output.append("\nData Flow Visualization")
    output.append("=" * 80)
    output.append("")
    
    for i, method_name in enumerate(method_names):
        output.append(f"[{i+1}] {method_name}")
        output.append("─" * 40)
        
        # Show inputs
        method_inputs = [n for n in nodes if n.source_method == method_name and n.type == 'input']
        if method_inputs:
            output.append("  Inputs:")
            for node in method_inputs[:5]:
                # Check if this input comes from previous method
                incoming = [f for f in flows if f.target_method == method_name and f.target_field == node.name]
                if incoming:
                    source = incoming[0]
                    arrow = "→" if source.flow_type == 'direct' else "⟿"
                    output.append(f"    {arrow} {node.name} (from {source.source_method}.{source.source_field})")
                else:
                    output.append(f"    • {node.name} (user input)")
        
        # Show outputs
        method_outputs = [n for n in nodes if n.source_method == method_name and n.type == 'output']
        if method_outputs:
            output.append("  Outputs:")
            for node in method_outputs[:5]:
                # Check if this output feeds into next method
                outgoing = [f for f in flows if f.source_method == method_name and f.source_field == node.name]
                if outgoing:
                    targets = [f"{f.target_method}.{f.target_field}" for f in outgoing]
                    output.append(f"    • {node.name} → [{', '.join(targets[:2])}]")
                else:
                    output.append(f"    • {node.name}")
        
        output.append("")
    
    output.append("=" * 80)
    return "\n".join(output)


def print_analysis(nodes: List[DataNode], flows: List[DataFlow], method_names: List[str], full_lineage: bool = False):
    """Print data flow analysis."""
    print("\nData Flow Analysis")
    print("=" * 80)
    print(f"Methods: {len(method_names)}")
    print(f"Data nodes: {len(nodes)}")
    print(f"Data flows: {len(flows)}")
    print()
    
    # Flow summary
    print("Flow Summary:")
    print("-" * 80)
    for flow in flows:
        confidence_marker = "✓" if flow.confidence >= 0.8 else "~"
        print(f"{confidence_marker} {flow.source_method}.{flow.source_field} → {flow.target_method}.{flow.target_field}")
        print(f"   Type: {flow.flow_type}, Confidence: {flow.confidence:.1%}")
    print()
    
    # Show lineage if requested
    if full_lineage:
        lineage = build_lineage_graph(flows)
        print("Full Data Lineage:")
        print("-" * 80)
        for target, sources in lineage.items():
            print(f"{target}")
            for source in sources:
                print(f"  ← {source}")
        print()
    
    # Visualization
    viz = visualize_flow(nodes, flows, method_names)
    print(viz)


def export_analysis(nodes: List[DataNode], flows: List[DataFlow], filepath: Path):
    """Export analysis to JSON."""
    output = {
        'nodes': [
            {
                'name': n.name,
                'type': n.type,
                'source_method': n.source_method,
                'target_methods': n.target_methods,
                'field_type': n.field_type
            }
            for n in nodes
        ],
        'flows': [
            {
                'source_method': f.source_method,
                'source_field': f.source_field,
                'target_method': f.target_method,
                'target_field': f.target_field,
                'flow_type': f.flow_type,
                'confidence': f.confidence
            }
            for f in flows
        ]
    }
    
    filepath.write_text(json.dumps(output, indent=2))
    print(f"\nExported data flow to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze data flow and lineage across methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('methods', nargs='+', help='Method names in sequence')
    parser.add_argument('--collider-path', help='Path to collider repository')
    parser.add_argument('--full-lineage', action='store_true', help='Show full data lineage')
    parser.add_argument('--visualize', action='store_true', help='Show flow visualization')
    parser.add_argument('--export', help='Export analysis to JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Setup
    setup_collider_path(args.collider_path)
    registry = load_method_registry()
    
    if not registry:
        print("Error: No methods found in registry", file=sys.stderr)
        sys.exit(1)
    
    # Analyze
    nodes, flows = analyze_data_flow(args.methods, registry)
    
    # Output
    if args.export:
        export_analysis(nodes, flows, Path(args.export))
    
    if args.json:
        output = {
            'methods': args.methods,
            'node_count': len(nodes),
            'flow_count': len(flows),
            'flows': [
                {
                    'source': f"{f.source_method}.{f.source_field}",
                    'target': f"{f.target_method}.{f.target_field}",
                    'type': f.flow_type,
                    'confidence': f.confidence
                }
                for f in flows
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print_analysis(nodes, flows, args.methods, args.full_lineage)


if __name__ == '__main__':
    main()
