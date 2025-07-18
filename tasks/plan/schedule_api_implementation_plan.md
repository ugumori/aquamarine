# スケジュールAPI実装計画

## 概要
Raspberry PIで照明や電子機器を制御するIoTアプリケーションにスケジュール機能を追加する。
TDD（Test-Driven Development）アプローチで実装する。

## 実装対象機能

### APIエンドポイント
- `POST /schedule/{device_id}` - スケジュール作成
- `GET /schedule/{device_id}` - デバイス別スケジュール取得
- `DELETE /schedule/{schedule_id}` - スケジュール削除

### データ構造
- Schedule（スケジュール）
  - schedule_id: str (PK)
  - device_id: str (FK)
  - schedule: str ("HH:MM"形式)
  - is_on: bool
  - created_at: datetime
  - updated_at: datetime

## 実装ファイル一覧

### 1. データベース層（Infrastructure Layer）
- `src/infrastructure/models.py` - Scheduleモデル追加
- `src/infrastructure/repositories.py` - ScheduleRepositoryの実装

### 2. アプリケーション層（Application Layer）  
- `src/application/models.py` - Pydanticモデル定義
- `src/application/repositories.py` - ScheduleRepositoryインターフェース
- `src/application/services.py` - ScheduleService実装

### 3. プレゼンテーション層（Presentation Layer）
- `src/presentation/api.py` - FastAPIエンドポイント追加

### 4. テスト
- `tests/test_infrastructure/test_schedule_repository.py`
- `tests/test_application/test_schedule_service.py`
- `tests/test_presentation/test_schedule_api.py`

## 詳細実装内容

### 1. データモデル設計

#### Pydanticモデル（application/models.py）
```python
class ScheduleCreateRequest(BaseModel):
    schedule: str  # "HH:MM"形式
    is_on: bool

class ScheduleModel(BaseModel):
    schedule_id: str
    schedule: str
    is_on: bool

class ScheduleListResponse(BaseModel):
    schedules: List[ScheduleModel]
```

#### SQLAlchemyモデル（infrastructure/models.py）
```python
class Schedule(Base):
    __tablename__ = "schedules"
    
    schedule_id = Column(String, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    schedule = Column(String, nullable=False)
    is_on = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### 2. APIエンドポイント仕様

#### POST /schedule/{device_id}
- **Request**: `ScheduleCreateRequest`
- **Response**: `ScheduleModel`
- **エラー**: 
  - 400 Bad Request (存在しないdevice_id、不正な時間形式)

#### GET /schedule/{device_id}
- **Response**: `ScheduleListResponse`
- **エラー**: 
  - 404 Not Found (存在しないdevice_id)
- **並び順**: スケジュール時間昇順

#### DELETE /schedule/{schedule_id}
- **Response**: 204 No Content
- **エラー**: 
  - 404 Not Found (存在しないschedule_id)

### 3. バリデーション仕様

#### 時間形式バリデーション
- **正規表現**: `^([01]?[0-9]|2[0-3]):[0-5][0-9]$`
- **範囲**: 00:00〜23:59
- **エラー**: 400 Bad Request

#### デバイス存在確認
- **対象**: POST /schedule/{device_id}、GET /schedule/{device_id}
- **エラー**: 400 Bad Request (POST)、404 Not Found (GET)

## TDD実装順序

### Phase 1: Infrastructure Layer
1. **Scheduleモデルのテスト作成**
   - テーブル作成確認
   - 外部キー制約確認
   
2. **ScheduleRepositoryのテスト作成**
   - save()メソッド
   - find_by_device_id()メソッド
   - find_by_id()メソッド
   - delete()メソッド
   
3. **SQLAlchemyモデル実装**
   - Scheduleクラス作成
   - テーブル定義
   
4. **ScheduleRepository実装**
   - CRUD操作実装
   - 並び順実装（時間昇順）

### Phase 2: Application Layer
1. **ScheduleServiceのテスト作成**
   - create_schedule()メソッド
   - get_schedules_by_device_id()メソッド
   - delete_schedule()メソッド
   - バリデーション処理
   
2. **Pydanticモデル実装**
   - リクエスト/レスポンスモデル
   - バリデーション設定
   
3. **ScheduleService実装**
   - ビジネスロジック実装
   - エラーハンドリング

### Phase 3: Presentation Layer
1. **APIエンドポイントのテスト作成**
   - 正常系テスト
   - 異常系テスト
   - 境界値テスト
   
2. **FastAPIエンドポイント実装**
   - ルーティング設定
   - レスポンス設定

### Phase 4: Integration Testing
1. **全体統合テスト**
   - API全体の動作確認
   
2. **エラーハンドリングテスト**
   - 各種エラーケース確認

## テストケース設計

### 正常系テスト
- スケジュール作成（有効な時間形式）
- デバイス別スケジュール取得
- スケジュール削除
- 時間順ソート確認
- 重複スケジュール作成

### 異常系テスト
- 存在しないdevice_idでのスケジュール作成
- 不正な時間形式（25:00、-1:00、abc:de等）
- 存在しないdevice_idでのスケジュール取得
- 存在しないschedule_idでの削除

### 境界値テスト
- 00:00、23:59の時間設定
- 同一時間・同一デバイスの重複スケジュール

## 実装時の注意点

### 1. エラーハンドリング
- HTTPExceptionを使用
- 適切なステータスコード（400、404、204）
- 既存のエラーハンドリングパターンに従う

### 2. UUIDの使用
- schedule_id生成にUUID使用
- 既存のDeviceServiceと同様のパターン

### 3. 外部キー制約
- device_idの存在確認はアプリケーション層で実装
- DeviceServiceを利用した存在確認

### 4. 並び順
- 時間文字列での辞書順ソート
- SQLAlchemyのorder_by使用

### 5. テーブル作成
- アプリケーション起動時の自動作成
- 既存のテーブル作成パターンに従う

### 6. コーディング規約
- 既存のコードスタイルに従う
- 同期処理で実装
- クリーンアーキテクチャの依存関係を遵守

## 実装完了条件

1. **機能実装完了**
   - 全APIエンドポイントが正常動作
   - 全バリデーションが適切に機能
   
2. **テスト完了**
   - 単体テスト：100%パス
   - 統合テスト：100%パス
   - カバレッジ：既存水準維持
   
3. **品質チェック完了**
   - `flake8`エラーなし
   - `mypy`エラーなし
   
4. **動作確認完了**
   - Raspberry PI上でのテスト実行
   - 実際のAPIエンドポイントでの動作確認

## 推奨作業時間配分

- Phase 1 (Infrastructure): 30%
- Phase 2 (Application): 40%
- Phase 3 (Presentation): 20%
- Phase 4 (Integration): 10%

## 依存関係

- 既存のDeviceService（device_id存在確認）
- 既存のデータベース設定
- 既存のテストフレームワーク
- 既存のFastAPIアプリケーション構成