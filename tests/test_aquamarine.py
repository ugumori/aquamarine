#!/usr/bin/env python

"""Tests for `aquamarine` package."""

import pytest
import sys
import os

# src ディレクトリを Python パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_import_aquamarine():
    """aquamarine パッケージのインポートテスト"""
    import aquamarine
    assert aquamarine is not None

def test_import_main():
    """メインモジュールのインポートテスト"""
    import aquamarine
    assert hasattr(aquamarine, 'main')
    assert callable(aquamarine.main)
