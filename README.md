# 日本の国民所得（GNI）推移と構造分析

[![Built with Gemini 3.8 Flash](https://img.shields.io/badge/Built%20with-Gemini%203.8%20Flash-8A2BE2.svg)](https://deepmind.google/technologies/gemini/)
[![PEP 723](https://img.shields.io/badge/PEP-723-blue.svg)](https://peps.python.org/pep-0723/)
[![uv](https://img.shields.io/badge/managed%20by-uv-DE5FE9.svg)](https://github.com/astral-sh/uv)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green.svg)](https://katzkawai.org/japan-national-income/)

世界銀行オープンデータ（World Bank Open Data）APIから日本の経済統計を取得し、国民総所得（GNI）、国内総生産（GDP）、海外からの純所得（一次所得収支）、および1人当たり国民所得の長期推移（1980年〜2025年）を可視化・分析するオープンソースプロジェクトです。

> **🤖 AI構築クレジット**  
> 本プロジェクト（Python可視化スクリプト、Webインタラクティブダッシュボード、GitHub Pages公開設定、ドキュメント全般）は **Gemini 3.8 Flash** を使用して対話的に設計・実装・構築されました。

---

## 🌐 サイト概要

本プロジェクトで公開している Web サイト（GitHub Pages）は、日本の国民所得の構造変化を直感的に把握できるダッシュボードです。

- **公開URL**: **[https://katzkawai.org/japan-national-income/](https://katzkawai.org/japan-national-income/)**  
  *(または [https://katzkawai.github.io/japan-national-income/](https://katzkawai.github.io/japan-national-income/) )*

### 主な特徴・提供機能
1. **インタラクティブ推移チャート (Chart.js)**:
   - **GNI vs GDP**: 国内生産（GDP）と国民所得（GNI）の長期乖離を比較。
   - **海外からの純所得**: 近年+40兆円超へと急増した投資立国としての所得受取超過を棒グラフで表示。
   - **1人当たり所得推移**: 円建て（万円）とドル建て（USドル）の二軸比較により、為替影響（円安等）を可視化。
   - **年次成長率**: 前年比伸び率の推移。
2. **高解像度プロット画像**:
   - Python (Matplotlib / Seaborn) で生成された4面分析チャートの原寸閲覧・ダウンロード。
3. **推移データテーブル**:
   - 直近10年間の主要指標を一覧表示。
4. **PEP 723 / `uv` による再現性**:
   - 手元ですぐに同じデータ取得と可視化を再現可能。

---

## 📊 可視化グラフ

![日本の国民所得推移と分析](japan_national_income.png)

### 主な経済的着眼点
1. **国民総所得（GNI）と国内総生産（GDP）の乖離**:
   - 近年、日本の名目GNIは名目GDPを大きく上回っています（2025年実績でGNI約705.7兆円に対し、GDPは約663.8兆円）。
2. **海外からの純所得（第一次所得収支）の拡大**:
   - その差分である海外からの純所得（対外直接投資や証券投資からの利子・配当収益）は年間 **+41.9兆円** 規模に達し、日本経済が「貿易立国」から「投資立国」へ変化した実態を表しています。
3. **1人当たり国民総所得**:
   - 日本円ベースでは直近で約572万円に達する一方、ドル換算では為替変動（円安）の影響を受けています。

---

## 🚀 実行方法

本プロジェクトのPythonスクリプトは [PEP 723](https://peps.python.org/pep-0723/)（Inline script metadata）に準拠しています。[`uv`](https://github.com/astral-sh/uv) がインストールされていれば、仮想環境の作成や `pip install` の手動実行なしで、以下のワンライナーで即座に実行できます。

```bash
# スクリプトの実行（最新データ取得、グラフ画像 japan_national_income.png および data.json を生成）
uv run visualize_national_income.py
```

### 依存関係定義（PEP 723）
```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "matplotlib",
#     "pandas",
#     "requests",
#     "seaborn",
# ]
# ///
```

---

## 📁 ファイル構成

```text
├── visualize_national_income.py  # PEP 723対応 Python可視化スクリプト（世界銀行API連携）
├── index.html                    # GitHub Pages用 インタラクティブダッシュボード
├── data.json                     # スクリプトから出力された年次経済データ
├── japan_national_income.png     # Python (Matplotlib) で生成された4面グラフ画像
├── README.md                     # 本ドキュメント（概要、更新履歴、クレジット）
└── .gitignore                    # Git除外設定
```

---

## 📝 更新履歴 (Changelog)

### [1.1.0] - 2026-09-10
- **ドキュメント拡充**:
  - `README.md` にサイトの概要、主な特徴、更新履歴を追加。
  - プロジェクトが **Gemini 3.8 Flash** によって構築された旨を明記。
- **UI更新**:
  - `index.html` のヘッダーバッジおよびフッターに Gemini 3.8 Flash による構築クレジットを追加。

### [1.0.0] - 2026-09-10
- **初期リリース**:
  - PEP 723 準拠の Python 可視化スクリプト `visualize_national_income.py` を実装（世界銀行 API から GNI, GDP, 1人当りGNI, 成長率を取得・分析）。
  - 高解像度4面分析プロット画像 `japan_national_income.png` を生成。
  - Web用データ出力 `data.json` の自動生成機能を追加。
  - Chart.js & Tailwind CSS によるインタラクティブダッシュボード `index.html` を作成。
  - `gh` CLI を用いて公開リモートリポジトリ `katzkawai/japan-national-income` を作成・プッシュ。
  - GitHub Pages を設定・公開（カスタムドメインおよび `github.io` に対応）。

---

## 📜 出典・クレジット

- **データ出典**: [World Bank Open Data](https://data.worldbank.org/)  
  (Indicators: `NY.GNP.MKTP.CN`, `NY.GDP.MKTP.CN`, `NY.GNP.PCAP.CN`, `NY.GNP.MKTP.CD`, `NY.GNP.PCAP.CD`)
- **制作・開発**: **Gemini 3.8 Flash** & Katz Kawai
