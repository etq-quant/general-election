import pandas as pd
import numpy as np
import plotly.graph_objs as go


def get_table1(df, gdf):
    tdf = pd.melt(
        df[["state", "GE14_registered_voters", "GE15_registered_voters"]].rename(
            columns={"GE14_registered_voters": "GE14", "GE15_registered_voters": "GE15"}
        ),
        id_vars=["state"],
        var_name="GE",
        value_name="registered_voters",
    )
    tdf = tdf.pivot_table(
        index="state", columns="GE", values="registered_voters", aggfunc="sum"
    )
    tdf.columns.name = None
    tdf.index.name = None
    tdf.loc["Total"] = tdf.sum()
    tdf["registered_voters_increase"] = tdf["GE15"] - tdf["GE14"]
    tdf["registered_voters_increase_pct"] = (tdf["GE15"] / tdf["GE14"] - 1) * 100

    ydf = gdf.groupby(["state"])[["male_18_20", "female_18_20"]].sum()
    ydf["young_voters"] = ydf.sum(axis=1)
    ydf.loc["Total"] = ydf.sum()
    tdf = tdf.merge(ydf, left_index=True, right_index=True, how="left")
    tdf["young_voters_pct"] = tdf["young_voters"] / tdf["GE15"] * 100

    u = tdf.index.get_level_values(0)

    tdf = (
        tdf.style.format("{:,.0f}")
        .format("{:,.2f}%", subset=[i for i in tdf.columns if i.endswith("_pct")])
        .background_gradient(
            subset=pd.IndexSlice[
                u[:-1], ["GE14", "GE15", "young_voters", "young_voters_pct"]
            ],
            cmap="pink_r",
            axis=0,
        )
        .bar(
            subset=pd.IndexSlice[u[:-1], "registered_voters_increase"], color="#FED8B1"
        )
        .bar(
            subset=pd.IndexSlice[u[:-1], "registered_voters_increase_pct"],
            color="#FBE7A1",
        )
        .bar(subset=pd.IndexSlice[u[:-1], "male_18_20"], color="#1974D2")
        .bar(subset=pd.IndexSlice[u[:-1], "female_18_20"], color="#F67280")
        .applymap(lambda x: "background-color: #BCC6CC", subset=pd.IndexSlice[u[-1], :])
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [("background-color", "#36454F"), ("color", "white")],
                },
            ]
        )
    )
    return tdf


def get_race_table(df):
    cols = [
        f"{i}_{j}_voters"
        for i in ["GE14", "GE15"]
        for j in ["malay", "chinese", "indian", "others"]
    ]
    tdf = df.groupby(["state"])[cols].sum()
    for i in tdf.columns:
        tdf[i] = tdf[i].astype(int)

    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"{i}_voters_increase"] = tdf[f"GE15_{i}_voters"] - tdf[f"GE14_{i}_voters"]
    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"{i}_voters_increase_pct"] = (
            tdf[f"GE15_{i}_voters"] / tdf[f"GE14_{i}_voters"] - 1
        ) * 100

    tdf["GE14_voters"] = tdf[
        [
            "GE14_malay_voters",
            "GE14_chinese_voters",
            "GE14_indian_voters",
            "GE14_others_voters",
        ]
    ].sum(axis=1)
    tdf["GE15_voters"] = tdf[
        [
            "GE15_malay_voters",
            "GE15_chinese_voters",
            "GE15_indian_voters",
            "GE15_others_voters",
        ]
    ].sum(axis=1)

    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"GE14_{i}_ratio"] = tdf[f"GE14_{i}_voters"] / tdf["GE14_voters"] * 100
    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"GE15_{i}_ratio"] = tdf[f"GE15_{i}_voters"] / tdf["GE15_voters"] * 100

    tdf = tdf.replace(np.inf, np.nan)
    tdf = tdf[
        [i for i in tdf.columns if i.endswith("increase")]
        + [i for i in tdf.columns if i.endswith("increase_pct")]
        + [i for i in tdf.columns if "increase" not in i]
    ]

    tdf.index.name = None

    green_bar_color = "#54C571"
    red_bar_color = "#FF6347"
    tdf = (
        tdf.style.format("{:,.0f}")
        .format("{:,.2f}%", subset=[i for i in tdf.columns if i.endswith("_pct")])
        .bar(
            subset=[i for i in tdf.columns if i.endswith("increase_pct")],
            color=green_bar_color,
            vmin=0,
            axis=0,
            align="zero",
        )
        .bar(
            subset=(tdf["malay_voters_increase_pct"] <= 0, "malay_voters_increase_pct"),
            color=red_bar_color,
            vmax=0,
            axis=0,
            align="zero",
        )
        .bar(
            subset=(
                tdf["chinese_voters_increase_pct"] <= 0,
                "chinese_voters_increase_pct",
            ),
            color=red_bar_color,
            vmax=0,
            axis=0,
            align="zero",
        )
        .bar(
            subset=(
                tdf["indian_voters_increase_pct"] <= 0,
                "indian_voters_increase_pct",
            ),
            color=red_bar_color,
            vmax=0,
            axis=0,
            align="zero",
        )
        .bar(
            subset=(
                tdf["others_voters_increase_pct"] <= 0,
                "others_voters_increase_pct",
            ),
            color=red_bar_color,
            vmax=0,
            axis=0,
            align="zero",
        )
        .background_gradient(
            subset=[i for i in tdf.columns if i.endswith("increase")],
            cmap="Greens",
            vmin=0,
            axis=0,
        )
        .background_gradient(
            subset=(tdf["malay_voters_increase"] <= 0, "malay_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["chinese_voters_increase"] <= 0, "chinese_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["indian_voters_increase"] <= 0, "indian_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["others_voters_increase"] <= 0, "others_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .highlight_null(
            subset=[i for i in tdf.columns if i.endswith("increase_pct")],
            null_color="#36454F",
        )
        .bar(
            subset=[
                "GE15_chinese_voters",
                "GE15_indian_voters",
                "GE15_others_voters",
                "GE15_malay_voters",
            ],
            color="#FBE7A1",
        )
        .bar(subset=[i for i in tdf.columns if i.endswith("_ratio")], color="#FA8072",)
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [("background-color", "#36454F"), ("color", "white")],
                },
                {
                    "selector": "td, th",
                    "props": [("border", "1px solid grey !important")],
                },
            ]
        )
    )
    return tdf


