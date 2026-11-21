"""Tests for the crypto portfolio CLI."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


# Mock the portfolio module functions
def test_get_coin_id():
    """Test coin ID lookup."""
    from portfolio import get_coin_id
    
    assert get_coin_id("BTC") == "bitcoin"
    assert get_coin_id("ETH") == "ethereum"
    assert get_coin_id("SOL") == "solana"
    assert get_coin_id("btc") == "bitcoin"  # Case insensitive
    assert get_coin_id("UNKNOWN") == "unknown"  # Falls back to lowercase


def test_load_portfolio_empty():
    """Test loading portfolio when no file exists."""
    from portfolio import load_portfolio
    
    with patch.object(Path, 'exists', return_value=False):
        portfolio = load_portfolio()
        assert portfolio == {"holdings": {}, "currency": "USD", "alerts": {}}


def test_load_portfolio_existing():
    """Test loading portfolio from existing file."""
    from portfolio import load_portfolio
    
    test_data = {"holdings": {"BTC": 1.0}, "currency": "EUR", "alerts": {}}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)
    
    try:
        with patch('portfolio.CONFIG_FILE', temp_path):
            portfolio = load_portfolio()
            assert portfolio["holdings"]["BTC"] == 1.0
            assert portfolio["currency"] == "EUR"
    finally:
        temp_path.unlink()


def test_save_portfolio():
    """Test saving portfolio to file."""
    from portfolio import save_portfolio
    
    test_data = {"holdings": {"ETH": 2.5}, "currency": "USD", "alerts": {}}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        with patch('portfolio.CONFIG_FILE', temp_path):
            save_portfolio(test_data)
            
            with open(temp_path) as f:
                saved = json.load(f)
            
            assert saved["holdings"]["ETH"] == 2.5
    finally:
        temp_path.unlink()


@patch('portfolio.requests.get')
def test_fetch_prices_success(mock_get):
    """Test successful price fetching."""
    from portfolio import fetch_prices
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "bitcoin": {"usd": 50000, "usd_24h_change": 2.5}
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    prices = fetch_prices(["bitcoin"])
    assert "bitcoin" in prices
    assert prices["bitcoin"]["usd"] == 50000


@patch('portfolio.requests.get')
def test_fetch_prices_error(mock_get):
    """Test price fetching with network error."""
    import requests

    from portfolio import fetch_prices
    
    mock_get.side_effect = requests.RequestException("Network error")
    
    prices = fetch_prices(["bitcoin"])
    assert prices == {}


def test_coin_ids_mapping():
    """Test that common coins are mapped correctly."""
    from portfolio import COIN_IDS
    
    assert "BTC" in COIN_IDS
    assert "ETH" in COIN_IDS
    assert "SOL" in COIN_IDS
    assert COIN_IDS["BTC"] == "bitcoin"
    assert COIN_IDS["ETH"] == "ethereum"


def test_eur_total_keeps_real_zero_prices_and_missing_change(monkeypatch):
    from click.testing import CliRunner

    import portfolio

    monkeypatch.setattr(portfolio, "load_portfolio", lambda: {"holdings": {"BTC": 2, "ETH": 1}, "currency": "EUR"})
    quotes = {"bitcoin": {"eur": 10, "eur_24h_change": None}, "ethereum": {"eur": 0}}
    monkeypatch.setattr(portfolio, "fetch_prices", lambda *args: quotes)
    result = CliRunner().invoke(portfolio.cli, ["show"])
    assert result.exit_code == 0
    assert "Total Portfolio Value: EUR 20.00" in result.output
    assert "EUR 0.00" in result.output
    assert "Unavailable" in result.output
    assert "$" not in result.output


def test_partial_quote_does_not_become_a_total_or_allocation(monkeypatch):
    from click.testing import CliRunner

    import portfolio

    monkeypatch.setattr(portfolio, "load_portfolio", lambda: {"holdings": {"BTC": 2, "ETH": 1}, "currency": "USD"})
    monkeypatch.setattr(portfolio, "fetch_prices", lambda *args: {"bitcoin": {"usd": 10}, "ethereum": {"usd": None}})
    monkeypatch.setattr(portfolio, "PLOTEXT_AVAILABLE", True)
    chart = MagicMock()
    monkeypatch.setattr(portfolio, "plt", chart, raising=False)
    result = CliRunner().invoke(portfolio.cli, ["show"])
    assert result.exit_code == 0
    assert "Total Portfolio Value: Unavailable" in result.output
    assert "$20.00" in result.output
    result = CliRunner().invoke(portfolio.cli, ["allocation"])
    assert result.exit_code == 0
    assert "Allocation unavailable" in result.output
    chart.bar.assert_not_called()


def test_price_command_hides_missing_prices_and_shows_real_zero(monkeypatch):
    from click.testing import CliRunner

    import portfolio

    monkeypatch.setattr(portfolio, "fetch_prices", lambda *args: {"bitcoin": {"usd": 0, "usd_24h_change": 0}})
    result = CliRunner().invoke(portfolio.cli, ["prices", "BTC", "ETH"])
    assert result.exit_code == 0
    assert "$0.00" in result.output and "+0.00%" in result.output
    assert "Unavailable" in result.output
