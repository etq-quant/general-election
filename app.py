import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from plot import *

st.set_page_config(
    page_title="General Election", layout="wide",
)
st.title("General Election")
DATA_PATH = "data/new_voters.csv"
DATA_PATH_GE15 = "data/voters_ge15.csv"


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH)
    # df = df[~df["state"].isin(["Sarawak", "Sabah"])].copy()
    return df


@st.cache(allow_output_mutation=True)
def load_data_GE15():
    df = pd.read_csv(DATA_PATH_GE15)
    return df


adf = load_data()
df = adf[~adf["state"].isin(["Sarawak", "Sabah"])].copy()
gdf = load_data_GE15()

ag_df = gdf.melt(
    id_vars=["state", "parlimen"],
    value_vars=[i for i in gdf.columns if any(x in i for x in ["male", "female"])],
    var_name="age_group",
)
ag_df["gender"] = ag_df["age_group"].map(lambda x: x.split("_", 1)[0])
ag_df["age_group"] = ag_df["age_group"].map(lambda x: x.split("_", 1)[1])

# v2_tab, v1_tab = st.tabs(["V2", "V1"])

###############
# create tabs #
###############
tab_estimated_result, tab_descriptive_analysis, tab_age_group = st.tabs(
    ["Estimated Result", "Descriptive Analysis", "Age Group Analysis"]
)

