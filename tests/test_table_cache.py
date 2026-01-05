import pytest
import pandas as pd
from mysharelib.table_cache import TableCache

@pytest.fixture
def test_db_path(tmp_path):
    return str(tmp_path / "tushare_equity_info.db")

@pytest.fixture
def table_cache(test_db_path):
    table_schema = {
        'symbol': 'TEXT',
        'name': 'TEXT',
        'price': 'REAL'
    }
    #db_path = ':memory:'
    db_path = test_db_path
    table_name = 'equity_info'
    cache = TableCache(table_schema, db_path, table_name)
    test_data = pd.DataFrame({
        'symbol': ['AAPL', 'MSFT', 'GOOGL'],
        'name': ['Apple', 'Microsoft', 'Google'],
        'price': [150.0, 300.0, 2800.0]
    })
    cache.write_dataframe(test_data)
    data=cache.read_dataframe()  # Ensure the table is created and populated
    print(data)
    return cache

def test_read_rows_no_filters(table_cache):
    result = table_cache.read_rows({})
    assert len(result) == 3
    assert all(col in result.columns for col in ['symbol', 'name', 'price'])

def test_read_rows_single_filter(table_cache):
    filters = {'symbol': 'AAPL'}
    result = table_cache.read_rows(filters)
    assert len(result) == 1
    assert result.iloc[0]['name'] == 'Apple'

def test_read_rows_multiple_filters(table_cache):
    filters = {'symbol': 'MSFT', 'price': 300.0}
    result = table_cache.read_rows(filters)
    assert len(result) == 1
    assert result.iloc[0]['name'] == 'Microsoft'

def test_read_rows_no_matches(table_cache):
    filters = {'symbol': 'INVALID'}
    result = table_cache.read_rows(filters)
    assert len(result) == 0