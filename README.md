# LGBT Laws Scraper - Peru

A comprehensive scraper to find and analyze laws related to LGBT rights in Peru's Congress. This tool is designed for academic research comparing democracy and LGBT rights between Brazil and Peru.

## Overview

This project provides automated tools to search, extract, and analyze LGBT-related legislation from Peru's Congress database. It uses the official Congress API endpoints to gather comprehensive information about law proposals, their status, and related documentation.

## Features

- **API-Based Scraping**: Uses Peru Congress official API endpoints for reliable data extraction
- **Comprehensive Search Terms**: Searches for 70+ LGBT-related terms in Spanish
- **Multiple Output Formats**: Results saved as JSON, CSV, and human-readable text
- **Detailed Law Information**: Extracts full metadata including authors, committees, status, and documents
- **Research-Ready Data**: Structured output suitable for academic analysis

## Usage

### Prerequisites

- Python 3.11+
- UV package manager

### Installation

```bash
# Install dependencies
uv sync
```

### Running the Scraper

```bash
# Run the main API scraper
uv run python api_lgbt_scraper.py

# Or run the alternative web scraper (less reliable)
uv run python main.py
```

## Search Terms

The scraper searches for laws containing LGBT-related terms including:

- Identity terms: `LGBT`, `LGBTI`, `LGBTIQ`, `gay`, `lesbiana`, `trans`, `bisexual`, `queer`
- Legal concepts: `matrimonio igualitario`, `unión civil`, `identidad de género`, `orientación sexual`
- Rights terms: `no discriminación`, `igualdad`, `derechos reproductivos`
- Social issues: `homofobia`, `transfobia`, `crímenes de odio`

## Output Files

The scraper generates several output files:

- `lgbt_laws_api_results.json` - Complete detailed results with full API responses
- `lgbt_laws_simplified.json` - Simplified version with key information
- `lgbt_laws_peru.csv` - Spreadsheet format for data analysis
- `lgbt_laws_summary.txt` - Human-readable summary report

## Data Structure

Each law entry includes:

```json
{
  "proyecto_ley": "02194/2021-CR",
  "titulo": "LEY DE IDENTIDAD DE GÉNERO",
  "estado": "EN COMISIÓN",
  "fecha_presentacion": "2022-05-30T00:00:00.000-0500",
  "proponente": "Congreso-Actualización",
  "autores": "...",
  "search_term": "identidad de género",
  "sumilla": "Propone Ley de Identidad de Género...",
  "comisiones": ["Constitución y Reglamento"],
  "url_detalle": "https://wb2server.congreso.gob.pe/spley-portal/..."
}
```

## Research Context

This tool is part of a comparative study analyzing:

- **Democracy and LGBT Rights**: How democratic processes affect LGBT legislation
- **Cross-Country Analysis**: Comparing legislative patterns between Brazil and Peru  
- **Policy Evolution**: Tracking changes in LGBT rights legislation over time
- **Institutional Factors**: Understanding how different political systems approach LGBT issues

## API Endpoints

The scraper uses Peru Congress official API:

- **Search API**: `https://wb2server.congreso.gob.pe/spley-portal-service/proyecto-ley/lista-con-filtro`
- **Details API**: `https://wb2server.congreso.gob.pe/spley-portal-service/expediente/{period}/{id}`

## Academic Use

When using this data for research, please consider:

- **Data Currency**: Legislative data changes frequently
- **Context**: Individual laws should be analyzed within broader political context  
- **Methodology**: Document search terms and time periods used
- **Ethics**: Respect privacy and ethical guidelines for political research

---

*This scraper was developed as part of comparative research on democracy and LGBT rights in Latin America.*