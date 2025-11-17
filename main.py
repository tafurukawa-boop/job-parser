"""CLI entry point for quick validation of the JobParser workflow."""

from parser import parse_job


SAMPLE_JOB = """
【キャッチコピー】
AIで未来をつくる仲間を募集！

【仕事内容】
最先端のモデルを用いたAPI開発・MLOps推進を担当。

【勤務地】
東京都千代田区（フルリモート相談可）

【給与】
月給40万円〜＋業績賞与

【勤務時間】
10:00〜19:00（フレックス制）

【選考プロセス】
書類選考→1次面接→最終面接→内定
"""


def main():
    parsed = parse_job(SAMPLE_JOB)
    print(parsed)


if __name__ == "__main__":
    main()
