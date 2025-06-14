# アプリケーション仕様
Rasberry PIで照明や電子機器を制御するIoTアプリケーション。

## 言語
Python

## HTTPサーバー
FastAPI

## プロジェクトの構成
- src/presentation/
    - HTTPサーバーのエンドポイントを持つ
    - HTTPサーバーはlocalhost:80で起動します。
- src/application/
    - アプリケーションロジックを持つ
        - デバイスの登録、デバイスの一覧取得、デバイスの状態取得、デバイスのOn/Off操作を行う
- src/hardware/
    - GPIOの操作などRasberry PIのハードウェアを操作するモジュール
- src/infrastructure
    - DBの操作を行う
        - PostgreSQLを使用する
        - ORMはSQLAlchemyを使用する
        - PostgreSQLの接続情報（例: ホスト名、ユーザー名、パスワード、DB名）は.envファイルに記載する
    - AWSの操作を行う
        - boto3を使用する
- src/main.py
    - アプリケーションのエントリーポイント


## 構成の依存関係
- presentation層はapplication層のAPIを呼び出す
- application層はhardware層のAPIを呼び出す
- application層はinfrastructure層のAPIを呼び出す
- infrastructure層はDBや外部サービスのAPIを呼び出す
- hardware層とinfrastructure層はお互いに依存しない
- presentation層は基本的にhardware層に直接依存しないが、RasberryPIのGPIOを直接操作するエンドポイントのみ、hardware層のAPIを直接呼び出す


## HTTPエンドポイントの仕様
- POST /device/register
    - デバイスの登録を行う
    - デバイスの登録にはデバイスの名前とGPIOの番号をクエリパラメータで指定する
- GET /device/list
    - 登録されたデバイスの一覧を取得する
- POST /device/{device_id}/on
    - 指定されたデバイスをOnにする
    - デバイスのIDはdevice/registerで登録したデバイスのIDを使用する
- POST /device/{device_id}/off
    - 指定されたデバイスをOffにする
    - デバイスのIDはdevice/registerで登録したデバイスのIDを使用する
- GET /device/{device_id}/status
    - 指定されたデバイスの状態を取得する
    - デバイスのIDはdevice/registerで登録したデバイスのIDを使用する
- POST /GPIO/{gpio_number}/on
    - RasberryPIのGPIOを直接Onにする
- POST /GPIO/{gpio_number}/off
    - RasberryPIのGPIOを直接Offにする
- GET /GPIO/{gpio_number}/status
    - RasberryPIのGPIOの状態を取得する

## アプリケーション層のモデル定義
- device
    - device_id: str //内部的に管理するIDで、UUIDを使用する
    - device_name: str
    - gpio_number: int
    - is_on: bool
    - created_at: datetime
    - updated_at: datetime
- device_register_request
    - device_name: str
    - gpio_number: int
- device_register_response
    - device_id: str
    - device_name: str
    - gpio_number: int
    - created_at: datetime
    - updated_at: datetime
- device_list_response
    - devices: list[device]

## デバイス状態の保持方法
- is_on: bool をどのように扱うか
    - 常にハードウェアの実際の状態と一致させる
    - DBに永続化しない


## 非同期処理の使用有無
FastAPI は非同期サーバだが、一方でGPIO制御やDBアクセスは同期処理が主である。
処理の簡略化のため、すべて同期処理とする。

## AWSの利用用途
現状は具体的な利用ユースケースはなく、将来のAWS利用を想定したものとする。

## エラーハンドリング
- デバイスが存在しない、またはGPIOがすでに使用中などのケースでの戻り値の方針（ステータスコード、エラーメッセージ）
  - デバイスが存在しない場合は404 Not Foundとする
  - デバイスが存在する場合、GPIOがすでに使用中などのケースでは400 Bad Requestとする

## セキュリティ
FastAPI を localhost:80 で起動だが、これは開発用途前提である。
本番環境は後の課題とする。

## デプロイ方法
Raspberry Pi 上では systemdで Python アプリを常駐させる。
依存管理はpip, venv, requirements.txtで行う。

