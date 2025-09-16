"""
Data export utilities for Peru LGBT law scrapers
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path


class DataExporter:
    """Utility class for exporting scraped law data in multiple formats"""

    def __init__(self, output_dir="data/exports"):
        # Make path relative to project root, not current working directory
        if not Path(output_dir).is_absolute():
            # Find project root by looking for pyproject.toml
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "pyproject.toml").exists():
                    self.output_dir = current / output_dir
                    break
                current = current.parent
            else:
                # Fallback if pyproject.toml not found
                self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_results(self, results, period_name):
        """Save results in multiple formats (JSON, CSV, TXT)"""
        if not results:
            print(f"No LGBT-related laws found for {period_name} period.")
            return

        # Save detailed JSON
        json_file = self.output_dir / f"lgbt_laws_{period_name}_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Save as CSV - flatten complex fields
        csv_results = self._flatten_for_csv(results)
        csv_file = self.output_dir / f"lgbt_laws_{period_name}.csv"
        df = pd.DataFrame(csv_results)
        df.to_csv(csv_file, index=False, encoding="utf-8")

        # Create human-readable summary
        txt_file = self.output_dir / f"lgbt_laws_{period_name}_summary.txt"
        self._create_summary(results, txt_file, period_name)

        print(f"Results saved:")
        print(f"  - {json_file} (detailed)")
        print(f"  - {csv_file} (spreadsheet)")
        print(f"  - {txt_file} (human readable)")

    def _flatten_for_csv(self, results):
        """Flatten complex fields for CSV export"""
        csv_results = []
        for result in results:
            csv_result = result.copy()

            # Flatten authors
            if isinstance(csv_result.get("authors"), list):
                author_names = [
                    author.get("name", "") if isinstance(author, dict) else str(author)
                    for author in csv_result["authors"]
                ]
                csv_result["authors"] = "; ".join(author_names)

            # Flatten tracking
            if isinstance(csv_result.get("tracking"), list):
                tracking_summary = [
                    f"{t.get('date', '')}: {t.get('action', '')[:50]}..."
                    for t in csv_result["tracking"][:3]  # First 3 entries
                ]
                csv_result["tracking"] = "; ".join(tracking_summary)

            # Flatten committees
            if isinstance(csv_result.get("committees"), list):
                csv_result["committees"] = "; ".join(csv_result["committees"])

            csv_results.append(csv_result)

        return csv_results

    def _create_summary(self, results, txt_file, period_name):
        """Create human-readable summary file"""
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(f"LEYES SOBRE DERECHOS LGBT EN PERÚ - {period_name.upper()}\\n")
            f.write("=" * 50 + "\\n")
            f.write(
                f"Búsqueda realizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
            )
            f.write(f"Total de proyectos encontrados: {len(results)}\\n\\n")

            for i, law in enumerate(results, 1):
                f.write(
                    f"{i}. {law.get('law_number', 'N/A')} - {law.get('title', 'Sin título')[:80]}...\\n"
                )
                f.write(f"   Fecha: {law.get('date', 'N/A')}\\n")
                f.write(f"   Estado: {law.get('status', 'N/A')}\\n")
                f.write(f"   Proponente: {law.get('proponent', 'N/A')}\\n")

                if law.get("parliamentary_group"):
                    f.write(f"   Grupo Parlamentario: {law['parliamentary_group']}\\n")
                if law.get("period"):
                    f.write(f"   Período: {law['period']}\\n")

                # Handle authors field
                authors = law.get("authors", [])
                if isinstance(authors, list) and authors:
                    author_names = [
                        author.get("name", "")
                        if isinstance(author, dict)
                        else str(author)
                        for author in authors
                    ]
                    f.write(f"   Autores: {', '.join(author_names)}\\n")
                elif isinstance(authors, str) and authors:
                    f.write(f"   Autores: {authors}\\n")

                f.write(
                    f"   Término de búsqueda: {law.get('search_term_used', 'N/A')}\\n"
                )
                f.write(
                    f"   Términos encontrados: {', '.join(law.get('found_terms', []))}\\n"
                )
                f.write(f"   URL: {law.get('url', 'N/A')}\\n")
                f.write(
                    f"   Resumen: {law.get('summary', 'Sin resumen')[:150]}...\\n\\n"
                )
