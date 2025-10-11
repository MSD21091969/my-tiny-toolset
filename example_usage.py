"""
Example usage of the code analyzer
"""

from code_analyzer import CodeAnalyzer
from excel_exporter import export_to_excel, EXCEL_AVAILABLE


def analyze_current_directory():
    """Analyze code in current directory"""
    print("=" * 60)
    print("CODE ANALYZER - Request/Response Model Mapping")
    print("=" * 60)

    # Create analyzer
    analyzer = CodeAnalyzer(".")

    # Analyze all Python files
    print("\nAnalyzing Python files...")
    analyzer.analyze_directory(
        exclude_patterns=["venv", ".venv", "__pycache__", "analysis_output"]
    )

    # Print summary
    analyzer.print_summary()

    # Export to CSV
    print("\nExporting to CSV...")
    analyzer.export_to_csv("analysis_output")

    # Export to JSON
    print("\nExporting to JSON...")
    analyzer.export_to_json("analysis_output/analysis.json")

    # Export to Excel if available
    if EXCEL_AVAILABLE:
        print("\nExporting to Excel...")
        export_to_excel(analyzer, "analysis_output/code_analysis.xlsx")
    else:
        print("\nExcel export not available (install openpyxl for Excel support)")

    print("\n" + "=" * 60)
    print("Analysis complete! Check the 'analysis_output' folder.")
    print("=" * 60)


def analyze_specific_directory(path: str):
    """Analyze code in specific directory"""
    analyzer = CodeAnalyzer(path)
    analyzer.analyze_directory()
    analyzer.print_summary()
    analyzer.export_to_csv("analysis_output")

    if EXCEL_AVAILABLE:
        export_to_excel(analyzer, "analysis_output/code_analysis.xlsx")


if __name__ == "__main__":
    analyze_current_directory()
