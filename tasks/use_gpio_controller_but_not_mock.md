## 概要
現状、test_infrastructureに実装しているGPIOのテストはmockになっているが、RasberryPIでテスト実行する時に限りmockを使用せず、実際のGPIOを使用する。

## 要求
- RasberryPIのテスト実行は実際のGPIOを使用する
- RasberryPI以外でテスト実行する時はmockにする
- MockとGPIOでテスト内容は同一
- テストにMockか実GPIOかinjectionする形で実装する
