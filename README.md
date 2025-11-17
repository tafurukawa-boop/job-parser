# Job Parser

求人原稿をクレンジングし、AI 的なヘッダ検出ロジックで構造化 JSON を返すパーサーです。

## プロジェクト構成
- `job_parser/parser.py` : 全体のパースフローと JSON 生成
- `job_parser/utils/cleaning.py` : 改行整理、HTML エンティティ変換、全角・半角スペース正規化
- `job_parser/utils/header_detection.py` : ヘッダ候補抽出とセクション分割のヒューリスティック
- `job_parser/main.py` : サンプル実行用エントリポイント
- `job_parser/__init__.py` : `parse_job` の公開インポート

## 使い方
### サンプル実行
```bash
python -m job_parser.main
```

### モジュールとして利用
任意の求人文を `parse_job` に渡して利用できます。

```python
from job_parser import parse_job

raw_text = """
【キャッチコピー】
働きやすさ抜群の環境です

勤務地：東京都新宿区
仕事内容：データ基盤の整備と分析業務
給与：年収500万円〜
"""

structured = parse_job(raw_text)
print(structured)
```

`parse_job` の戻り値は以下の構造を持ちます。

```json
{
  "job_title": "",
  "company": "",
  "salary": "",
  "sections": {
    "キャッチコピー": "...",
    "勤務地": "...",
    "仕事内容": "...",
    "求めている人材": "...",
    "勤務時間": "...",
    "勤務時間詳細": "...",
    "勤務地所在地": "...",
    "交通アクセス": "...",
    "給与詳細": "...",
    "試用期間": "...",
    "待遇・福利厚生": "...",
    "社会保険": "...",
    "選考プロセス": "...",
    "(未知の見出し)": "..."
  }
}
```
