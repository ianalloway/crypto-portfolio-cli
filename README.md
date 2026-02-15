# Crypto Portfolio CLI

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A command-line tool for tracking your cryptocurrency portfolio with live prices and terminal-based charts.

## Features

- **Live Price Tracking** - Real-time prices from CoinGecko API (no API key required)
- **Portfolio Management** - Add, remove, and update your holdings
- **Terminal Charts** - Visualize price history and portfolio allocation in your terminal
- **Multiple Currencies** - Support for USD, EUR, GBP, and more
- **Price Alerts** - Set alerts for price targets
- **Export Data** - Export portfolio to CSV or JSON

## Installation

```bash
# Clone the repository
git clone https://github.com/ianalloway/crypto-portfolio-cli.git
cd crypto-portfolio-cli

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python portfolio.py
```

## Quick Start

```bash
# Add holdings to your portfolio
python portfolio.py add BTC 0.5
python portfolio.py add ETH 2.0
python portfolio.py add SOL 50

# View your portfolio
python portfolio.py show

# Get live prices
python portfolio.py prices BTC ETH SOL

# Show price chart
python portfolio.py chart BTC --days 30

# Show portfolio allocation
python portfolio.py allocation
```

## Commands

| Command | Description |
|---------|-------------|
| `add <coin> <amount>` | Add holdings to portfolio |
| `remove <coin>` | Remove coin from portfolio |
| `show` | Display portfolio with current values |
| `prices <coins...>` | Get live prices for coins |
| `chart <coin>` | Show price history chart |
| `allocation` | Show portfolio allocation pie chart |
| `alert <coin> <price>` | Set price alert |
| `export` | Export portfolio to file |

## Configuration

Create a `.portfolio.json` file in your home directory or use the CLI to manage your holdings:

```json
{
  "holdings": {
    "BTC": 0.5,
    "ETH": 2.0,
    "SOL": 50
  },
  "currency": "USD"
}
```

## Tech Stack

- Python 3.8+
- Rich (terminal formatting)
- Plotext (terminal charts)
- Requests (API calls)
- Click (CLI framework)

## API

This tool uses the free CoinGecko API which requires no authentication. Rate limits apply (10-30 calls/minute for free tier).

## Author

**Ian Alloway** - Data Scientist & AI Specialist

- Portfolio: [ianalloway.xyz](https://ianalloway.xyz)
- GitHub: [@ianalloway](https://github.com/ianalloway)
- Twitter: [@ianallowayxyz](https://x.com/ianallowayxyz)

## License

MIT License - see [LICENSE](LICENSE) for details.
