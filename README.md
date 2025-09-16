# LGBT Laws Scraper - Peru

A comprehensive scraper to find and analyze laws related to LGBT rights in Peru's Congress across different historical periods. This tool is designed for academic research comparing democracy and LGBT rights between Brazil and Peru.

## Overview

This project provides automated tools to search, extract, and analyze LGBT-related legislation from Peru's Congress database across multiple historical periods (2006-present). It includes specialized scrapers for different eras, from modern API-based extraction to legacy Lotus Notes systems.

## 🏗️ Project Structure

```
lgtb-peru-law/
├── README.md
├── pyproject.toml
├── main.py                     # Main CLI interface
├── scrapers/                   # Core scraper modules
│   ├── __init__.py
│   ├── base.py                 # Base scraper with shared functionality
│   ├── current/                # Current period (2021+)
│   │   ├── __init__.py
│   │   └── api_scraper.py      # API-based scraper
│   ├── historical/             # Historical periods
│   │   ├── __init__.py
│   │   ├── scraper_2016.py     # 2016-2021 period
│   │   ├── scraper_2011.py     # 2011-2016 period
│   │   └── scraper_2006.py     # 2006-2011 period (experimental)
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── search_terms.py     # LGBT search terms database
│       └── export.py           # Data export utilities
└── data/                       # Data storage
    ├── raw/                    # Raw scraped data
    ├── processed/              # Processed/cleaned data
    └── exports/                # Final export files (CSV, JSON, TXT)
```

## ✨ Features

- **Multi-Period Coverage**: Covers 15+ years of legislation (2006-present)
- **API-Based Scraping**: Uses Peru Congress official API for current period
- **Historical Web Scraping**: Custom scrapers for legacy systems
- **Comprehensive Search**: 70+ LGBT-related terms in Spanish
- **Multiple Output Formats**: JSON, CSV, and human-readable summaries
- **Modular Architecture**: Clean separation by time periods and functionality
- **Research-Ready Data**: Structured output suitable for academic analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager

### Installation

```bash
# Install dependencies
uv sync
```

### Usage

```bash
# Scrape current period (2021+) using API
python main.py --current

# Scrape specific historical period
python main.py --historical 2016  # 2016-2021
python main.py --historical 2011  # 2011-2016

# Scrape all available periods
python main.py --all

# Run in test mode (limited results)
python main.py --current --test
```

### Individual Scrapers

You can also run individual scrapers directly:

```bash
# Current API scraper
uv run python scrapers/current/api_scraper.py

# Historical scrapers
uv run python scrapers/historical/scraper_2016.py
uv run python scrapers/historical/scraper_2011.py
```

## 📊 Data Coverage

| Period | Scraper | Status | Data Source |
|--------|---------|---------|-------------|
| 2021+ | API | ✅ Active | Modern Congress API |
| 2016-2021 | Web | ✅ Active | 2016-2021 Portal |
| 2011-2016 | Web | ✅ Active | 2011-2016 Portal |
| 2006-2011 | Web | ⚠️ Experimental | Lotus Notes System |

## 🔍 Search Terms

The scraper searches for 70+ LGBT-related terms including:

**Identity Terms**: `LGBT`, `LGBTI`, `LGBTIQ`, `gay`, `lesbiana`, `trans`, `bisexual`, `queer`, `intersex`

**Legal Concepts**: `matrimonio igualitario`, `unión civil`, `identidad de género`, `orientación sexual`

**Rights & Discrimination**: `no discriminación`, `igualdad`, `crímenes de odio`, `homofobia`, `transfobia`

**Legal Processes**: `cambio de nombre`, `rectificación de sexo`, `reasignación de sexo`

## 📁 Output Files

Results are automatically organized in `data/exports/`:

- `lgbt_laws_{period}_results.json` - Complete detailed results
- `lgbt_laws_{period}.csv` - Spreadsheet format for analysis  
- `lgbt_laws_{period}_summary.txt` - Human-readable summary

## 📋 Data Structure

Each law entry includes:

```json
{
  "search_term_used": "identidad de género",
  "found_terms": ["identidad de género", "transgénero"],
  "url": "https://...",
  "title": "LEY DE IDENTIDAD DE GÉNERO", 
  "law_number": "02194/2021-CR",
  "date": "2022-05-30",
  "status": "EN COMISIÓN",
  "summary": "Propone Ley de Identidad de Género...",
  "authors": "...",
  "proponent": "Congreso",
  "year": "2021+",
  "scraped_at": "2024-XX-XX"
}
```

## 🎓 Research Context

This tool supports comparative research on:

- **Democracy and LGBT Rights**: How democratic processes affect LGBT legislation
- **Cross-Country Analysis**: Comparing legislative patterns between Brazil and Peru  
- **Policy Evolution**: Tracking changes in LGBT rights legislation over time
- **Institutional Analysis**: Understanding how different political systems approach LGBT issues
- **Historical Trends**: Long-term patterns in LGBT rights advancement

## 🔧 Technical Details

### API Endpoints

- **Search**: `https://wb2server.congreso.gob.pe/spley-portal-service/proyecto-ley/lista-con-filtro`
- **Details**: `https://wb2server.congreso.gob.pe/spley-portal-service/expediente/{period}/{id}`

### Historical Systems

- **2016-2021**: Web portal with structured search
- **2011-2016**: Legacy web system with different field names
- **2006-2011**: Lotus Notes/Domino database (experimental)

### VPN Requirements

Some periods may require VPN access due to geographic restrictions:

```bash
# Enable VPN before running scrapers if you encounter 403 errors
python main.py --current  # May need VPN for API access
```

## 📈 Development

### Adding New Periods

1. Create new scraper in `scrapers/historical/`
2. Inherit from `BaseLGBTScraper`
3. Implement period-specific parsing
4. Add to main CLI interface

### Contributing

- Follow existing code patterns
- Use shared utilities from `scrapers/utils/`
- Test with limited results first
- Document any new search terms or data fields

## 📚 Academic Use

When using this data for research:

- **Cite Methodology**: Document search terms and time periods
- **Data Currency**: Legislative data changes frequently  
- **Context**: Analyze laws within broader political context
- **Ethics**: Follow ethical guidelines for political research
- **Reproducibility**: Save search parameters and timestamps

## ⚠️ Notes

- The 2006-2011 scraper is experimental and may have limited functionality
- VPN may be required for some endpoints
- Rate limiting is implemented to be respectful to Congress servers
- Some historical data may have inconsistent formatting

---

*This scraper was developed as part of comparative research on democracy and LGBT rights in Latin America. For academic inquiries, please refer to the research context and methodology sections.*