with tab_estimated_result:
    data = {}
    # with v2_tab:
    my_expander = st.expander(label="Turnout", expanded=True)
    with my_expander:
        para = [("Malay", 72), ("Chinese", 70), ("Indian", 70), ("Others", 70)]
        st_cols = st.columns(len(para))
        for k, v in enumerate(st_cols):
            data["{}_turnout".format(para[k][0])] = v.slider(
                "{} Turnout".format(para[k][0]), 0, 100, para[k][1]
            )

    my_expander = st.expander(label="BN Support", expanded=True)
    with my_expander:
        para = [("Malay", 38), ("Chinese", 20), ("Indian", 30), ("Others", 20)]
        st_cols = st.columns(len(para))
        for k, v in enumerate(st_cols):
            data["BN_{}_support".format(para[k][0])] = v.slider(
                "{} Support".format(para[k][0]), 0, 100, para[k][1]
            )

    my_expander = st.expander(label="PH Support", expanded=True)
    with my_expander:
        para = [("Malay", 25), ("Chinese", 60), ("Indian", 60), ("Others", 20)]
        st_cols = st.columns(len(para))
        for k, v in enumerate(st_cols):
            data["PH_{}_support".format(para[k][0])] = v.slider(
                "PH {} Support".format(para[k][0]), 0, 100, para[k][1]
            )

    my_expander = st.expander(label="PN Support", expanded=True)
    with my_expander:
        para = [("Malay", 25), ("Chinese", 15), ("Indian", 10), ("Others", 20)]
        st_cols = st.columns(len(para))
        for k, v in enumerate(st_cols):
            data["PN_{}_support".format(para[k][0])] = v.slider(
                "PN {} Support".format(para[k][0]), 0, 100, para[k][1]
            )

    my_expander = st.expander(label="Safe Threshold", expanded=False)
    with my_expander:
        data["safe_threshold"] = st.slider(
            "Safe Threshold: percentage of majority - percentage of new voters increase",
            -100,
            100,
            -100,
        )

    my_expander = st.expander(label="Safe Combo", expanded=False)
    with my_expander:
        data["safe_combo"] = st.multiselect(
            "Safe Combo",
            options=["2004", "2008", "2013", "2018"],
            default=["2013", "2018"],
        )

    for i in ["BN", "PH", "PN"]:
        df[i] = (
            data["Malay_turnout"]
            * data[f"{i}_Malay_support"]
            * df["GE15_malay_voters"]
            / 10000
            + data["Chinese_turnout"]
            * data[f"{i}_Chinese_support"]
            * df["GE15_chinese_voters"]
            / 10000
            + data["Indian_turnout"]
            * data[f"{i}_Indian_support"]
            * df["GE15_indian_voters"]
            / 10000
            + data["Others_turnout"]
            * data[f"{i}_Others_support"]
            * df["GE15_others_voters"]
            / 10000
        )

    df["estimate_party"] = df[["BN", "PH", "PN"]].idxmax(axis=1)
    party_color = {"BN": "#2B65EC", "PH": "#E41B17", "PN": "#659EC7"}

    def highlight_party(val):
        return "background-color: {}".format(party_color.get(val))

    def get_party(x):
        PN_LIST = ["PR-PAS", "GS-PAS", "PH-PPBM", "BA-PAS"]
        PH_LIST = ["PH-DAP", "PH-PKR", "PH-PAN", "PR-DAP", "PR-PKR", "BA-PKR"]
        if x in PN_LIST:
            return "PN"
        if x in PH_LIST:
            return "PH"
        x = x.split("-")[0]
        if x == "BN":
            return "BN"
        else:
            return None

    df["safe_threshold"] = (
        df["GE14_majority_pct"] - df["registered_voters_increase_pct"]
    )

    for i in ["2004", "2008", "2013", "2018"]:
        df[f"{i}_party"] = df[i].map(get_party)

    if data["safe_combo"]:
        df["base"] = df[[f"{i}_party" for i in data["safe_combo"]]].nunique(axis=1) == 1
        df["base"] = df["base"] & (df["safe_threshold"] >= data["safe_threshold"])
        sname = "{}_party".format(data["safe_combo"][-1])
        df["base_party"] = df[["base", sname]].apply(
            lambda x: x[sname] if x["base"] else None, axis=1,
        )
    else:
        df["base"] = False
        df["base_party"] = None

    df["party"] = df["base_party"].fillna(df["estimate_party"])

    GE14_voter_cols = [
        "GE14_{}_ratio".format(i) for i in ["malay", "chinese", "indian", "others"]
    ]
    GE15_voter_cols = [
        "GE15_{}_ratio".format(i) for i in ["malay", "chinese", "indian", "others"]
    ]

    int_types = ["int16", "int32", "int64"]
    float_types = ["float16", "float32", "float64"]
    num_cols = df.select_dtypes(include=int_types + float_types).columns

    tab_chart, tab_data, tab_raw_data = st.tabs(["Chart", "Data", "Raw Data"])

    with tab_chart:
        st.subheader("Estimated Result Excluded Sabah and Sarawak")
        sdf = df.groupby(["party"]).size().reset_index().rename(columns={0: "seats"})
        chart = (
            alt.Chart(sdf, title="Estimated Result")
            .mark_bar()
            .encode(
                alt.X("party"),
                alt.Y("seats"),
                alt.Color(
                    "party",
                    scale=alt.Scale(
                        domain=list(party_color.keys()),
                        range=list(party_color.values()),
                    ),
                ),
                alt.Tooltip(["party", "seats"]),
            )
        )

        text = chart.mark_text(
            align="center", baseline="bottom", fontSize=24, color="black",
        ).encode(alt.Text("seats"))

        chart = (
            (chart + text)
            .properties(height=400)
            .configure_title(fontSize=24)
            .configure_axis(labelFontSize=24, titleFontSize=26)
        )

        st.altair_chart(chart, use_container_width=True)

    with tab_data:
        front_cols = [
            "##",
            "state",
            "constituency",
            "2004",
            "2008",
            "2013",
            "2018",
            "base_party",
            "estimate_party",
            "BN",
            "PH",
            "PN",
            "party",
            "GE14_registered_voters",
            "GE15_registered_voters",
            "registered_voters_increase_pct",
            "GE14_majority_pct",
            "safe_threshold",
            "registered_voters_increase",
            "GE14_majority",
        ]
        st.dataframe(
            df[front_cols]
            .set_index(["##", "state", "constituency"])
            .style.format({i: "{:,.0f}" for i in num_cols})
            .applymap(highlight_party, subset=["party"])
            .background_gradient(
                subset="registered_voters_increase_pct", cmap="Oranges", axis=0
            )
            .background_gradient(subset="GE14_majority_pct", cmap="Greens", axis=0)
            .background_gradient(subset="safe_threshold", cmap="Blues", axis=0)
            .highlight_max(subset=["BN", "PH", "PN"], color="#AAF0D1", axis=1),
            use_container_width=True,
            height=800,
        )

    with tab_raw_data:
        front_cols = [
            "##",
            "state",
            "constituency",
            "2004",
            "2008",
            "2013",
            "2018",
            "base_party",
            "estimate_party",
            "BN",
            "PH",
            "PN",
            "party",
            "GE14_registered_voters",
            "GE15_registered_voters",
            "registered_voters_increase_pct",
            "GE14_majority_pct",
            "safe_threshold",
            "registered_voters_increase",
            "GE14_majority",
            "GE14_malay_ratio",
            "GE15_malay_ratio",
            "GE14_chinese_ratio",
            "GE15_chinese_ratio",
            "GE14_indian_ratio",
            "GE15_indian_ratio",
            "GE14_others_ratio",
            "GE15_others_ratio",
            "GE14_malay_voters",
            "GE15_malay_voters",
            "GE14_chinese_voters",
            "GE15_chinese_voters",
            "GE14_indian_voters",
            "GE15_indian_voters",
            "GE14_others_voters",
            "GE15_others_voters",
        ]
        rearrange_cols = front_cols + [i for i in df.columns if i not in front_cols]
        st.dataframe(
            df[rearrange_cols]
            .set_index(["##", "state", "constituency"])
            .style.format({i: "{:,.0f}" for i in num_cols})
            .applymap(highlight_party, subset=["party"])
            .background_gradient(
                subset=GE14_voter_cols + GE15_voter_cols, cmap="Blues", axis=1
            )
            .background_gradient(
                subset="registered_voters_increase_pct", cmap="Oranges", axis=0
            )
            .background_gradient(subset="GE14_majority_pct", cmap="Greens", axis=0)
            .background_gradient(subset="safe_threshold", cmap="Blues", axis=0)
            .highlight_max(subset=["BN", "PH", "PN"], color="#AAF0D1", axis=1),
            use_container_width=True,
            height=800,
        )


