# LGBT Laws Scraper - Peru

A comprehensive scraper to find and analyze laws related to LGBT rights in Peru's Congress across different historical periods. This tool is designed for academic research comparing democracy and LGBT rights between Brazil and Peru.

## Overview

This project provides automated tools to search, extract, and analyze LGBT-related legislation from Peru's Congress database across multiple historical periods (1995-present). It includes specialized scrapers for different eras, from modern API-based extraction to legacy web systems.

## 🏗️ Project Structure

```
lgtb-peru-law/
├── README.md
├── pyproject.toml
├── main.py                     # Main CLI interface
├── scrapers/                   # Core scraper modules
│   ├── __init__.py
│   ├── base.py                 # Base scraper with shared functionality
│   ├── periods/                # Period-specific scrapers
│   │   ├── __init__.py
│   │   ├── scraper_2021.py     # 2021+ API-based scraper
│   │   ├── scraper_2016.py     # 2016-2021 period
│   │   ├── scraper_2011.py     # 2011-2016 period
│   │   ├── scraper_2006.py     # 2006-2011 period
│   │   ├── scraper_2001.py     # 2001-2006 period
│   │   ├── scraper_2000.py     # 2000-2001 period
│   │   └── scraper_1995.py     # 1995-2000 period
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── search_terms.py     # LGBT search terms database
│       └── export.py           # Data export utilities
└── data/                       # Data storage
    └── exports/                # Export files (CSV, JSON, TXT)
```

## ✨ Features

- **Multi-Period Coverage**: Covers 25+ years of legislation (1995-present)
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
uv run python main.py --current

# Scrape specific historical period
uv run python main.py --period 2016  # 2016-2021
uv run python main.py --period 2011  # 2011-2016
uv run python main.py --period 2006  # 2006-2011
uv run python main.py --period 2001  # 2001-2006
uv run python main.py --period 2000  # 2000-2001
uv run python main.py --period 1995  # 1995-2000

# Scrape all available periods
uv run python main.py --all

# Run in test mode (limited results)
uv run python main.py --current --test
```

### Individual Scrapers

You can also run individual scrapers directly:

```bash
# Individual scrapers
uv run python -m scrapers.periods.scraper_2021
uv run python -m scrapers.periods.scraper_2016
uv run python -m scrapers.periods.scraper_2011
uv run python -m scrapers.periods.scraper_2006
uv run python -m scrapers.periods.scraper_2001
uv run python -m scrapers.periods.scraper_2000
uv run python -m scrapers.periods.scraper_1995
```

## 📊 Data Coverage

| Period | Scraper | Status | Data Source |
|--------|---------|---------|-------------|
| 2021+ | API | ✅ Active | Modern Congress API |
| 2016-2021 | Web | ✅ Active | 2016-2021 Portal |
| 2011-2016 | Web | ✅ Active | 2011-2016 Portal |
| 2006-2011 | Web | ✅ Active | 2006-2011 Portal |
| 2001-2006 | Web | ✅ Active | 2001-2006 Portal |
| 2000-2001 | Web | ✅ Active | 2000-2001 Portal |
| 1995-2000 | Web | ✅ Active | 1995-2000 Portal |

## 🔍 Search Terms

The scraper searches for 70+ LGBT-related terms including:

**Identity Terms**: `LGBT`, `LGBTI`, `LGBTIQ`, `gay`, `lesbiana`, `trans`, `bisexual`, `queer`, `intersex`

**Legal Concepts**: `matrimonio igualitario`, `unión civil`, `identidad de género`, `orientación sexual`

**Rights & Discrimination**: `no discriminación`, `igualdad`, `crímenes de odio`, `homofobia`, `transfobia`

**Legal Processes**: `cambio de nombre`, `rectificación de sexo`, `reasignación de sexo`

> [!NOTE]  
> [List of all the words used can be founded in this link](https://github.com/ArthurJordao/lgtb-peru-laws-web-scrapping/blob/main/scrapers/utils/search_terms.py#L8-L83)

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
- **2006-2011**: Legacy web portal with hidden form fields
- **2001-2006**: Legacy web system with HTML parsing challenges
- **2000-2001**: Legacy NSF database with Start/Count pagination
- **1995-2000**: Oldest legacy system with malformed HTML patterns

### VPN Requirements

Some periods may require VPN access due to geographic restrictions:

```bash
# Enable VPN before running scrapers if you encounter 403 errors
uv run python main.py --current  # May need VPN for API access
```

## 📈 Development

### Adding New Periods

1. Create new scraper in `scrapers/periods/`
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

- VPN may be required for some endpoints
- Rate limiting is implemented to be respectful to Congress servers
- Some historical data may have inconsistent formatting

---

*This scraper was developed as part of comparative research on democracy and LGBT rights in Latin America. For academic inquiries, please refer to the research context and methodology sections.*
