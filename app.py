import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_cleaning import load_and_clean_data
from data_cleaning import add_iso_codes
import plotly.express as px
import altair as alt
import numpy as np
from vega_datasets import data

st.set_page_config(
    page_title="World Happiness Report 2026",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Main Content Width
# -----------------------------------------------------------------------------

st.markdown("""
<style>
.block-container {
    max-width: 1200px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Load Data
# -----------------------------------------------------------------------------

df = load_and_clean_data(
    "data/world_happiness_Update_report_2026.csv"
)

df = add_iso_codes(df)


# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------

st.title("World Happiness Report 2026 🌍")

st.write(
    "An exploration of what drives happiness across "
    "147 countries, based on the World Happiness "
    "Update Report 2026, released on March 20, 2026, using Gallup World Poll data from 2023–2025."
)

st.divider()



# -----------------------------------------------------------------------------
# Part I: Overview
# -----------------------------------------------------------------------------



st.header("Part I: Overview")

st.write(
    "**What does the global happiness landscape look like across the 147 countries?** "
    "This overview establishes the baseline for the analysis by looking at the "
    "overall happiness score, the highest-scoring country, the number of countries "
    "covered, and their average GDP per capita. These indicators provide a starting "
    "point for understanding how happiness varies across countries before examining "
    "the factors that may explain these differences."
)


# -----------------------------------------------------------------------------
# Distribution Sparkline
# -----------------------------------------------------------------------------

def draw_distribution(data, column, color="#1CBCF5", bins=14):

    values = data[column].dropna()

    counts, edges = np.histogram(
        values,
        bins=bins
    )

    centers = (edges[:-1] + edges[1:]) / 2

    distribution_df = pd.DataFrame({
        "value": centers,
        "count": counts,
        "lower": edges[:-1],
        "upper": edges[1:]
    })

    fig = px.line(
        distribution_df,
        x="value",
        y="count",
        markers=True
    )

    fig.update_traces(
        line=dict(
            color=color,
            width=2
        ),
        marker=dict(
            size=4
        ),
        customdata=distribution_df[
            ["lower", "upper"]
        ],
        hovertemplate=(
            "<b>%{customdata[0]:.2f} – %{customdata[1]:.2f}</b><br>"
            "Countries: %{y}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=80,
        margin=dict(
            l=5,
            r=5,
            t=5,
            b=5
        ),
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False
        ),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# -----------------------------------------------------------------------------
# KPI Cards
# -----------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


# -----------------------------------------------------------------------------
# KPI 1: Countries Analyzed
# -----------------------------------------------------------------------------

with col1:
    with st.container(border=True):

        st.metric(
            "Countries Analyzed",
            len(df)
        )

        # Keep card height consistent with the other KPIs
        st.markdown(
            "<div style='height: 122px;'></div>",
            unsafe_allow_html=True
        )


# -----------------------------------------------------------------------------
# KPI 2: Average Happiness Score
# -----------------------------------------------------------------------------

with col2:
    with st.container(border=True):

        avg_score = df["score"].mean()
        delta = avg_score - 5.0

        st.metric(
            "Average Happiness Score",
            f"{avg_score:.2f}",
            f"{delta:+.2f} vs. scale midpoint (5.0)"
        )

        fig_score = draw_distribution(
            df,
            "score",
            "#1CBCF5",
            bins=14
        )

        st.plotly_chart(
            fig_score,
            use_container_width=True,
            config={"displayModeBar": False},
            key="average_happiness_distribution"
        )


# -----------------------------------------------------------------------------
# KPI 3: Highest Happiness Score
# -----------------------------------------------------------------------------

with col3:
    with st.container(border=True):

        top_country = df.loc[
            df["score"].idxmax()
        ]

        st.metric(
            "Highest Happiness Score",
            f"{top_country['score']:.2f}",
            top_country["country"]
        )

        fig_top_score = draw_distribution(
            df,
            "score",
            "#1CBCF5",
            bins=14
        )

        st.plotly_chart(
            fig_top_score,
            use_container_width=True,
            config={"displayModeBar": False},
            key="highest_happiness_distribution"
        )


# -----------------------------------------------------------------------------
# KPI 4: Average GDP per Capita
# -----------------------------------------------------------------------------

with col4:
    with st.container(border=True):

        avg_gdp = df["gdp_per_capita"].mean()

        st.metric(
            "Average GDP per Capita",
            f"{avg_gdp:.3f}"
        )

        fig_gdp = draw_distribution(
            df,
            "gdp_per_capita",
            "#1CBCF5",
            bins=14
        )

        st.plotly_chart(
            fig_gdp,
            use_container_width=True,
            config={"displayModeBar": False},
            key="average_gdp_distribution"
        )

        st.markdown(
                    "<div style='height: 26px;'></div>",
                    unsafe_allow_html=True
                )


st.write("")
st.write("")
st.write("")

# -----------------------------------------------------------------------------
# Part II: What Drives Happiness
# -----------------------------------------------------------------------------

st.header("Part II: What Drives Happiness")

st.write(
    "**What factors are most strongly associated with happiness?** " \
    "Economic prosperity, social support, healthy life expectancy, "
    "and freedom to make life choices show stronger relationships with " \
    "happiness, while generosity and perceptions of corruption have " \
    "weaker associations. These relationships provide a starting point "
    "for understanding which factors are most closely connected to differences in happiness across countries."
)

st.write("")

BLUE = "#1CBCF5"


factor_cols = [
    "score", "gdp_per_capita", "social_support",
    "healthy_life_expectancy", "freedom", "generosity", "corruption"
]

corr = df[factor_cols].corr().reset_index().melt(id_vars="index")
corr.columns = ["Variable 1", "Variable 2", "Correlation"]

heatmap = alt.Chart(corr).mark_rect().encode(
    x=alt.X("Variable 1:N", title=None),
    y=alt.Y("Variable 2:N", title=None),
    color=alt.Color(
        "Correlation:Q",
        scale=alt.Scale(scheme="blues"),
        legend=alt.Legend(title="Correlation"),
    ),
    tooltip=[
        alt.Tooltip("Variable 1:N"),
        alt.Tooltip("Variable 2:N"),
        alt.Tooltip("Correlation:Q", format=".2f"),
    ],
).properties(height=400)

text = alt.Chart(corr).mark_text(baseline="middle").encode(
    x="Variable 1:N",
    y="Variable 2:N",
    text=alt.Text("Correlation:Q", format=".2f"),
    color=alt.condition(
        alt.datum.Correlation > 0.5, alt.value("white"), alt.value("black")
    ),
)

st.altair_chart(heatmap + text, use_container_width=True)

st.write(
    "GDP per capita, social support, and healthy life expectancy tend to show "
    "the strongest relationships with overall happiness score, while generosity "
    "and perceptions of corruption typically show weaker correlations."
)

BLUE = "#1CBCF5"  # matches the reference image's blue

st.subheader("GDP per Capita vs. Happiness Score")

left_col, right_col = st.columns([2, 1])

with left_col:
    scatter_fig = px.scatter(
        df,
        x="gdp_per_capita",
        y="score",
        hover_name="country",
        hover_data={"gdp_per_capita": ":.3f", "score": ":.2f"},
        trendline="ols",
        color_discrete_sequence=[BLUE],
        opacity=0.7,
    )
    scatter_fig.update_traces(marker=dict(size=9))
    scatter_fig.update_layout(
        xaxis_title="GDP per Capita",
        yaxis_title="Happiness Score",
        height=520,
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

with right_col:
    gdp_hist = px.histogram(
        df,
        x="gdp_per_capita",
        nbins=10,
        color_discrete_sequence=[BLUE],
    )
    gdp_hist.update_layout(
        title="GDP per Capita Distribution",
        xaxis_title="GDP per Capita (binned)",
        yaxis_title="Countries",
        height=250,
        margin=dict(t=40, b=30),
    )
    st.plotly_chart(gdp_hist, use_container_width=True)

    score_hist = px.histogram(
        df,
        x="score",
        nbins=10,
        color_discrete_sequence=[BLUE],
    )
    score_hist.update_layout(
        title="Happiness Score Distribution",
        xaxis_title="Score (binned)",
        yaxis_title="Countries",
        height=250,
        margin=dict(t=40, b=30),
    )
    st.plotly_chart(score_hist, use_container_width=True)


st.write(
    "GDP per capita shows a clear positive relationship with happiness, " \
    "although countries with similar levels of economic prosperity can " \
    "have noticeably different happiness scores. This suggests that economic" \
    "prosperity alone does not fully explain differences in national happiness."
)

st.write("")
st.write("")
st.write("")

# -----------------------------------------------------------------------------
# Part III: Overperformers & Underperformers
# -----------------------------------------------------------------------------


st.header("Part III: Overperformers & Underperformers")

st.write(
    "**GDP per capita** "
    "is strongly associated with happiness, but it does not fully explain differences between countries "
    "Using a simple linear regression, we can predict each country's expected happiness "
    "score based on its wealth alone — and then see which countries beat that expectation, "
    "and which fall short."
)

st.write("")

# --- Fit linear regression ---
x = df["gdp_per_capita"].to_numpy()
y = df["score"].to_numpy()

slope, intercept = np.polyfit(x, y, 1)
df["predicted_score"] = slope * df["gdp_per_capita"] + intercept
df["residual"] = df["score"] - df["predicted_score"]

std_dev = df["residual"].std()

def classify(residual):
    if residual > std_dev:
        return "Overperformer"
    elif residual < -std_dev:
        return "Underperformer"
    else:
        return "In Range"

df["status"] = df["residual"].apply(classify)

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)

overperformers = df[df["status"] == "Overperformer"]
underperformers = df[df["status"] == "Underperformer"]

with col1:
    st.metric("Overperformers", len(overperformers))
with col2:
    st.metric("Underperformers", len(underperformers))
with col3:
    biggest_over = overperformers.loc[overperformers["residual"].idxmax()]
    st.metric("Biggest Overperformer", biggest_over["country"], f"+{biggest_over['residual']:.2f}")
with col4:
    biggest_under = underperformers.loc[underperformers["residual"].idxmin()]
    st.metric(
    "Biggest Underperformer",
    biggest_under["country"],
    f"{biggest_under['residual']:.2f}"
)

st.write("")

# --- Color-coded scatter with trend line ---
BLUE = "#1CBCF5"
GREEN = "#2ECC71"
ORANGE = "#E67E22"

status_colors = alt.Scale(
    domain=["Overperformer", "In Range", "Underperformer"],
    range=[GREEN, BLUE, ORANGE],
)

scatter = alt.Chart(df).mark_circle(size=90, opacity=0.75).encode(
    x=alt.X("gdp_per_capita:Q", title="GDP per Capita"),
    y=alt.Y("score:Q", title="Happiness Score"),
    color=alt.Color("status:N", scale=status_colors, title="Status"),
    tooltip=[
        alt.Tooltip("country:N", title="Country"),
        alt.Tooltip("gdp_per_capita:Q", title="GDP per Capita", format=".3f"),
        alt.Tooltip("score:Q", title="Score", format=".2f"),
        alt.Tooltip("status:N", title="Status"),
    ],
)

trend_line = alt.Chart(df).mark_line(color="gray", strokeDash=[4, 4]).encode(
    x="gdp_per_capita:Q",
    y="predicted_score:Q",
)

st.altair_chart((scatter + trend_line).properties(height=500), use_container_width=True)

# --- Ranked tables ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Overperformers")
    top_over = overperformers.sort_values("residual", ascending=False).head(10)
    st.dataframe(
        top_over[["country", "score", "gdp_per_capita", "residual"]],
        hide_index=True,
    )

with col_right:
    st.subheader("Top 10 Underperformers")
    top_under = underperformers.sort_values("residual").head(10)
    st.dataframe(
        top_under[["country", "score", "gdp_per_capita", "residual"]],
        hide_index=True,
    )

st.write("")
st.write("")
st.write("")


# -----------------------------------------------------------------------------
# Part IV
# -----------------------------------------------------------------------------



st.header("Part IV: Explore Any Country")

st.write(
    "Select a country to see its happiness score, global rank, "
    "and how it scores across each of the six contributing factors relative to all 147 countries."
)

# -----------------------------------------------------------------------------
# Normalize factors to 0-1 scale
# -----------------------------------------------------------------------------

factor_list = [
    "social_support",
    "freedom",
    "healthy_life_expectancy",
    "gdp_per_capita",
    "generosity",
    "corruption",
]

for col in factor_list:
    min_val = df[col].min()
    max_val = df[col].max()

    df[f"{col}_norm"] = (
        (df[col] - min_val) /
        (max_val - min_val)
    )

# -----------------------------------------------------------------------------
# Country selector
# -----------------------------------------------------------------------------

country_list = sorted(df["country"].unique())

default_index = (
    country_list.index("Philippines")
    if "Philippines" in country_list
    else 0
)

selected_country = st.selectbox(
    "Select Country:",
    country_list,
    index=default_index
)

country_row = df[
    df["country"] == selected_country
].iloc[0]

# -----------------------------------------------------------------------------
# KPI Header
# -----------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Happiness Score",
        f"{country_row['score']:.2f}"
    )

with col2:
    st.metric(
        "Global Rank",
        f"#{int(country_row['rank'])}"
    )

# -----------------------------------------------------------------------------
# Factor Labels
# -----------------------------------------------------------------------------

factor_labels = {
    "social_support": "Social Support",
    "freedom": "Freedom",
    "healthy_life_expectancy": "Healthy Life Expectancy",
    "gdp_per_capita": "GDP",
    "generosity": "Generosity",
    "corruption": "Corruption",
}

# Create the sorting list separately
factor_list_labels = [
    factor_labels[f]
    for f in factor_list
]

# -----------------------------------------------------------------------------
# Factor Bar Chart
# -----------------------------------------------------------------------------

bar_data = pd.DataFrame({
    "Factor": [
        factor_labels[f]
        for f in factor_list
    ],

    "Normalized Value": [
        country_row[f"{f}_norm"]
        for f in factor_list
    ],

    "Raw Value": [
        country_row[f]
        for f in factor_list
    ],
})

BLUE = "#1CBCF5"

factor_bar = (
    alt.Chart(bar_data)
    .mark_bar(color=BLUE)
    .encode(
        y=alt.Y(
            "Factor:N",
            sort=factor_list_labels,
            title=None
        ),

        x=alt.X(
            "Normalized Value:Q",
            scale=alt.Scale(domain=[0, 1]),
            title="Min-max normalization (0-1)"
        ),

        tooltip=[
            alt.Tooltip(
                "Factor:N",
                title="Factor"
            ),

            alt.Tooltip(
                "Raw Value:Q",
                format=".3f",
                title="Raw Value"
            ),

            alt.Tooltip(
                "Normalized Value:Q",
                format=".2f",
                title="Relative Score"
            ),
        ],
    )
    .properties(
        height=280
    )
)

st.altair_chart(
    factor_bar,
    use_container_width=True
)

# -----------------------------------------------------------------------------
# World Map
# -----------------------------------------------------------------------------

st.subheader("Global Happiness Map")

world = alt.topo_feature(
    data.world_110m.url,
    "countries"
)

world_map = (
    alt.Chart(world)
    .mark_geoshape(
        stroke="white",
        strokeWidth=0.5
    )
    .encode(
        color=alt.Color(
            "score:Q",
            scale=alt.Scale(
                scheme="blues"
            ),
            title="Happiness Score"
        ),

        tooltip=[
            alt.Tooltip(
                "country:N",
                title="Country"
            ),

            alt.Tooltip(
                "score:Q",
                title="Happiness Score",
                format=".2f"
            ),
        ],
    )
    .transform_lookup(
        lookup="id",

        from_=alt.LookupData(
            df,
            "iso_numeric",
            [
                "country",
                "score"
            ]
        )
    )
    .project(
        "naturalEarth1"
    )
    .properties(
        width=900,
        height=450
    )
)

st.altair_chart(
    world_map,
    use_container_width=True
)