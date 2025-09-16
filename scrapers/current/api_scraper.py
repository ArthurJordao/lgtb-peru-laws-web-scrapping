import requests
import json
import time
from datetime import datetime
from ..base import BaseLGBTScraper


class PeruLGBTAPIScraper(BaseLGBTScraper):
    def __init__(self):
        super().__init__("api_current")

        # API endpoints discovered
        self.search_api = "https://wb2server.congreso.gob.pe/spley-portal-service/proyecto-ley/lista-con-filtro"
        self.detail_api = (
            "https://wb2server.congreso.gob.pe/spley-portal-service/expediente"
        )

    def setup_session(self):
        """Override base setup for API-specific headers"""
        super().setup_session()
        # Update with API-specific headers
        api_headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": "https://wb2server.congreso.gob.pe/spley-portal/",
            "Origin": "https://wb2server.congreso.gob.pe",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        self.session.headers.update(api_headers)

    def search_laws(self, search_term, max_results=50):
        """Search for laws using the discovered API endpoint"""
        print(f"Searching for: {search_term}")

        payload = {
            "perParId": 2021,  # Current parliamentary period
            "perLegId": None,
            "comisionId": None,
            "estadoId": None,
            "congresistaId": None,
            "grupoParlamentarioId": None,
            "proponenteId": None,
            "legislaturaId": None,
            "fecPresentacionDesde": None,
            "fecPresentacionHasta": None,
            "pleyNum": None,
            "palabras": search_term,  # This is the search field
            "tipoFirmanteId": None,
            "pageSize": max_results,
            "rowStart": 0,
        }

        try:
            response = self.session.post(self.search_api, json=payload, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 200 and data.get("status") == "success":
                    projects = data.get("data", {}).get("proyectos", [])
                    total_rows = data.get("data", {}).get("rowsTotal", 0)

                    print(f"  Found {len(projects)} results (total: {total_rows})")

                    for project in projects:
                        # Get detailed information for each project
                        self.get_project_details(project, search_term)
                        time.sleep(0.5)  # Be respectful

                    return len(projects)
                else:
                    print(f"  API error: {data}")
                    return 0
            else:
                print(f"  HTTP error {response.status_code}")
                return 0

        except Exception as e:
            print(f"  Search failed: {e}")
            return 0

    def get_project_details(self, project, search_term):
        """Get detailed information about a specific project"""
        per_par_id = project.get("perParId")
        pley_num = project.get("pleyNum")

        if not per_par_id or not pley_num:
            return

        # Find the pleyId - we need this for the detail API
        # The API seems to use pleyId for details, but we have pleyNum from search
        # Let's try to construct the detail URL
        detail_url = f"{self.detail_api}/{per_par_id}/{pley_num}"

        try:
            response = self.session.get(detail_url, timeout=15)

            if response.status_code == 200:
                detail_data = response.json()

                if detail_data.get("code") == 200:
                    # Combine search result with detailed data
                    full_data = {
                        "search_term_used": search_term,
                        "basic_info": project,
                        "detailed_info": detail_data.get("data", {}),
                        "scraped_at": datetime.now().isoformat(),
                    }

                    self.results.append(full_data)

                    titulo = project.get("titulo", "Sin título")
                    estado = project.get("desEstado", "Sin estado")
                    fecha = project.get("fecPresentacion", "Sin fecha")

                    print(
                        f"    ✓ {project.get('proyectoLey', 'N/A')}: {titulo[:80]}..."
                    )
                    print(f"      Estado: {estado}, Fecha: {fecha}")
                else:
                    print(f"    Detail API error for {project.get('proyectoLey')}")
            else:
                print(
                    f"    Detail HTTP error {response.status_code} for {project.get('proyectoLey')}"
                )

        except Exception as e:
            print(f"    Detail fetch failed for {project.get('proyectoLey')}: {e}")

    def search_all_terms(self):
        """Search for all LGBT-related terms"""
        print("Starting LGBT rights law search using Peru Congress API...")
        print(f"Search terms: {', '.join(self.search_terms)}")
        print()

        total_found = 0

        for term in self.search_terms:
            try:
                found = self.search_laws(term)
                total_found += found
                time.sleep(1)  # Be respectful between searches

                if len(self.results) >= 50:  # Reasonable limit
                    print(f"Reached limit of 50 results, stopping search...")
                    break

            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break

        print(
            f"\nTotal search completed. Found {len(self.results)} LGBT-related laws/projects"
        )
        return total_found

    def save_results(self):
        """Save results in multiple formats"""
        if not self.results:
            print("No LGBT-related laws found.")
            return

        # Save detailed JSON
        with open("lgbt_laws_api_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Create a simplified version for easier reading
        simplified_results = []
        for result in self.results:
            basic = result["basic_info"]
            detailed = result["detailed_info"]

            simplified = {
                "proyecto_ley": basic.get("proyectoLey", "N/A"),
                "titulo": basic.get("titulo", "Sin título"),
                "estado": basic.get("desEstado", "Sin estado"),
                "fecha_presentacion": basic.get("fecPresentacion", "Sin fecha"),
                "proponente": basic.get("desProponente", "Sin proponente"),
                "autores": basic.get("autores", "Sin autores"),
                "search_term": result["search_term_used"],
                "sumilla": detailed.get("general", {}).get("sumilla", "Sin sumilla")
                if detailed
                else "Sin detalles",
                "comisiones": [
                    c.get("nombre", "Sin nombre")
                    for c in detailed.get("comisiones", [])
                ]
                if detailed
                else [],
                "url_detalle": f"https://wb2server.congreso.gob.pe/spley-portal/#/expediente/main/{basic.get('perParId')}/{basic.get('pleyNum')}",
            }
            simplified_results.append(simplified)

        # Save simplified JSON
        with open("lgbt_laws_simplified.json", "w", encoding="utf-8") as f:
            json.dump(simplified_results, f, indent=2, ensure_ascii=False)

        # Save as CSV
        df = pd.DataFrame(simplified_results)
        df.to_csv("lgbt_laws_peru.csv", index=False, encoding="utf-8")

        # Create human-readable summary
        with open("lgbt_laws_summary.txt", "w", encoding="utf-8") as f:
            f.write("LEYES SOBRE DERECHOS LGBT EN PERÚ - RESUMEN\n")
            f.write("=" * 50 + "\n")
            f.write(
                f"Búsqueda realizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Total de proyectos encontrados: {len(simplified_results)}\n\n")

            for i, law in enumerate(simplified_results, 1):
                f.write(f"{i}. {law['proyecto_ley']}\n")
                f.write(f"   Título: {law['titulo']}\n")
                f.write(f"   Estado: {law['estado']}\n")
                f.write(f"   Fecha: {law['fecha_presentacion']}\n")
                f.write(f"   Término de búsqueda: {law['search_term']}\n")
                f.write(
                    f"   Comisiones: {', '.join(law['comisiones']) if law['comisiones'] else 'Ninguna'}\n"
                )
                f.write(f"   Sumilla: {law['sumilla'][:200]}...\n")
                f.write(f"   URL: {law['url_detalle']}\n\n")

        print(f"Results saved:")
        print(f"  - lgbt_laws_api_results.json (detailed)")
        print(f"  - lgbt_laws_simplified.json (simplified)")
        print(f"  - lgbt_laws_peru.csv (spreadsheet)")
        print(f"  - lgbt_laws_summary.txt (human readable)")

    def run(self):
        """Main execution method"""
        try:
            self.search_all_terms()
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            self.save_results()


if __name__ == "__main__":
    api = PeruLGBTAPIScraper()
    api.run()
