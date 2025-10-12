"""
Code Analyzer - Extract models, functions, and methods for analysis
Supports exporting to CSV, Excel, and JSON formats
"""

import ast
import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ModelInfo:
    """Information about a model/class"""

    name: str
    file_path: str
    line_number: int
    base_classes: List[str]
    fields: List[Dict[str, str]]
    docstring: Optional[str]
    decorators: List[str]
    is_pydantic: bool
    is_dataclass: bool


@dataclass
class FunctionInfo:
    """Information about a function or method"""

    name: str
    file_path: str
    line_number: int
    class_name: Optional[str]
    parameters: List[Dict[str, str]]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    is_async: bool


@dataclass
class RequestResponseMapping:
    """Mapping between request and response models"""

    function_name: str
    file_path: str
    request_models: List[str]
    response_models: List[str]
    http_method: Optional[str]
    endpoint: Optional[str]


class CodeAnalyzer:
    """Analyze Python code to extract models and functions"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.models: List[ModelInfo] = []
        self.functions: List[FunctionInfo] = []
        self.mappings: List[RequestResponseMapping] = []

    def analyze_directory(self, exclude_patterns: List[str] = None):
        """Analyze all Python files in the directory"""
        if exclude_patterns is None:
            exclude_patterns = ["venv", ".venv", "__pycache__", "node_modules", ".git"]

        python_files = []
        for py_file in self.root_path.rglob("*.py"):
            # Skip excluded directories
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)

        for py_file in python_files:
            self.analyze_file(py_file)

    def analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            self._extract_from_ast(tree, file_path)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _extract_from_ast(self, tree: ast.AST, file_path: Path):
        """Extract information from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._extract_model(node, file_path)
            elif isinstance(node, ast.FunctionDef) or isinstance(
                node, ast.AsyncFunctionDef
            ):
                self._extract_function(node, file_path)

    def _extract_model(self, node: ast.ClassDef, file_path: Path):
        """Extract model/class information"""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{self._get_attr_name(base)}")

        # Check if it's Pydantic or dataclass
        is_pydantic = any("BaseModel" in base for base in base_classes)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        is_dataclass = "dataclass" in decorators

        # Extract fields
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                field_type = self._get_annotation_str(item.annotation)
                default_value = (
                    self._get_default_value(item.value) if item.value else None
                )
                fields.append(
                    {"name": field_name, "type": field_type, "default": default_value}
                )

        # Get docstring
        docstring = ast.get_docstring(node)

        model = ModelInfo(
            name=node.name,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            base_classes=base_classes,
            fields=fields,
            docstring=docstring,
            decorators=decorators,
            is_pydantic=is_pydantic,
            is_dataclass=is_dataclass,
        )
        self.models.append(model)

    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        class_name: str = None,
    ):
        """Extract function/method information"""
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param_name = arg.arg
            param_type = (
                self._get_annotation_str(arg.annotation) if arg.annotation else None
            )
            parameters.append({"name": param_name, "type": param_type})

        # Get return type
        return_type = self._get_annotation_str(node.returns) if node.returns else None

        # Get decorators
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        # Get docstring
        docstring = ast.get_docstring(node)

        function = FunctionInfo(
            name=node.name,
            file_path=str(file_path.relative_to(self.root_path)),
            line_number=node.lineno,
            class_name=class_name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )
        self.functions.append(function)

        # Try to detect request/response patterns
        self._detect_req_resp_mapping(node, file_path, function)

    def _detect_req_resp_mapping(
        self, node: ast.FunctionDef, file_path: Path, function: FunctionInfo
    ):
        """Detect request/response model patterns"""
        request_models = []
        response_models = []
        http_method = None
        endpoint = None

        # Check decorators for HTTP methods (FastAPI, Flask, etc.)
        for decorator in node.decorator_list:
            dec_name = self._get_decorator_name(decorator)
            if dec_name in ["get", "post", "put", "patch", "delete"]:
                http_method = dec_name.upper()
                # Try to extract endpoint
                if isinstance(decorator, ast.Call) and decorator.args:
                    if isinstance(decorator.args[0], ast.Constant):
                        endpoint = decorator.args[0].value

        # Look for type hints that suggest request/response
        for param in function.parameters:
            param_type = param.get("type", "")
            if param_type and (
                "Request" in param_type or "Input" in param_type or "Body" in param_type
            ):
                request_models.append(param_type)

        if function.return_type:
            if "Response" in function.return_type or "Output" in function.return_type:
                response_models.append(function.return_type)

        # Only create mapping if we found something interesting
        if request_models or response_models or http_method:
            mapping = RequestResponseMapping(
                function_name=function.name,
                file_path=function.file_path,
                request_models=request_models,
                response_models=response_models,
                http_method=http_method,
                endpoint=endpoint,
            )
            self.mappings.append(mapping)

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_attr_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return self._get_attr_name(decorator)
        return str(decorator)

    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get full attribute name"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def _get_annotation_str(self, annotation: ast.expr) -> str:
        """Convert annotation to string"""
        if annotation is None:
            return None
        try:
            return ast.unparse(annotation)
        except:
            return str(annotation)

    def _get_default_value(self, value: ast.expr) -> str:
        """Get default value as string"""
        if value is None:
            return None
        try:
            return ast.unparse(value)
        except:
            return str(value)

    def export_to_csv(self, output_dir: str = "analysis_output"):
        """Export analysis results to CSV files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export models
        models_file = output_path / f"models_{timestamp}.csv"
        with open(models_file, "w", newline="", encoding="utf-8") as f:
            if self.models:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "name",
                        "file_path",
                        "line_number",
                        "base_classes",
                        "field_count",
                        "is_pydantic",
                        "is_dataclass",
                        "docstring",
                    ],
                )
                writer.writeheader()
                for model in self.models:
                    writer.writerow(
                        {
                            "name": model.name,
                            "file_path": model.file_path,
                            "line_number": model.line_number,
                            "base_classes": ", ".join(model.base_classes),
                            "field_count": len(model.fields),
                            "is_pydantic": model.is_pydantic,
                            "is_dataclass": model.is_dataclass,
                            "docstring": (model.docstring or "")[:100],
                        }
                    )

        # Export model fields
        fields_file = output_path / f"model_fields_{timestamp}.csv"
        with open(fields_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["model_name", "file_path", "field_name", "field_type", "default_value"]
            )
            for model in self.models:
                for field in model.fields:
                    writer.writerow(
                        [
                            model.name,
                            model.file_path,
                            field["name"],
                            field["type"],
                            field.get("default", ""),
                        ]
                    )

        # Export functions
        functions_file = output_path / f"functions_{timestamp}.csv"
        with open(functions_file, "w", newline="", encoding="utf-8") as f:
            if self.functions:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "name",
                        "file_path",
                        "line_number",
                        "class_name",
                        "param_count",
                        "return_type",
                        "is_async",
                        "decorators",
                    ],
                )
                writer.writeheader()
                for func in self.functions:
                    writer.writerow(
                        {
                            "name": func.name,
                            "file_path": func.file_path,
                            "line_number": func.line_number,
                            "class_name": func.class_name or "",
                            "param_count": len(func.parameters),
                            "return_type": func.return_type or "",
                            "is_async": func.is_async,
                            "decorators": ", ".join(func.decorators),
                        }
                    )

        # Export request/response mappings
        mappings_file = output_path / f"req_resp_mappings_{timestamp}.csv"
        with open(mappings_file, "w", newline="", encoding="utf-8") as f:
            if self.mappings:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "function_name",
                        "file_path",
                        "http_method",
                        "endpoint",
                        "request_models",
                        "response_models",
                    ],
                )
                writer.writeheader()
                for mapping in self.mappings:
                    writer.writerow(
                        {
                            "function_name": mapping.function_name,
                            "file_path": mapping.file_path,
                            "http_method": mapping.http_method or "",
                            "endpoint": mapping.endpoint or "",
                            "request_models": ", ".join(mapping.request_models),
                            "response_models": ", ".join(mapping.response_models),
                        }
                    )

        print(f"Ô£ô Exported to CSV files in '{output_dir}/'")
        print(f"  - {models_file.name} ({len(self.models)} models)")
        print(f"  - {fields_file.name} (model fields)")
        print(f"  - {functions_file.name} ({len(self.functions)} functions)")
        print(f"  - {mappings_file.name} ({len(self.mappings)} mappings)")

        return output_path

    def export_to_json(self, output_file: str = None):
        """Export analysis results to JSON"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"analysis_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "models": [asdict(m) for m in self.models],
            "functions": [asdict(f) for f in self.functions],
            "mappings": [asdict(m) for m in self.mappings],
            "summary": {
                "total_models": len(self.models),
                "total_functions": len(self.functions),
                "total_mappings": len(self.mappings),
                "pydantic_models": sum(1 for m in self.models if m.is_pydantic),
                "dataclasses": sum(1 for m in self.models if m.is_dataclass),
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Ô£ô Exported to JSON: {output_file}")
        return output_file

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 60)
        print("CODE ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Root Path: {self.root_path}")
        print(f"\nModels Found: {len(self.models)}")
        print(f"  - Pydantic Models: {sum(1 for m in self.models if m.is_pydantic)}")
        print(f"  - Dataclasses: {sum(1 for m in self.models if m.is_dataclass)}")
        print(f"\nFunctions Found: {len(self.functions)}")
        print(f"  - Async Functions: {sum(1 for f in self.functions if f.is_async)}")
        print(f"\nRequest/Response Mappings: {len(self.mappings)}")

        if self.models:
            print("\nTop Models:")
            for model in self.models[:5]:
                print(
                    f"  ÔÇó {model.name} ({len(model.fields)} fields) - {model.file_path}"
                )

        if self.mappings:
            print("\nAPI Endpoints:")
            for mapping in self.mappings[:5]:
                method = mapping.http_method or "FUNC"
                endpoint = mapping.endpoint or f"/{mapping.function_name}"
                print(f"  ÔÇó {method:6} {endpoint}")
                if mapping.request_models:
                    print(f"         ÔåÉ {', '.join(mapping.request_models)}")
                if mapping.response_models:
                    print(f"         ÔåÆ {', '.join(mapping.response_models)}")

        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze Python code for models and functions"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)",
    )
    parser.add_argument("--csv", action="store_true", help="Export to CSV files")
    parser.add_argument("--json", action="store_true", help="Export to JSON file")
    parser.add_argument(
        "--output-dir", default="analysis_output", help="Output directory for CSV files"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["venv", ".venv", "__pycache__"],
        help="Patterns to exclude",
    )

    args = parser.parse_args()

    analyzer = CodeAnalyzer(args.path)

    print(f"Analyzing code in: {analyzer.root_path}")
    analyzer.analyze_directory(exclude_patterns=args.exclude)

    analyzer.print_summary()

    if args.csv:
        analyzer.export_to_csv(args.output_dir)

    if args.json:
        analyzer.export_to_json()

    if not args.csv and not args.json:
        print("Use --csv or --json to export results")


if __name__ == "__main__":
    main()
