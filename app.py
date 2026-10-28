
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="F1 Race Intelligence",
    page_icon="🏎️",
    layout="wide",
)

API = "https://api.jolpi.ca/ergast/f1"




@st.cache_data(ttl=3600, show_spinner=False)
def load_season(year):
    url = f"{API}/{year}/results.json"
    response = requests.get(
        url,
        params={"limit": 1000, "offset": 0},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()["MRData"]
    rows = []

    for race in data["RaceTable"]["Races"]:
        for result in race.get("Results", []):
            driver = result["Driver"]
            constructor = result["Constructor"]
            position = result.get("position", "")

            rows.append({
                "Season": int(race["season"]),
                "Round": int(race["round"]),
                "Race": race["raceName"],
                "Country": race["Circuit"]["Location"]["country"],
                "Driver": driver["givenName"] + " " + driver["familyName"],
                "Team": constructor["name"],
                "Position": int(position) if position.isdigit() else None,
                "Points": float(result["points"]),
                "Status": result["status"],
            })

    return pd.DataFrame(rows)



st.markdown(
    """
    <h1 style="color:#e10600;">🏎️ F1 RACE INTELLIGENCE</h1>
    <p>Data-driven insights into Formula 1 drivers, teams and race results.</p>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Dashboard Filters")
    year = st.selectbox(
        "Select season",
        list(range(2025, 2009, -1)),
    )

try:
    with st.spinner(f"Loading {year} Formula 1 results..."):
        df = load_season(year)

    if df.empty:
        st.warning("No race results were returned for this season.")
        st.stop()

except Exception as error:
    st.error("Could not load the race data.")
    st.exception(error)
    st.stop()

st.caption(
    f"Season: {year} | Race entries: {len(df):,} | "
    "Source: Jolpica F1 API"
)

driver_stats = (
    df.groupby("Driver", as_index=False)
    .agg(
        Points=("Points", "sum"),
        Wins=("Position", lambda s: (s == 1).sum()),
        Podiums=("Position", lambda s: s.isin([1, 2, 3]).sum()),
        Races=("Race", "nunique"),
    )
    .sort_values("Points", ascending=False)
)

team_stats = (
    df.groupby("Team", as_index=False)
    .agg(Points=("Points", "sum"))
    .sort_values("Points", ascending=False)
)

race_count = df["Race"].nunique()
driver_count = df["Driver"].nunique()
team_count = df["Team"].nunique()

non_finish = ~df["Status"].str.lower().isin(
    ["finished", "disqualified", "excluded", "not classified"]
)
non_finish_rate = non_finish.mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Grand Prix", race_count)
c2.metric("Drivers", driver_count)
c3.metric("Constructors", team_count)
c4.metric("Non-finish statuses", f"{non_finish_rate:.1f}%")

st.info(
    "The non-finish metric uses recorded result statuses. It is not a "
    "confirmed mechanical-failure rate."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Driver Performance",
    "Team Analysis",
    "Country Insights",
    "Race Reliability",
])

with tab1:
    st.subheader(f"Driver Championship — {year}")

    top_drivers = driver_stats.head(15).sort_values("Points")

    fig = px.bar(
        top_drivers,
        x="Points",
        y="Driver",
        orientation="h",
        color="Points",
        color_continuous_scale=["#7f0000", "#e10600", "#ff7777"],
        title="Top 15 Drivers by Championship Points",
    )
    fig.update_layout(
        template="plotly_dark",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Complete Driver Statistics")
    st.dataframe(driver_stats, use_container_width=True)

with tab2:
    st.subheader(f"Constructor Performance — {year}")

    fig = px.bar(
        team_stats.sort_values("Points"),
        x="Points",
        y="Team",
        orientation="h",
        color="Points",
        color_continuous_scale=["#7f0000", "#e10600"],
        title="Constructor Championship Points",
    )
    fig.update_layout(
        template="plotly_dark",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Grand Prix by Host Country")

    country_stats = (
        df[["Race", "Country"]]
        .drop_duplicates()
        .groupby("Country", as_index=False)
        .size()
        .rename(columns={"size": "Grand Prix"})
        .sort_values("Grand Prix", ascending=False)
    )

    fig = px.bar(
        country_stats,
        x="Country",
        y="Grand Prix",
        color="Grand Prix",
        color_continuous_scale=["#7f0000", "#e10600"],
        title="Number of Events Hosted by Country",
    )
    fig.update_layout(
        template="plotly_dark",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(country_stats, use_container_width=True)

with tab4:
    st.subheader("Race Result Status by Constructor")

    status_stats = (
        df.groupby(["Team", "Status"], as_index=False)
        .size()
        .rename(columns={"size": "Entries"})
    )

    fig = px.bar(
        status_stats,
        x="Team",
        y="Entries",
        color="Status",
        title="Finishes, Retirements and Other Recorded Statuses",
    )
    fig.update_layout(
        template="plotly_dark",
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Recorded statuses do not independently establish the cause "
        "of a retirement or non-finish."
    )

st.divider()
st.caption(
    "F1 Race Intelligence | Educational project | "
    "Historical results from the Jolpica F1 API."
)
