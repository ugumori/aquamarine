# スケジュール機能実装計画

## 概要
スケジュールに従ってGPIOをon/offする機能を実装する。APSchedulerを使用し、JST基準で毎日実行される。

## 実装する機能
- スケジュールに従ったGPIO自動制御
- アプリケーション起動時のスケジュール読み込み
- スケジュールCRUD操作時の即時反映
- JST基準での時刻管理
- GPIO制御失敗時のログ出力

## アーキテクチャ設計

### 新規クラス: ScheduleExecutorService
**場所**: `src/application/services.py`

**責務**:
- APSchedulerを使用したスケジュール管理
- 毎日実行スケジュールの動的追加・削除
- スケジュール実行時のGPIO制御
- エラーハンドリングとログ出力

**主要メソッド**:
```python
class ScheduleExecutorService:
    def start() -> None
    def add_schedule(schedule_id: str, device_id: str, schedule_time: str, is_on: bool) -> None
    def remove_schedule(schedule_id: str) -> None
    def _execute_schedule(device_id: str, gpio_number: int, is_on: bool) -> None
```

### 既存クラス拡張: ScheduleService
**変更点**:
- ScheduleExecutorServiceへの依存追加
- `create_schedule()`: DB保存後にスケジューラーに追加
- `delete_schedule()`: DB削除後にスケジューラーから削除

## 技術仕様

### 依存関係
- `APScheduler`: スケジュール管理
- `pytz`: JST対応

### スケジュール形式
- 入力: `HH:MM`形式（例: "14:30"）
- 実行: 毎日指定時刻にJST基準で実行

### エラーハンドリング
- GPIO制御失敗時: WARNINGレベルでログ出力
- ログ内容: デバイス名、GPIO番号、時刻、エラー内容

### DI設計
- ScheduleExecutorServiceはシングルトンとして管理
- `app.state`で保持し、ファクトリ関数で提供

## 実装ファイル一覧

### 1. 依存関係追加
**ファイル**: `requirements.txt`
```
apscheduler
pytz
```

### 2. ScheduleExecutorService実装
**ファイル**: `src/application/services.py`
- 新規クラス追加
- APScheduler設定（JST、毎日実行）
- GPIO制御とエラーハンドリング

### 3. ScheduleService拡張
**ファイル**: `src/application/services.py`
- ScheduleExecutorServiceとの連携
- create/delete時の即時反映

### 4. アプリケーション起動処理
**ファイル**: `src/aquamarine.py`
- ScheduleExecutorServiceインスタンス作成
- 既存スケジュール読み込み
- app.stateに設定
- スケジューラー開始

### 5. API層統合
**ファイル**: `src/presentation/api.py`
- `get_schedule_executor_service()`追加
- `get_schedule_service()`拡張

### 6. テスト実装
**ファイル**: `tests/test_schedule_executor.py`（新規）
- ScheduleExecutorServiceの単体テスト
- スケジュール追加・削除テスト
- GPIO制御失敗テスト

**ファイル**: `tests/test_application.py`（拡張）
- ScheduleService拡張のテスト

## TDD実装手順

### Phase 1: ScheduleExecutorService
1. **Red**: ScheduleExecutorServiceのテスト作成
   - スケジュール追加・削除機能
   - 時刻形式パース
   - GPIO制御とエラーハンドリング

2. **Green**: ScheduleExecutorService実装
   - APScheduler設定
   - JST対応
   - GPIO制御ロジック

3. **Refactor**: コード整理

### Phase 2: ScheduleService拡張
1. **Red**: ScheduleService拡張のテスト作成
   - create_schedule時のスケジューラー連携
   - delete_schedule時のスケジューラー連携

2. **Green**: ScheduleService拡張実装
   - ScheduleExecutorServiceとの連携

3. **Refactor**: コード整理

### Phase 3: アプリケーション統合
1. **Validation**: 統合テスト実行
2. **Validation**: RaspberryPI上でのテスト
3. **Validation**: 動作確認

## 検証項目

### 単体テスト
- [ ] ScheduleExecutorService: スケジュール追加
- [ ] ScheduleExecutorService: スケジュール削除
- [ ] ScheduleExecutorService: GPIO制御成功
- [ ] ScheduleExecutorService: GPIO制御失敗時ログ
- [ ] ScheduleService: create時のスケジューラー連携
- [ ] ScheduleService: delete時のスケジューラー連携

### 統合テスト
- [ ] アプリケーション起動時のスケジュール読み込み
- [ ] API経由でのスケジュール作成・削除
- [ ] 時刻到達時のGPIO制御実行

### RaspberryPI検証
- [ ] 実際のGPIO制御動作
- [ ] スケジュール通りの実行
- [ ] エラー時のログ出力

## 設計上の考慮点

### パフォーマンス
- スケジューラーはバックグラウンドで軽量動作
- GPIO制御は同期処理（既存設計に合わせる）

### 拡張性
- 将来的なスケジュール形式拡張を考慮した設計
- 複数デバイス対応

### 保守性
- 責務の分離（実行 vs 管理）
- ログによる動作追跡
- テスタビリティ