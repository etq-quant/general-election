import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="General Election", layout="wide",
)
st.title("General Election")
DATA_PATH = "data/GE_sdata.csv"


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df[~df["state"].isin(["Sarawak", "Sabah"])].copy()
    return df


df = load_data()

my_expander = st.expander(label="Turnout", expanded=True)
with my_expander:
    col1, col2 = st.columns(2)
    malay_turnout = col1.slider("Malay turnout", 0, 100, 80)
    non_malay_turnout = col2.slider("non-Malay turnout", 0, 100, 80)


my_expander = st.expander(label="BN", expanded=True)
with my_expander:
    # st.header("BN")
    BN_col1, BN_col2 = st.columns(2)
    BN_MS = BN_col1.slider("BN Malay Support", 0, 100, 40)
    BN_nMS = BN_col2.slider("BN non-Malay Support", 0, 100, 20)

my_expander = st.expander(label="PH", expanded=True)
with my_expander:
    # st.header("PH")
    PH_col1, PH_col2 = st.columns(2)
    PH_MS = PH_col1.slider("PH Malay Support", 0, 100, 25)
    PH_nMS = PH_col2.slider("PH non-Malay Support", 0, 100, 50)

my_expander = st.expander(label="PN", expanded=True)
with my_expander:
    # st.header("PN")
    PN_col1, PN_col2 = st.columns(2)
    PN_MS = PN_col1.slider("PN Malay Support", 0, 100, 30)
    PN_nMS = PN_col2.slider("PN non-Malay Support", 0, 100, 15)


df["BN"] = (
    df["malay_voter_ratio"] * BN_MS * malay_turnout
    + df["non_malay_voter_ratio"] * BN_nMS * non_malay_turnout
)
df["PH"] = (
    df["malay_voter_ratio"] * PH_MS * malay_turnout
    + df["non_malay_voter_ratio"] * PH_nMS * non_malay_turnout
)
df["PN"] = (
    df["malay_voter_ratio"] * PN_MS * malay_turnout
    + df["non_malay_voter_ratio"] * PN_nMS * non_malay_turnout
)
df["estimated"] = df[["BN", "PH", "PN"]].idxmax(axis=1)


def get_base(a, b):
    PAS_LIST = ["PR-PAS", "GS-PAS"]
    PH_LIST = ["PH-DAP", "PH-PKR", "PH-PAN", "PR-DAP", "PR-PKR"]
    if a in PAS_LIST and b in PAS_LIST:
        return "PN"
    if a in PH_LIST and b in PH_LIST:
        return "PH"
    a = a.split("-")[0]
    b = b.split("-")[0]
    if a == b == "BN":
        return "BN"
    else:
        return None


df["base"] = df.apply(lambda x: get_base(x["2013"], x["2018"]), axis=1)
df["party"] = df["base"].fillna(df["estimated"])

data = {"BN": "#2B65EC", "PH": "#E41B17", "PN": "#659EC7"}


def highlight_party(val):
    return "background-color: {}".format(data.get(val))


sdf = df.groupby(["party"]).size().reset_index().rename(columns={0: "seats"})
sdf["color"] = df["party"].map(data)
chart = (
    alt.Chart(sdf, title="Expected Result")
    .mark_bar()
    .encode(
        alt.X("party"),
        alt.Y("seats"),
        alt.Color(
            "party",
            scale=alt.Scale(domain=list(data.keys()), range=list(data.values())),
        ),
        alt.Tooltip(["party", "seats"]),
    )
)

text = chart.mark_text(
    align="center",
    baseline="bottom",
    fontSize=24,
    # dy=50,
    # dx=50,
    color="black",
).encode(alt.Text("seats"))

chart = (
    (chart + text)
    .properties(height=400)
    .configure_title(fontSize=24)
    .configure_axis(labelFontSize=24, titleFontSize=26)
)

st.altair_chart(chart, use_container_width=True)

cols = [
    "state",
    "constituency",
    "2004",
    "2008",
    "2013",
    "2018",
    "malay_voter_ratio",
    "non_malay_voter_ratio",
    "party",
]

tab1, tab2 = st.tabs(["Estimation", "New Voters"])
with tab1:
    st.dataframe(
        df.set_index("##")[cols].style.applymap(highlight_party, subset=["party"]),
        use_container_width=True,
        height=800,
    )

nvdf = pd.read_csv("data/new_voters.csv")
nvdf = nvdf[~nvdf["state"].isin(["Sarawak", "Sabah"])].copy()
int_types = ["int16", "int32", "int64"]
float_types = ["float16", "float32", "float64"]
num_cols = nvdf.select_dtypes(include=int_types + float_types).columns

front_cols = [
    "##",
    "state",
    "constituency",
    "2004",
    "2008",
    "2013",
    "2018",
    "GE14_registered_voters",
    "GE15_registered_voters",
    "registered_voters_increase",
    "registered_voters_increase_pct",
    "GE14_majority",
    "GE14_majority_pct",
    "GE14_malay_voters",
    "GE14_malay_ratio",
    "GE15_malay_voters",
    "GE15_malay_ratio",
    "GE14_chinese_voters",
    "GE14_chinese_ratio",
    "GE15_chinese_voters",
    "GE15_chinese_ratio",
    "GE14_indian_voters",
    "GE14_indian_ratio",
    "GE15_indian_voters",
    "GE15_indian_ratio",
    "GE14_others_voters",
    "GE14_others_ratio",
    "GE15_others_voters",
    "GE15_others_ratio",
]
GE14_voter_cols = [
    "GE14_{}_voters".format(i) for i in ["malay", "chinese", "indian", "others"]
]
GE15_voter_cols = [
    "GE15_{}_voters".format(i) for i in ["malay", "chinese", "indian", "others"]
]
rearrange_cols = front_cols + [i for i in nvdf.columns if i not in front_cols]
with tab2:
    st.dataframe(
        nvdf[rearrange_cols]
        .set_index(["##", "state", "constituency", "2004", "2008", "2013", "2018"])
        .style.format({i: "{:,.0f}" for i in num_cols})
        .background_gradient(subset=GE14_voter_cols, cmap="Blues", axis=1)
        .background_gradient(subset=GE15_voter_cols, cmap="Reds", axis=1)
        .background_gradient(
            subset="registered_voters_increase_pct", cmap="Oranges", axis=0
        )
        .background_gradient(
            subset="GE14_majority_pct", cmap="Greens", axis=0
        )
        .bar(
            subset=["registered_voters_increase_pct"], color="#54C571", vmin=0, vmax=100
        ),
        use_container_width=True,
        height=800,
    )
