import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data_cleaning import load_and_clean_data
import seaborn as sns

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


# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------

st.title("World Happiness Report 2026 🌍")

st.write(
    "An exploration of what drives happiness across 147 countries, "
    "based on the Gallup World Poll (2023–2025 averages)."
)

st.divider()


# -----------------------------------------------------------------------------
# Part I: Overview
# -----------------------------------------------------------------------------

st.header("Part I: Overview")


# -----------------------------------------------------------------------------
# Sparkline / Distribution Chart
# -----------------------------------------------------------------------------

def draw_sparkline(data, color):
    fig, ax = plt.subplots(figsize=(2, 0.6))

    ax.hist(
        data,
        bins=15,
        color=color,
        alpha=0.4
    )

    ax.axis("off")
    fig.patch.set_alpha(0)

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

        st.pyplot(
            draw_sparkline(
                df["score"],
                "green"
            ),
            use_container_width=False
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
            "Highest Score",
            f"{top_country['score']:.2f}",
            top_country["country"]
        )

        st.pyplot(
            draw_sparkline(
                df["score"],
                "green"
            ),
            use_container_width=False
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

        st.pyplot(
            draw_sparkline(
                df["gdp_per_capita"],
                "steelblue"
            ),
            use_container_width=False
        )

        st.markdown(
            "<div style='height: 28px;'></div>",
            unsafe_allow_html=True
        )



# -----------------------------------------------------------------------------
# Part II: What Drives Happiness
# -----------------------------------------------------------------------------

st.header("Part II: What Drives Happiness")

st.write(
    "Which factors are most closely tied to a country's happiness score? "
    "The heatmap below shows how strongly each factor correlates with the overall score — "
    "values closer to 1 indicate a stronger positive relationship."
)

factor_cols = [
    "score", "gdp_per_capita", "social_support",
    "healthy_life_expectancy", "freedom", "generosity", "corruption"
]

corr = df[factor_cols].corr()

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(corr, annot=True, cmap="Blues", fmt=".2f", ax=ax)
st.pyplot(fig)

st.write(
    "GDP per capita, social support, and healthy life expectancy tend to show "
    "the strongest relationships with overall happiness score, while generosity "
    "and perceptions of corruption typically show weaker correlations."
)

st.subheader("GDP per Capita vs. Happiness Score")

fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.scatter(df["gdp_per_capita"], df["score"], alpha=0.6, color="steelblue")

# simple linear trend line
import numpy as np
z = np.polyfit(df["gdp_per_capita"], df["score"], 1)
trend = np.poly1d(z)
x_range = np.linspace(df["gdp_per_capita"].min(), df["gdp_per_capita"].max(), 100)
ax2.plot(x_range, trend(x_range), color="red", linewidth=2, label="Trend line")

ax2.set_xlabel("GDP per Capita")
ax2.set_ylabel("Happiness Score")
ax2.legend()
st.pyplot(fig2)

st.write(
    "While wealth is clearly linked to happiness, the relationship isn't perfect — "
    "some countries score higher or lower than their GDP alone would predict. "
    "We'll explore exactly which countries in Part III."
)