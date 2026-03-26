import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="STC Quality Executive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

PURPLE = "#5A0AA2"
TEAL = "#2EC4D3"
ORANGE = "#FF7A45"
PINK = "#FF4D73"


@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    xlsx_path = os.path.join(base_dir, "Most common Deviations.xlsx")
    csv_path = os.path.join(base_dir, "deviations_data.csv")

    if os.path.exists(xlsx_path):
        df = pd.read_excel(xlsx_path)
    else:
        df = pd.read_csv(csv_path)

    df["District"] = df["District"].astype(str).str.strip().str.upper()
    df["WorkOrderNum"] = df["WorkOrderNum"].astype(str).str.strip()
    df["DeviationName"] = df["DeviationName"].astype(str).str.strip()

    short_map = {
        "NO DEBRIS IS REMAINING ON THE SITE?": "No debris remaining on site",
        "HAVE ALL STC SAFETY MEASUREMENTS BEEN FOLLOWED?": "STC safety measures followed",
        "MUNICIPALITY PERMITS ARE VALID AND RENEWED AS REQUIRED?": "Municipality permits valid",
        "ALL DAMAGE TO PROPERTY (TILES, CURBS, WALLS, ASPHALT) HAS BEEN REPAIRED TO ORIGINAL STATE OR AS PER CUSTOMER REQUEST AT WORK COMPLETION ?": "Damage repaired to original state",
        "PEDESTRIAN PASSES PLACED EVERY 100M IN FRONT OF CUSTOMER HOUSES AS REQUIRED": "Pedestrian passes placed every 100m",
    }

    df["DeviationShort"] = df["DeviationName"].map(short_map).fillna(df["DeviationName"])
    return df


@st.cache_data
def load_kpi():
    base_dir = os.path.dirname(__file__)
    kpi = pd.read_csv(os.path.join(base_dir, "kpi_snapshot.csv"))
    monthly = pd.read_csv(os.path.join(base_dir, "monthly_progress.csv"))
    return kpi, monthly


df = load_data()
kpi, monthly = load_kpi()

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 1rem;
        }}
        .stMetric {{
            background-color: #F8F5FC;
            border: 1px solid #E9DDF8;
            border-radius: 14px;
            padding: 10px 14px;
        }}
        .title-box {{
            background: {PURPLE};
            color: white;
            border-radius: 14px;
            padding: 16px 20px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="title-box"><h2 style="margin:0">STC Project Quality Executive Dashboard</h2>'
    '<p style="margin:6px 0 0 0">Deviation hotspots • WO drilldown • district heatmap • KPI recovery lens</p></div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Filters")
    district_filter = st.multiselect(
        "District",
        options=sorted(df["District"].dropna().unique())
    )
    deviation_filter = st.multiselect(
        "Deviation",
        options=sorted(df["DeviationShort"].dropna().unique())
    )
    wo_filter = st.multiselect(
        "Work Order",
        options=sorted(df["WorkOrderNum"].dropna().unique())
    )

filtered = df.copy()

if district_filter:
    filtered = filtered[filtered["District"].isin(district_filter)]

if deviation_filter:
    filtered = filtered[filtered["DeviationShort"].isin(deviation_filter)]

if wo_filter:
    filtered = filtered[filtered["WorkOrderNum"].isin(wo_filter)]

total_dev = len(filtered)
unique_wo = filtered["WorkOrderNum"].nunique()
unique_dist = filtered["District"].nunique()

repeat_wo_share = 0
if total_dev:
    repeat_wo_share = (filtered["WorkOrderNum"].value_counts().head(5).sum() / total_dev) * 100

row1 = st.columns(4)
row1[0].metric("Total deviations", f"{total_dev:,}")
row1[1].metric("Unique WOs", f"{unique_wo:,}")
row1[2].metric("Districts impacted", f"{unique_dist:,}")
row1[3].metric("Top 5 WO share", f"{repeat_wo_share:.1f}%")

st.subheader("KPI Snapshot")
metric_cols = st.columns(len(kpi))

for i, row in kpi.iterrows():
    target = row["Target"] if not pd.isna(row["Target"]) else None
    delta = row["Current"] - target if target is not None else None
    metric_cols[i].metric(
        row["Metric"],
        f'{row["Current"]:.2f}%',
        None if delta is None else f"{delta:.2f} pts vs target"
    )

colA, colB = st.columns([1.2, 1])

with colA:
    st.subheader("Most Common Deviations")
    top_dev = filtered["DeviationShort"].value_counts().reset_index()
    top_dev.columns = ["Deviation", "Count"]

    fig = px.bar(
        top_dev.sort_values("Count"),
        x="Count",
        y="Deviation",
        orientation="h",
        color_discrete_sequence=[PURPLE]
    )
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("Monthly KPI Progress")
    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Overall KPI %"],
            mode="lines+markers+text",
            text=[f"{v:.2f}%" for v in monthly["Overall KPI %"]],
            textposition="top center",
            line=dict(color="#7B61FF", width=3),
            name="Overall KPI"
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Target %"],
            mode="lines",
            line=dict(color="#9CA3AF", dash="dot"),
            name="Target"
        )
    )

    fig2.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="KPI %"
    )
    st.plotly_chart(fig2, use_container_width=True)

