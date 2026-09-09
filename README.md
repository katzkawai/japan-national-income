# 日本の国民所得（GNI）推移と構造分析：名目 vs 実質

[![Built with Gemini 3.8 Flash](https://img.shields.io/badge/Built%20with-Gemini%203.8%20Flash-8A2BE2.svg)](https://deepmind.google/technologies/gemini/)
[![PEP 723](https://img.shields.io/badge/PEP-723-blue.svg)](https://peps.python.org/pep-0723/)
[![uv](https://img.shields.io/badge/managed%20by-uv-DE5FE9.svg)](https://github.com/astral-sh/uv)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green.svg)](https://katzkawai.org/japan-national-income/)

世界銀行オープンデータ（World Bank Open Data）APIから日本の経済統計を取得し、**名目**（額面価格）および**実質**（物価調整後・基準年固定価格）の国民総所得（GNI）、国内総生産（GDP）、海外からの純所得（一次所得収支）、および1人当たり国民所得の長期推移（1980年〜）を可視化・分析するオープンソースプロジェクトです。

> **🤖 AI構築クレジット**  
> 本プロジェクト（Python可視化スクリプト、Webインタラクティブダッシュボード、GitHub Pages公開設定、ドキュメント全般）は **Gemini 3.8 Flash** を使用して対話的に設計・実装・構築されました。

---

## 🌐 サイト概要

本プロジェクトで公開している Web サイト（GitHub Pages）は、日本の国民所得の構造変化と、名目・実質の乖離を直感的に把握できるダッシュボードです。

- **公開URL**: **[https://katzkawai.org/japan-national-income/](https://katzkawai.org/japan-national-income/)**  
  *(または [https://katzkawai.github.io/japan-national-income/](https://katzkawai.github.io/japan-national-income/) )*

### 主な特徴・提供機能
1. **「名目」と「実質」の対比可視化**:
   - **GNI：名目 vs 実質**: 近年のインフレ局面における名目値の急膨張と、物価調整後の実質値のギャップ（+60兆円以上）を視覚化。
   - **実質GNI vs 実質GDP**: 実質ベースでも海外投資収益（約+24兆円）が国民所得を底上げしている実態を比較。
   - **1人当たり国民所得**: 額面（570万円超）と実質購買力（約490万円）の比較。
   - **成長率比較**: 実質成長率と名目成長率の推移。
2. **高解像度4面分析プロット画像**:
   - Python (Matplotlib / Seaborn) で自動生成されたチャートの原寸閲覧・ダウンロード。
3. **推移データテーブル**:
   - 直近10年間の主要指標（名目GNI/GDP、実質GNI/GDP、1人当り名目/実質）を一覧表示。
4. **PEP 723 / `uv` によるワンライナー再現性**:
   - 環境構築不要で即座にデータ取得とプロットを再実行可能。

---

## 📊 可視化グラフ（名目 vs 実質）

![日本の国民所得推移と分析：名目 vs 実質](japan_national_income.png)

### 💡 主な経済的着眼点

| 視点 | 名目（Nominal） | 実質（Real: 物価調整後） | 読み解き・分析ポイント |
| :--- | :--- | :--- | :--- |
| **国民総所得 (GNI)** | **705.7 兆円** (2025年) | **608.2 兆円** (2024年) | 2022年以降のインフレにより名目は急増しているが、実質は約608兆円。物価上昇による膨らみが約65兆円分存在。 |
| **国内総生産 (GDP)** | **663.8 兆円** (2025年) | **584.2 兆円** (2024年) | 実質GDPは580〜590兆円規模で推移。 |
| **海外からの純所得** | **+41.9 兆円** (2025年) | **+24.0 兆円** (2024年) | 名目・実質ともに受取超過。日本経済が海外投資収益で所得を稼ぐ「投資立国」へ転換したことが実質でも裏付けられる。 |
| **1人当たりGNI** | **572.0 万円** (2025年) | **490.6 万円** (2024年) | 額面上の所得は大きく伸びているが、実質的な生活実感・購買力は490万円前後で推移。 |

---

## 🚀 実行方法

本プロジェクトのPythonスクリプトは [PEP 723](https://peps.python.org/pep-0723/)（Inline script metadata）に準拠しています。[`uv`](https://github.com/astral-sh/uv) がインストールされていれば、仮想環境の作成や `pip install` なしで即座に実行できます。

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
├── visualize_national_income.py  # PEP 723対応 Pythonスクリプト（名目・実質指標取得）
├── index.html                    # GitHub Pages用 インタラクティブダッシュボード
├── data.json                     # スクリプトから出力された年次経済データ
├── japan_national_income.png     # Python (Matplotlib) で生成された4面グラフ画像
├── README.md                     # 本ドキュメント（概要、名目・実質の解説、更新履歴、クレジット）
└── .gitignore                    # Git除外設定
```

---

## 📝 更新履歴 (Changelog)

### [1.2.0] - 2026-09-10
- **実質（物価調整後）指標の追加・全面対応**:
  - 世界銀行APIから実質GNI（`NY.GNP.MKTP.KN`）、実質GDP（`NY.GDP.MKTP.KN`）、実質1人当たりGNI（`NY.GNP.PCAP.KN`）を取得。
  - Pythonスクリプトのプロットを「名目 vs 実質」の多角的分析チャート（GNI名目実質比較、実質GNI vs 実質GDP、1人当たり名目実質比較、成長率比較）へ刷新。
  - Webダッシュボードに「名目と実質の読み解き方」解説バナー、名目・実質KPIカード、タブ切り替えチャート、データテーブルを追加。
  - `README.md` に名目と実質の比較解説表を追加。

### [1.1.0] - 2026-09-10
- **ドキュメント拡充 & クレジット明記**:
  - `README.md` にサイトの概要、主な特徴、更新履歴を追加。
  - プロジェクトが **Gemini 3.8 Flash** によって構築された旨を `README.md` および `index.html` に明記。

### [1.0.0] - 2026-09-10
- **初期リリース**:
  - PEP 723 準拠の Python 可視化スクリプト `visualize_national_income.py` を実装。
  - 高解像度プロット画像 `japan_national_income.png` および `data.json` を生成。
  - Chart.js & Tailwind CSS によるインタラクティブダッシュボード `index.html` を作成。
  - `gh` CLI を用いて公開リモートリポジトリ `katzkawai/japan-national-income` を作成・GitHub Pages で公開。

---

## 📜 出典・クレジット

- **データ出典**: [World Bank Open Data](https://data.worldbank.org/)  
  (Indicators: `NY.GNP.MKTP.CN`, `NY.GDP.MKTP.CN`, `NY.GNP.PCAP.CN`, `NY.GNP.MKTP.CD`, `NY.GNP.PCAP.CD`, `NY.GNP.MKTP.KN`, `NY.GDP.MKTP.KN`, `NY.GNP.PCAP.KN`)
- **制作・開発**: **Gemini 3.8 Flash** & Katz Kawai
