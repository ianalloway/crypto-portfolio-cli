#!/usr/bin/env python3
"""
Crypto Portfolio CLI - Track your cryptocurrency portfolio with live prices and terminal charts.
"""

import json
import os
from pathlib import Path
from typing import Optional

import click
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

try:
    import plotext as plt
    PLOTEXT_AVAILABLE = True
except ImportError:
    PLOTEXT_AVAILABLE = False

console = Console()

COINGECKO_API = "https://api.coingecko.com/api/v3"
CONFIG_FILE = Path.home() / ".portfolio.json"

COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "APE": "apecoin",
    "ARB": "arbitrum",
    "OP": "optimism",
    "NEAR": "near",
    "FTM": "fantom",
}


def load_portfolio() -> dict:
    """Load portfolio from config file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"holdings": {}, "currency": "USD", "alerts": {}}


def save_portfolio(portfolio: dict) -> None:
    """Save portfolio to config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def get_coin_id(symbol: str) -> str:
    """Get CoinGecko coin ID from symbol."""
    symbol = symbol.upper()
    return COIN_IDS.get(symbol, symbol.lower())


def fetch_prices(coin_ids: list[str], currency: str = "usd") -> dict:
    """Fetch current prices from CoinGecko."""
    ids = ",".join(coin_ids)
    url = f"{COINGECKO_API}/simple/price"
    params = {
        "ids": ids,
        "vs_currencies": currency.lower(),
        "include_24hr_change": "true",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        console.print(f"[red]Error fetching prices: {e}[/red]")
        return {}


def fetch_price_history(coin_id: str, days: int = 30, currency: str = "usd") -> list:
    """Fetch price history from CoinGecko."""
    url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
    params = {"vs_currency": currency.lower(), "days": days}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("prices", [])
    except requests.RequestException as e:
        console.print(f"[red]Error fetching price history: {e}[/red]")
        return []


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Crypto Portfolio CLI - Track your cryptocurrency portfolio."""
    pass


@cli.command()
@click.argument("coin")
@click.argument("amount", type=float)
def add(coin: str, amount: float):
    """Add holdings to your portfolio."""
    portfolio = load_portfolio()
    coin = coin.upper()
    
    if coin in portfolio["holdings"]:
        portfolio["holdings"][coin] += amount
        console.print(f"[green]Updated {coin}: now holding {portfolio['holdings'][coin]}[/green]")
    else:
        portfolio["holdings"][coin] = amount
        console.print(f"[green]Added {amount} {coin} to portfolio[/green]")
    
    save_portfolio(portfolio)


@cli.command()
@click.argument("coin")
def remove(coin: str):
    """Remove a coin from your portfolio."""
    portfolio = load_portfolio()
    coin = coin.upper()
    
    if coin in portfolio["holdings"]:
        del portfolio["holdings"][coin]
        save_portfolio(portfolio)
        console.print(f"[green]Removed {coin} from portfolio[/green]")
    else:
        console.print(f"[yellow]{coin} not found in portfolio[/yellow]")


@cli.command()
def show():
    """Display your portfolio with current values."""
    portfolio = load_portfolio()
    holdings = portfolio.get("holdings", {})
    currency = portfolio.get("currency", "USD")
    
    if not holdings:
        console.print("[yellow]Portfolio is empty. Use 'add' command to add holdings.[/yellow]")
        return
    
    coin_ids = [get_coin_id(symbol) for symbol in holdings.keys()]
    prices = fetch_prices(coin_ids, currency)
    
    table = Table(title="Crypto Portfolio", show_header=True, header_style="bold cyan")
    table.add_column("Coin", style="bold")
    table.add_column("Amount", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("24h Change", justify="right")
    
    total_value = 0.0
    
    for symbol, amount in holdings.items():
        coin_id = get_coin_id(symbol)
        price_data = prices.get(coin_id, {})
        price = price_data.get(currency.lower(), 0)
        change_24h = price_data.get(f"{currency.lower()}_24h_change", 0)
        value = price * amount
        total_value += value
        
        change_color = "green" if change_24h >= 0 else "red"
        change_str = f"[{change_color}]{change_24h:+.2f}%[/{change_color}]"
        
        table.add_row(
            symbol,
            f"{amount:,.4f}",
            f"${price:,.2f}",
            f"${value:,.2f}",
            change_str,
        )
    
    console.print(table)
    console.print(f"\n[bold]Total Portfolio Value: ${total_value:,.2f}[/bold]")


@cli.command()
@click.argument("coins", nargs=-1)
def prices(coins: tuple):
    """Get live prices for specified coins."""
    if not coins:
        console.print("[yellow]Please specify at least one coin symbol.[/yellow]")
        return
    
    coin_ids = [get_coin_id(c) for c in coins]
    price_data = fetch_prices(coin_ids, "usd")
    
    table = Table(title="Live Crypto Prices", show_header=True, header_style="bold cyan")
    table.add_column("Coin", style="bold")
    table.add_column("Price (USD)", justify="right")
    table.add_column("24h Change", justify="right")
    
    for symbol in coins:
        coin_id = get_coin_id(symbol)
        data = price_data.get(coin_id, {})
        price = data.get("usd", 0)
        change = data.get("usd_24h_change", 0)
        
        change_color = "green" if change >= 0 else "red"
        change_str = f"[{change_color}]{change:+.2f}%[/{change_color}]"
        
        table.add_row(symbol.upper(), f"${price:,.2f}", change_str)
    
    console.print(table)


@cli.command()
@click.argument("coin")
@click.option("--days", "-d", default=30, help="Number of days of history")
def chart(coin: str, days: int):
    """Show price history chart for a coin."""
    if not PLOTEXT_AVAILABLE:
        console.print("[red]plotext not installed. Run: pip install plotext[/red]")
        return
    
    coin_id = get_coin_id(coin)
    history = fetch_price_history(coin_id, days)
    
    if not history:
        console.print(f"[red]Could not fetch price history for {coin}[/red]")
        return
    
    prices_list = [p[1] for p in history]
    
    plt.clear_figure()
    plt.plot(prices_list)
    plt.title(f"{coin.upper()} Price - Last {days} Days")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.show()


@cli.command()
def allocation():
    """Show portfolio allocation chart."""
    if not PLOTEXT_AVAILABLE:
        console.print("[red]plotext not installed. Run: pip install plotext[/red]")
        return
    
    portfolio = load_portfolio()
    holdings = portfolio.get("holdings", {})
    currency = portfolio.get("currency", "USD")
    
    if not holdings:
        console.print("[yellow]Portfolio is empty.[/yellow]")
        return
    
    coin_ids = [get_coin_id(symbol) for symbol in holdings.keys()]
    prices = fetch_prices(coin_ids, currency)
    
    values = {}
    for symbol, amount in holdings.items():
        coin_id = get_coin_id(symbol)
        price = prices.get(coin_id, {}).get(currency.lower(), 0)
        values[symbol] = price * amount
    
    total = sum(values.values())
    if total == 0:
        console.print("[yellow]Could not calculate portfolio values.[/yellow]")
        return
    
    labels = list(values.keys())
    sizes = [v / total * 100 for v in values.values()]
    
    plt.clear_figure()
    plt.bar(labels, sizes)
    plt.title("Portfolio Allocation (%)")
    plt.ylabel("Percentage")
    plt.show()


@cli.command()
@click.argument("coin")
@click.argument("target_price", type=float)
def alert(coin: str, target_price: float):
    """Set a price alert for a coin."""
    portfolio = load_portfolio()
    coin = coin.upper()
    
    if "alerts" not in portfolio:
        portfolio["alerts"] = {}
    
    portfolio["alerts"][coin] = target_price
    save_portfolio(portfolio)
    
    console.print(f"[green]Alert set: {coin} at ${target_price:,.2f}[/green]")


@cli.command()
@click.option("--format", "-f", type=click.Choice(["json", "csv"]), default="json")
@click.option("--output", "-o", default="portfolio_export")
def export(format: str, output: str):
    """Export portfolio to file."""
    portfolio = load_portfolio()
    holdings = portfolio.get("holdings", {})
    
    if format == "json":
        filename = f"{output}.json"
        with open(filename, "w") as f:
            json.dump(portfolio, f, indent=2)
    else:
        filename = f"{output}.csv"
        with open(filename, "w") as f:
            f.write("coin,amount\n")
            for coin, amount in holdings.items():
                f.write(f"{coin},{amount}\n")
    
    console.print(f"[green]Portfolio exported to {filename}[/green]")


@cli.command()
@click.argument("currency")
def set_currency(currency: str):
    """Set the display currency (USD, EUR, GBP, etc.)."""
    portfolio = load_portfolio()
    portfolio["currency"] = currency.upper()
    save_portfolio(portfolio)
    console.print(f"[green]Currency set to {currency.upper()}[/green]")


if __name__ == "__main__":
    cli()