colC, colD = st.columns([1.1, 1.1])

with colC:
    st.subheader("District Heatmap")
    heat = pd.crosstab(filtered["District"], filtered["DeviationShort"])

    if not heat.empty:
        fig3 = px.imshow(
            heat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=[[0, "#F3E8FF"], [1, PURPLE]]
        )
        fig3.update_layout(
            height=430,
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No records for current filters.")

with colD:
    st.subheader("Top Work Orders")
    wo_rank = (
        filtered.groupby(["WorkOrderNum", "District"])
        .size()
        .reset_index(name="Deviation Count")
        .sort_values("Deviation Count", ascending=False)
        .head(15)
    )

    fig4 = px.bar(
        wo_rank.sort_values("Deviation Count"),
        x="Deviation Count",
        y="WorkOrderNum",
        orientation="h",
        color="District",
        color_discrete_sequence=[PURPLE, TEAL, ORANGE, PINK]
    )
    fig4.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("WO Drilldown")
wo_summary = (
    filtered.groupby(["WorkOrderNum", "District", "DeviationShort"])
    .size()
    .reset_index(name="Deviation Count")
    .sort_values(["Deviation Count", "WorkOrderNum"], ascending=[False, True])
)
st.dataframe(wo_summary, use_container_width=True, hide_index=True)

st.subheader("District Owners per Deviation")
owner_rows = []
cross = pd.crosstab(filtered["DeviationShort"], filtered["District"])

for dev in cross.index:
    if cross.loc[dev].sum() == 0:
        continue

    district = cross.loc[dev].idxmax()
    count = int(cross.loc[dev].max())
    share = round((count / cross.loc[dev].sum()) * 100, 1)

    owner_rows.append({
        "Deviation": dev,
        "Highest District": district,
        "Count": count,
        "Share %": share
    })

st.dataframe(pd.DataFrame(owner_rows), use_container_width=True, hide_index=True)

st.subheader("Recovery Action Tracker")
actions = pd.DataFrame(
    [
        ["Housekeeping / debris", "Western & Jeddah WOs", "Daily close-out checklist, foreman signoff, photo evidence", "0-14 days", "Foreman + Site Supervisors + QA/QC"],
        ["H&S non-compliance", "High-repeat WOs", "Mandatory toolbox talk, supervisor stop-work authority, surprise audits", "0-14 days", "Site Supervisors + QA/QC"],
        ["Permit renewal gaps", "Permit coordinators", "Permit aging log, weekly renewal review, no-PO/no-work gate", "0-30 days", "Permit/Admin Lead + PM"],
        ["Property damage restoration", "Riyadh hotspot WOs", "Snag closure team, restoration checklist before WO closure", "0-30 days", "Site Supervisors + QA/QC + Project Managers"],
        ["Repeat offender WOs", "Top 5 WOs", "Escalate to PM, hold payment / performance notice, daily recovery review", "Immediate", "Project Managers"],
    ],
    columns=["Issue", "Focus Area", "Action", "Timeline", "Owner"]
)

st.dataframe(actions, use_container_width=True, hide_index=True)

st.caption("Source: user-provided deviation workbook and dashboard KPI snapshot.")
