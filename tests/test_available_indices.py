"""Tests for available indices model and field mapping."""

import pytest
from openbb_tushare.models.available_indices import (
    TushareAvailableIndicesData,
    TushareAvailableIndicesQueryParams,
)


def test_available_indices_data_ts_code_to_symbol_mapping():
    """Test that ts_code field is correctly mapped to symbol field."""
    # Sample data from Tushare API with ts_code field
    sample_data = {
        "ts_code": "000001.SH",
        "name": "上证指数",
        "fullname": "上海证券综合指数",
        "market": "SSE",
        "publisher": "上交所",
        "index_type": "综合指数",
        "category": "股票指数",
        "base_date": "19901219",
        "base_point": 100.0,
        "list_date": "19910715",
        "weight_rule": "总市值加权",
        "desc": "上海证券综合指数",
        "exp_date": None,
        "currency": "CNY",
    }
    
    # Validate that the model can accept ts_code and map it to symbol
    result = TushareAvailableIndicesData.model_validate(sample_data)
    
    # Verify that symbol field is populated from ts_code
    assert result.symbol == "000001.SH"
    
    # Verify that the original ts_code is accessible via alias
    assert hasattr(result, "symbol")
    
    # Verify other fields are preserved
    assert result.name == "上证指数"
    assert result.market == "SSE"
    assert result.currency == "CNY"


def test_available_indices_data_with_symbol_field():
    """Test that model also accepts symbol field directly."""
    # Sample data with symbol field (already mapped)
    sample_data = {
        "symbol": "000001.SH",
        "name": "上证指数",
        "fullname": "上海证券综合指数",
        "market": "SSE",
        "publisher": "上交所",
        "index_type": "综合指数",
        "category": "股票指数",
        "base_date": "19901219",
        "base_point": 100.0,
        "list_date": "19910715",
        "weight_rule": "总市值加权",
        "desc": "上海证券综合指数",
        "exp_date": None,
        "currency": "CNY",
    }
    
    # Validate that the model accepts symbol field directly
    result = TushareAvailableIndicesData.model_validate(sample_data)
    
    # Verify symbol field
    assert result.symbol == "000001.SH"
    assert result.name == "上证指数"


def test_available_indices_query_params():
    """Test AvailableIndicesQueryParams creation."""
    params = TushareAvailableIndicesQueryParams(use_cache=True)
    assert params.use_cache is True
    
    params = TushareAvailableIndicesQueryParams(use_cache=False)
    assert params.use_cache is False
    
    # Test default value
    params = TushareAvailableIndicesQueryParams()
    assert params.use_cache is True  # Default from Field definition

