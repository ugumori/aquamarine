#!/usr/bin/env python3
"""Console script for aquamarine."""

import uvicorn
from infrastructure.database import create_tables

def main():
    """アプリケーションのエントリーポイント"""
    # データベーステーブルを作成
    create_tables()
    
    # FastAPIアプリケーションを起動
    uvicorn.run(
        "presentation.api:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )

if __name__ == "__main__":
    main()