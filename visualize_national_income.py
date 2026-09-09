# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "matplotlib",
#     "pandas",
#     "requests",
#     "seaborn",
# ]
# ///
"""日本の国民所得（GNI: Gross National Income）を可視化するスクリプト

世界銀行オープンデータAPIから日本の各種経済指標を取得し、
国民総所得(GNI)、国内総生産(GDP)、海外からの純所得、1人当たりGNIの推移をプロットします。

実行方法:
    uv run visualize_national_income.py
"""

import sys
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

# スタイル設定
sns.set_theme(style="whitegrid")

# 日本語フォントの設定
JP_FONTS = [
    "Noto Sans CJK JP",
    "Noto Sans JP",
    "IPAexGothic",
    "IPAGothic",
    "TakaoGothic",
    "BIZ UDPGothic",
    "VL Gothic",
    "sans-serif",
]
available_fonts = {f.name for f in fm.fontManager.ttflist}
for font_name in JP_FONTS:
    if font_name in available_fonts:
        plt.rcParams["font.family"] = font_name
        break
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け防止

# 取得する指標の定義（世界銀行インジケーター）
INDICATORS = {
    "NY.GNP.MKTP.CN": "GNI_yen",       # 国民総所得 (名目, 円)
    "NY.GDP.MKTP.CN": "GDP_yen",       # 国内総生産 (名目, 円)
    "NY.GNP.PCAP.CN": "GNI_per_capita", # 1人当たりGNI (名目, 円)
    "NY.GNP.MKTP.CD": "GNI_usd",       # 国民総所得 (名目, 米ドル)
    "NY.GNP.PCAP.CD": "GNI_per_capita_usd", # 1人当たりGNI (米ドル, Atlas法)
}


def fetch_indicator(indicator_code: str, country_code: str = "JPN") -> pd.DataFrame:
    """世界銀行APIから指標データを取得する"""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=100"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if len(data) < 2 or not data[1]:
            print(f"警告: {indicator_code} のデータが見つかりませんでした。", file=sys.stderr)
            return pd.DataFrame()

        records = []
        for item in data[1]:
            if item.get("value") is not None:
                records.append({
                    "year": int(item["date"]),
                    "value": float(item["value"]),
                })
        return pd.DataFrame(records)
    except Exception as e:
        print(f"データ取得エラー ({indicator_code}): {e}", file=sys.stderr)
        return pd.DataFrame()


def load_all_data() -> pd.DataFrame:
    """全指標を取得・統合する"""
    merged_df = None
    print("世界銀行APIから日本の経済データを取得中...")
    for code, col_name in INDICATORS.items():
        print(f" - {col_name} ({code}) 取得中...")
        df = fetch_indicator(code)
        if df.empty:
            continue
        df = df.rename(columns={"value": col_name})
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="year", how="outer")

    if merged_df is None or merged_df.empty:
        raise RuntimeError("データの取得に失敗しました。")

    merged_df = merged_df.sort_values("year").reset_index(drop=True)

    # 単位変換: 円 -> 兆円 / 万円
    if "GNI_yen" in merged_df.columns:
        merged_df["GNI_trillion_yen"] = merged_df["GNI_yen"] / 1e12
    if "GDP_yen" in merged_df.columns:
        merged_df["GDP_trillion_yen"] = merged_df["GDP_yen"] / 1e12
    if "GNI_per_capita" in merged_df.columns:
        merged_df["GNI_per_capita_man_yen"] = merged_df["GNI_per_capita"] / 1e4

    # 海外からの純所得 (GNI - GDP)
    if "GNI_trillion_yen" in merged_df.columns and "GDP_trillion_yen" in merged_df.columns:
        merged_df["Net_income_from_abroad_trillion_yen"] = (
            merged_df["GNI_trillion_yen"] - merged_df["GDP_trillion_yen"]
        )

    # 前年比成長率 (%)
    if "GNI_yen" in merged_df.columns:
        merged_df["GNI_growth_rate"] = merged_df["GNI_yen"].pct_change() * 100
    if "GDP_yen" in merged_df.columns:
        merged_df["GDP_growth_rate"] = merged_df["GDP_yen"].pct_change() * 100

    return merged_df