def get_race_table2(df):
    cols = [
        f"{i}_{j}_voters"
        for i in ["GE14", "GE15"]
        for j in ["malay", "chinese", "indian", "others"]
    ]
    tdf = df.groupby(["state"])[cols].sum()
    for i in tdf.columns:
        tdf[i] = tdf[i].astype(int)

    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"{i}_voters_increase"] = tdf[f"GE15_{i}_voters"] - tdf[f"GE14_{i}_voters"]
    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"{i}_voters_increase_pct"] = (
            tdf[f"GE15_{i}_voters"] / tdf[f"GE14_{i}_voters"] - 1
        ) * 100

    tdf["GE14_voters"] = tdf[
        [
            "GE14_malay_voters",
            "GE14_chinese_voters",
            "GE14_indian_voters",
            "GE14_others_voters",
        ]
    ].sum(axis=1)
    tdf["GE15_voters"] = tdf[
        [
            "GE15_malay_voters",
            "GE15_chinese_voters",
            "GE15_indian_voters",
            "GE15_others_voters",
        ]
    ].sum(axis=1)

    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"GE14_{i}_ratio"] = tdf[f"GE14_{i}_voters"] / tdf["GE14_voters"] * 100
    for i in ["malay", "chinese", "indian", "others"]:
        tdf[f"GE15_{i}_ratio"] = tdf[f"GE15_{i}_voters"] / tdf["GE15_voters"] * 100

    tdf = tdf.replace(np.inf, np.nan)
    tdf = tdf[
        [i for i in tdf.columns if i.endswith("increase")]
        + [i for i in tdf.columns if i.endswith("increase_pct")]
        + [i for i in tdf.columns if "increase" not in i]
    ]

    tdf.index.name = None

    green_bar_color = "#54C571"
    red_bar_color = "#FF6347"
    tdf = (
        tdf.style.format("{:,.0f}")
        .format("{:,.2f}%", subset=[i for i in tdf.columns if i.endswith("_pct")])
        .background_gradient(
            subset=[i for i in tdf.columns if i.endswith("increase")],
            cmap="Greens",
            vmin=0,
            axis=0,
        )
        .background_gradient(
            subset=(tdf["malay_voters_increase"] <= 0, "malay_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["chinese_voters_increase"] <= 0, "chinese_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["indian_voters_increase"] <= 0, "indian_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(tdf["others_voters_increase"] <= 0, "others_voters_increase"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=[i for i in tdf.columns if i.endswith("increase_pct")],
            cmap="Greens",
            vmin=0,
            axis=0,
        )
        .background_gradient(
            subset=(tdf["malay_voters_increase_pct"] <= 0, "malay_voters_increase_pct"),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(
                tdf["chinese_voters_increase_pct"] <= 0,
                "chinese_voters_increase_pct",
            ),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(
                tdf["indian_voters_increase_pct"] <= 0,
                "indian_voters_increase_pct",
            ),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=(
                tdf["others_voters_increase_pct"] <= 0,
                "others_voters_increase_pct",
            ),
            cmap="OrRd_r",
            axis=0,
        )
        .background_gradient(
            subset=[i for i in tdf.columns if i.endswith("_ratio")],
            cmap="OrRd",
            axis=0,
        )
        .highlight_null(
            subset=[i for i in tdf.columns if i.endswith("increase_pct")],
            null_color="#36454F",
        )
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [("background-color", "#36454F"), ("color", "white")],
                },
                {
                    "selector": "td, th",
                    "props": [("border", "1px solid grey !important")],
                },
            ]
        )
    )
    return tdf