with tab_descriptive_analysis:

    tdf1 = get_table1(adf, gdf)
    st.subheader("New Registered Voters by States")
    st.table(tdf1)

    tab1, tab2 = st.tabs(["tab1", "tab2"])
    with tab1:
        tdf2 = get_race_table(adf)
        st.subheader("New Registered Voters by States and Race")
        st.table(tdf2)
    with tab2:
        tdf22 = get_race_table2(adf)
        st.subheader("New Registered Voters by States and Race")
        st.dataframe(tdf22, height=530)

with tab_age_group:
    tab_ag_state, tab_ag_parlimen, tab_ag_data, = st.tabs(["State", "Parlimen", "Data"])

    with tab_ag_data:
        ag_data_df = gdf.groupby(["state", "parlimen"])[
            ["total"]
            + [i for i in gdf.columns if any([j for j in ["male", "female"] if j in i])]
        ].sum()
        ag_data_df = ag_data_df.style.background_gradient(
            subset=[
                i for i in gdf.columns if any([j for j in ["male", "female"] if j in i])
            ],
            cmap="BuPu",
            axis=0,
        )
        st.subheader("Age Group Data")
        st.dataframe(ag_data_df, height=800)

    with tab_ag_state:
        state = st.multiselect("state", ag_df["state"].unique(), default=None)
        if state:
            for s in state:
                fig = plot_age_group(ag_df[ag_df["state"] == s], s)
                st.plotly_chart(fig)
        else:
            fig = plot_age_group(ag_df, "Malaysia")
            st.plotly_chart(fig)

    with tab_ag_parlimen:
        parlimen = st.multiselect(
            "parlimen", ag_df["parlimen"].unique(), default="P.001 Padang Besar"
        )
        for p in parlimen:
            fig = plot_age_group(ag_df[ag_df["parlimen"] == p], p)
            st.plotly_chart(fig)