def plot_national_income(df: pd.DataFrame, output_path: str = "japan_national_income.png") -> None:
    """国民所得の可視化グラフを生成・保存する"""
    # 1980年以降のデータをメインに分析（長期推移と直近トレンドを両立）
    sub_df = df[df["year"] >= 1980].copy()

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("日本の国民所得（GNI）推移と分析 (1980年〜)", fontsize=18, fontweight="bold", y=0.98)

    # 1. GNIとGDPの推移（兆円）
    ax1 = axes[0, 0]
    ax1.plot(sub_df["year"], sub_df["GNI_trillion_yen"], label="国民総所得 (GNI)", color="#1f77b4", linewidth=2.5)
    ax1.plot(sub_df["year"], sub_df["GDP_trillion_yen"], label="国内総生産 (GDP)", color="#ff7f0e", linewidth=2, linestyle="--")
    ax1.fill_between(
        sub_df["year"],
        sub_df["GDP_trillion_yen"],
        sub_df["GNI_trillion_yen"],
        where=(sub_df["GNI_trillion_yen"] >= sub_df["GDP_trillion_yen"]),
        color="#2ca02c",
        alpha=0.25,
        label="海外からの純所得 (受取超過)"
    )
    ax1.set_title("① 国民総所得(GNI) と 国内総生産(GDP) の推移", fontsize=13, fontweight="bold")
    ax1.set_ylabel("兆円", fontsize=11)
    ax1.set_xlabel("年", fontsize=11)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. 海外からの純所得（一次所得収支）の拡大
    ax2 = axes[0, 1]
    if "Net_income_from_abroad_trillion_yen" in sub_df.columns:
        colors = ["#2ca02c" if val >= 0 else "#d62728" for val in sub_df["Net_income_from_abroad_trillion_yen"]]
        ax2.bar(sub_df["year"], sub_df["Net_income_from_abroad_trillion_yen"], color=colors, alpha=0.75, width=0.8)
        ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax2.set_title("② 海外からの純所得 (GNI − GDP の差額)", fontsize=13, fontweight="bold")
        ax2.set_ylabel("兆円", fontsize=11)
        ax2.set_xlabel("年", fontsize=11)
        ax2.grid(True, linestyle=":", alpha=0.6)
        
        latest_valid = sub_df.dropna(subset=["Net_income_from_abroad_trillion_yen"]).iloc[-1]
        ax2.annotate(
            f"直近({int(latest_valid['year'])}年):\n+{latest_valid['Net_income_from_abroad_trillion_yen']:.1f}兆円",
            xy=(latest_valid["year"], latest_valid["Net_income_from_abroad_trillion_yen"]),
            xytext=(latest_valid["year"] - 7, latest_valid["Net_income_from_abroad_trillion_yen"] + 4),
            arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6),
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="#ffffcc", ec="gray", alpha=0.9),
        )

    # 3. 1人当たりGNIの推移（万円 & 米ドル）
    ax3 = axes[1, 0]
    color_yen = "#1f77b4"
    ax3.set_xlabel("年", fontsize=11)
    ax3.set_ylabel("1人当たりGNI (万円)", color=color_yen, fontsize=11)
    line1 = ax3.plot(sub_df["year"], sub_df["GNI_per_capita_man_yen"], color=color_yen, linewidth=2.5, label="1人当たりGNI (万円)")
    ax3.tick_params(axis="y", labelcolor=color_yen)
    ax3.grid(True, linestyle=":", alpha=0.6)

    # 米ドル軸（第2軸）
    ax3_twin = ax3.twinx()
    color_usd = "#9467bd"
    ax3_twin.set_ylabel("1人当たりGNI (USドル)", color=color_usd, fontsize=11)
    line2 = ax3_twin.plot(sub_df["year"], sub_df["GNI_per_capita_usd"], color=color_usd, linewidth=2, linestyle="-.", label="1人当たりGNI (USドル)")
    ax3_twin.tick_params(axis="y", labelcolor=color_usd)
    ax3_twin.grid(False)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper left")
    ax3.set_title("③ 1人当たり国民総所得(GNI)の推移（円・米ドル換算）", fontsize=13, fontweight="bold")

    # 4. GNI成長率とGDP成長率の推移 (%)
    ax4 = axes[1, 1]
    ax4.plot(sub_df["year"], sub_df["GNI_growth_rate"], label="GNI成長率 (%)", color="#1f77b4", linewidth=2)
    ax4.plot(sub_df["year"], sub_df["GDP_growth_rate"], label="GDP成長率 (%)", color="#ff7f0e", linewidth=1.5, linestyle="--", alpha=0.8)
    ax4.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax4.set_title("④ 名目GNIおよび名目GDPの前年比成長率", fontsize=13, fontweight="bold")
    ax4.set_ylabel("前年比 (%)", fontsize=11)
    ax4.set_xlabel("年", fontsize=11)
    ax4.legend(loc="lower left")
    ax4.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.text(0.99, 0.01, "データ出典: 世界銀行オープンデータ (World Bank Open Data)", ha="right", fontsize=9, color="gray")

    plt.savefig(output_path, dpi=200)
    print(f"\nグラフを保存しました: {output_path}")


def print_summary_table(df: pd.DataFrame) -> None:
    """直近10年分の要約データをコンソールに出力する"""
    cols_to_show = ["year", "GNI_trillion_yen", "GDP_trillion_yen", "Net_income_from_abroad_trillion_yen", "GNI_per_capita_man_yen"]
    available_cols = [c for c in cols_to_show if c in df.columns]

    sub_df = df.dropna(subset=["GNI_trillion_yen"]).tail(10)[available_cols]
    col_names_jp = {
        "year": "年",
        "GNI_trillion_yen": "名目GNI(兆円)",
        "GDP_trillion_yen": "名目GDP(兆円)",
        "Net_income_from_abroad_trillion_yen": "海外純所得(兆円)",
        "GNI_per_capita_man_yen": "1人当りGNI(万円)",
    }
    display_df = sub_df.rename(columns=col_names_jp).copy()
    display_df["年"] = display_df["年"].astype(int)

    print("\n" + "=" * 60)
    print("【日本の国民所得（直近10年間の推移要約）】")
    print("=" * 60)
    print(display_df.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    print("=" * 60)


def main():
    df = load_all_data()
    print_summary_table(df)
    plot_national_income(df, "japan_national_income.png")
    
    # Web用のJSONデータを出力 (1980年以降)
    sub_df = df[df["year"] >= 1980].copy()
    sub_df.to_json("data.json", orient="records", force_ascii=False, indent=2)
    print("Web用データを保存しました: data.json")


if __name__ == "__main__":
    main()
