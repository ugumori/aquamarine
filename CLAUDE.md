# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Raspberry PIで照明や電子機器を制御するIoTアプリケーション。FastAPIとPostgreSQLを使用したクリーンアーキテクチャ構成。

## 開発コマンド

### テスト実行
```bash
# 単体テスト実行
PYTHONPATH=src python -m pytest

# 全Python環境でテスト実行
tox

# カバレッジ付きテスト実行
coverage run --source aquamarine -m pytest
coverage report -m
coverage html
```

### コード品質チェック
```bash
# リント実行
flake8 aquamarine tests

# 型チェック
mypy .
```

### ビルドとインストール
```bash
# パッケージビルド
python -m build

# 開発用インストール
pip install -e .

# 依存関係インストール
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

<!-- ### データベース
```bash
# マイグレーション実行
alembic upgrade head

# 新しいマイグレーション作成
alembic revision --autogenerate -m "description"
``` -->

### アプリケーション起動
```bash
# メインアプリケーション起動
python -m src.main

# または
aquamarine
```

## アーキテクチャ

### レイヤー構成
- **presentation/** - FastAPI エンドポイント (HTTP API)
- **application/** - ビジネスロジック、デバイス管理サービス
- **infrastructure/** - データベース操作 (SQLAlchemy)、AWS連携
- **hardware/** - Raspberry Pi GPIO制御

### 依存関係
- presentation → application
- application ← infrastructure, hardware
    - applicationはinfrastructure, hardwareを呼び出すが、依存は逆転させる
- infrastructure ↔ hardware (相互依存なし)
- presentation → hardware (GPIO直接操作エンドポイントのみ、開発用)

## 技術スタック

- **言語**: Python 3.8+
- **Webフレームワーク**: FastAPI
- **データベース**: sqlite3 + SQLAlchemy
- **マイグレーション**: Alembic 1.13.0
- **非同期処理**: 使用しない（同期処理に統一）
- **デプロイ**: systemd + pip/venv

## 設定

<!-- ### 環境変数 (.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=iot_app
``` -->


## 重要な設計決定

- **デバイス状態管理**: `is_on`はハードウェアの実際の状態と一致させる、DBに永続化しない
- **エラーハンドリング**: 404 (Not Found), 400 (Bad Request) を適切に使用
- **セキュリティ**: 開発用途のため localhost:8080 で起動
- **AWS連携**: 将来の拡張用途、現在は具体的な利用なし

## 開発時の注意事項

- すべて同期処理で実装
- UUIDを使用したデバイスID管理
- クリーンアーキテクチャの依存関係を遵守
- パッケージの定義としてディレクトリに__init__.pyを作成する
- TDDで開発する
    - テスト実装、テストの失敗を確認、実装、テストの成功を確認、リファクタリングで進める
    - モック実装は基本的にしない
        - ただしRasberry PIのハードウェアに依存する処理のみモックを実装する。その場合でも、Rasberry PI上でテストを実行する場合は、モックを使わないこと。
    - 既存のテストはできるだけ書き換えないこと


## Rasberry PI上で動くアプリケーションのため、開発時にRasberry PIにアクセスする必要がある場合はsshでアクセスする
- Rasberry PIのホスト名
    - sapphire
- 接続コマンド
    - `ssh rava@sapphire.local`
- Rasberry PI上のプロジェクトディレクトリ
    - `/home/rava/projects/aquamarine`

## Rasberry PI上でのテスト実行
```
cd /home/rava/projects/aquamarine
source venv/bin/activate
PYTHONPATH=src python -m pytest
```
