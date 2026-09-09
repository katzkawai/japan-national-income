# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "matplotlib",
#     "pandas",
#     "requests",
#     "seaborn",
# ]
# ///
"""日本の国民所得（名目・実質 GNI）を可視化するスクリプト

世界銀行オープンデータAPIから日本の各種経済指標を取得し、
名目および実質の国民総所得(GNI)、国内総生産(GDP)、1人当たり所得、成長率の推移をプロットします。

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
    # 名目指標 (Nominal)
    "NY.GNP.MKTP.CN": "GNI_nominal_yen",       # 名目GNI (円)
    "NY.GDP.MKTP.CN": "GDP_nominal_yen",       # 名目GDP (円)
    "NY.GNP.PCAP.CN": "GNI_pc_nominal_yen",    # 1人当たり名目GNI (円)
    "NY.GNP.MKTP.CD": "GNI_nominal_usd",       # 名目GNI (米ドル)
    "NY.GNP.PCAP.CD": "GNI_pc_nominal_usd",    # 1人当たり名目GNI (米ドル, Atlas法)
    # 実質指標 (Real / Constant LCU: 基準年固定価格)
    "NY.GNP.MKTP.KN": "GNI_real_yen",          # 実質GNI (円)
    "NY.GDP.MKTP.KN": "GDP_real_yen",          # 実質GDP (円)
    "NY.GNP.PCAP.KN": "GNI_pc_real_yen",       # 1人当たり実質GNI (円)
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
    print("世界銀行APIから日本の経済データ（名目・実質）を取得中...")
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
    # 名目 (兆円)
    if "GNI_nominal_yen" in merged_df.columns:
        merged_df["GNI_nominal_trillion"] = merged_df["GNI_nominal_yen"] / 1e12
    if "GDP_nominal_yen" in merged_df.columns:
        merged_df["GDP_nominal_trillion"] = merged_df["GDP_nominal_yen"] / 1e12
    # 実質 (兆円)
    if "GNI_real_yen" in merged_df.columns:
        merged_df["GNI_real_trillion"] = merged_df["GNI_real_yen"] / 1e12
    if "GDP_real_yen" in merged_df.columns:
        merged_df["GDP_real_trillion"] = merged_df["GDP_real_yen"] / 1e12

    # 1人当たり (万円)
    if "GNI_pc_nominal_yen" in merged_df.columns:
        merged_df["GNI_pc_nominal_man_yen"] = merged_df["GNI_pc_nominal_yen"] / 1e4
    if "GNI_pc_real_yen" in merged_df.columns:
        merged_df["GNI_pc_real_man_yen"] = merged_df["GNI_pc_real_yen"] / 1e4

    # 海外からの純所得 (GNI - GDP)
    if "GNI_nominal_trillion" in merged_df.columns and "GDP_nominal_trillion" in merged_df.columns:
        merged_df["Net_income_nominal_trillion"] = (
            merged_df["GNI_nominal_trillion"] - merged_df["GDP_nominal_trillion"]
        )
    if "GNI_real_trillion" in merged_df.columns and "GDP_real_trillion" in merged_df.columns:
        merged_df["Net_income_real_trillion"] = (
            merged_df["GNI_real_trillion"] - merged_df["GDP_real_trillion"]
        )

    # 前年比成長率 (%)
    if "GNI_nominal_yen" in merged_df.columns:
        merged_df["GNI_growth_nominal"] = merged_df["GNI_nominal_yen"].pct_change() * 100
    if "GNI_real_yen" in merged_df.columns:
        merged_df["GNI_growth_real"] = merged_df["GNI_real_yen"].pct_change() * 100
    if "GDP_real_yen" in merged_df.columns:
        merged_df["GDP_growth_real"] = merged_df["GDP_real_yen"].pct_change() * 100

    return merged_df


def plot_national_income(df: pd.DataFrame, output_path: str = "japan_national_income.png") -> None:
    """名目・実質の国民所得可視化グラフを生成・保存する"""
    sub_df = df[df["year"] >= 1980].copy()

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("日本の国民所得（GNI）推移と分析：名目 vs 実質 (1980年〜)", fontsize=18, fontweight="bold", y=0.98)

    # 1. 国民総所得(GNI)：名目 vs 実質の推移（兆円）
    ax1 = axes[0, 0]
    ax1.plot(sub_df["year"], sub_df["GNI_nominal_trillion"], label="名目GNI (額面)", color="#1f77b4", linewidth=2.5)
    ax1.plot(sub_df["year"], sub_df["GNI_real_trillion"], label="実質GNI (物価調整後)", color="#2ca02c", linewidth=2.5, linestyle="--")
    # 名目と実質の乖離（インフレ/デフレ効果）
    valid_mask = sub_df["GNI_nominal_trillion"].notna() & sub_df["GNI_real_trillion"].notna()
    ax1.fill_between(
        sub_df.loc[valid_mask, "year"],
        sub_df.loc[valid_mask, "GNI_real_trillion"],
        sub_df.loc[valid_mask, "GNI_nominal_trillion"],
        where=(sub_df.loc[valid_mask, "GNI_nominal_trillion"] >= sub_df.loc[valid_mask, "GNI_real_trillion"]),
        color="#ff7f0e",
        alpha=0.2,
        label="インフレ要因（名目 > 実質）"
    )
    ax1.set_title("① 国民総所得(GNI)：名目 vs 実質の推移", fontsize=13, fontweight="bold")
    ax1.set_ylabel("兆円", fontsize=11)
    ax1.set_xlabel("年", fontsize=11)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. 実質ベースでの比較：実質GNI vs 実質GDP（兆円）
    ax2 = axes[0, 1]
    ax2.plot(sub_df["year"], sub_df["GNI_real_trillion"], label="実質GNI (国民所得)", color="#2ca02c", linewidth=2.5)
    ax2.plot(sub_df["year"], sub_df["GDP_real_trillion"], label="実質GDP (国内生産)", color="#9467bd", linewidth=2, linestyle=":")
    # 実質海外純所得の塗りつぶし
    mask_real = sub_df["GNI_real_trillion"].notna() & sub_df["GDP_real_trillion"].notna()
    ax2.fill_between(
        sub_df.loc[mask_real, "year"],
        sub_df.loc[mask_real, "GDP_real_trillion"],
        sub_df.loc[mask_real, "GNI_real_trillion"],
        where=(sub_df.loc[mask_real, "GNI_real_trillion"] >= sub_df.loc[mask_real, "GDP_real_trillion"]),
        color="#2ca02c",
        alpha=0.2,
        label="実質海外純所得 (受取超過)"
    )
    ax2.set_title("② 実質ベースの比較：実質GNI と 実質GDP", fontsize=13, fontweight="bold")
    ax2.set_ylabel("兆円 (実質固定価格)", fontsize=11)
    ax2.set_xlabel("年", fontsize=11)
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle=":", alpha=0.6)

    # 3. 1人当たりGNI：名目 vs 実質（万円）
    ax3 = axes[1, 0]
    ax3.plot(sub_df["year"], sub_df["GNI_pc_nominal_man_yen"], label="1人当たり名目GNI (額面)", color="#1f77b4", linewidth=2.5)
    ax3.plot(sub_df["year"], sub_df["GNI_pc_real_man_yen"], label="1人当たり実質GNI (購買力換算)", color="#2ca02c", linewidth=2.5, linestyle="--")
    ax3.set_title("③ 1人当たり国民所得：名目 vs 実質 (万円)", fontsize=13, fontweight="bold")
    ax3.set_ylabel("万円 / 人", fontsize=11)
    ax3.set_xlabel("年", fontsize=11)
    ax3.legend(loc="upper left")
    ax3.grid(True, linestyle=":", alpha=0.6)

    # 4. 前年比成長率：名目GNI成長率 vs 実質GNI成長率 (%)
    ax4 = axes[1, 1]
    ax4.plot(sub_df["year"], sub_df["GNI_growth_nominal"], label="名目GNI成長率 (%)", color="#1f77b4", linewidth=2)
    ax4.plot(sub_df["year"], sub_df["GNI_growth_real"], label="実質GNI成長率 (%)", color="#2ca02c", linewidth=2, linestyle="--")
    ax4.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax4.set_title("④ 前年比成長率：名目GNI vs 実質GNI (%)", fontsize=13, fontweight="bold")
    ax4.set_ylabel("前年比 (%)", fontsize=11)
    ax4.set_xlabel("年", fontsize=11)
    ax4.legend(loc="lower left")
    ax4.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.text(0.99, 0.01, "データ出典: 世界銀行オープンデータ (World Bank Open Data)", ha="right", fontsize=9, color="gray")

    plt.savefig(output_path, dpi=200)
    print(f"\nグラフを保存しました: {output_path}")


def print_summary_table(df: pd.DataFrame) -> None:
    """直近10年分の要約データ（名目・実質）をコンソールに出力する"""
    cols = [
        "year",
        "GNI_nominal_trillion",
        "GNI_real_trillion",
        "GDP_nominal_trillion",
        "GDP_real_trillion",
        "GNI_pc_nominal_man_yen",
        "GNI_pc_real_man_yen",
    ]
    available_cols = [c for c in cols if c in df.columns]

    sub_df = df.dropna(subset=["GNI_nominal_trillion"]).tail(10)[available_cols]
    col_names_jp = {
        "year": "年",
        "GNI_nominal_trillion": "名目GNI(兆円)",
        "GNI_real_trillion": "実質GNI(兆円)",
        "GDP_nominal_trillion": "名目GDP(兆円)",
        "GDP_real_trillion": "実質GDP(兆円)",
        "GNI_pc_nominal_man_yen": "1人当り名目(万)",
        "GNI_pc_real_man_yen": "1人当り実質(万)",
    }
    display_df = sub_df.rename(columns=col_names_jp).copy()
    display_df["年"] = display_df["年"].astype(int)

    print("\n" + "=" * 80)
    print("【日本の国民所得：名目と実質の推移（直近10年間）】")
    print("=" * 80)
    print(display_df.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
    print("=" * 80)


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
