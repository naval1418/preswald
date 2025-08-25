from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px
import pandas as pd
import numpy as np

# 1) Load via preswald.toml source
connect()
df = get_df("sample_csv")  # matches [data.sample_csv] in preswald.toml

# Optional cleanup
if "year" in df.columns:
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

text("# Biogeographical Analysis of Callitrichidae Distribution Patterns")

# ===== Simple controls (no multiselect) =====
# Filter by year range if present
if "year" in df.columns and df["year"].notna().any():
    yr_min = int(np.nanmin(df["year"]))
    yr_max = int(np.nanmax(df["year"]))
    yr_range = slider("Year range", min_val=yr_min, max_val=yr_max, default=(yr_min, yr_max))
else:
    yr_range = None

# Apply filters (year only)
df_filt = df.copy()
if yr_range and "year" in df_filt.columns:
    df_filt = df_filt[(df_filt["year"] >= yr_range[0]) & (df_filt["year"] <= yr_range[1])]

# Quick peek
table(df_filt.head(25), title="Preview (first 25 rows)")

# ===== Figure 1: Geographic Scatter =====
text("## Spatial Distribution Analysis")
text("Figure 1 illustrates the geographical distribution of Callitrichidae specimens across their native range.")
if {"decimalLatitude","decimalLongitude"}.issubset(df_filt.columns):
    fig = px.scatter_geo(
        df_filt,
        lat="decimalLatitude",
        lon="decimalLongitude",
        hover_name="speciesQueried" if "speciesQueried" in df_filt.columns else None,
        color="country" if "country" in df_filt.columns else None,
        title="Geographical Distribution of Callitrichidae Specimens",
        projection="natural earth",
    )
    plotly(fig)
else:
    text("⚠️ Columns 'decimalLatitude' and 'decimalLongitude' not found.")

# ===== Figure 2: Density (token-free) =====
text("## Population Density Assessment")
text("Figure 2 presents a density estimation of observations to highlight population concentration.")
if {"decimalLatitude","decimalLongitude"}.issubset(df_filt.columns):
    dens = px.density_contour(
        df_filt, x="decimalLongitude", y="decimalLatitude",
        title="Spatial Density Estimation of Observations",
    )
    plotly(dens)
else:
    text("⚠️ Need 'decimalLatitude' and 'decimalLongitude' for density plot.")

# ===== Figure 3: Species Richness by Country =====
text("## Species Richness Evaluation")
text("Figure 3 quantifies taxonomic diversity across political boundaries.")
if {"country","speciesQueried"}.issubset(df_filt.columns):
    richness = (
        df_filt.groupby("country")["speciesQueried"]
        .nunique()
        .reset_index(name="richness")
        .sort_values("richness", ascending=False)
    )
    richness_plot = px.bar(richness, x="country", y="richness",
                           title="Callitrichidae Species Richness by Geographic Region")
    plotly(richness_plot)
else:
    text("⚠️ Need 'country' and 'speciesQueried' columns for richness chart.")

# ===== Figure 4: Hierarchical Treemap =====
text("## Taxonomic Distribution by Geographic Region")
text("Figure 4 shows hierarchical relationships between geography and taxonomy.")
if {"country","speciesQueried"}.issubset(df_filt.columns):
    df_treemap = df_filt.groupby(["country", "speciesQueried"]).size().reset_index(name="count")
    treemap_plot = px.treemap(
        df_treemap, path=["country","speciesQueried"], values="count", color="count",
        title="Taxonomic and Geographic Distribution"
    )
    plotly(treemap_plot)
else:
    text("⚠️ Need 'country' and 'speciesQueried' for treemap.")

# ===== Figure 5: Life Stage over Time =====
text("## Ontogenetic Temporal Distribution")
text("Figure 5 examines temporal distribution across life stages.")
if {"year","lifeStage"}.issubset(df_filt.columns):
    life_stage_trend = df_filt[df_filt["lifeStage"].notna() & (df_filt["lifeStage"].str.lower() != "unknown")]
    life_stage_plot_data = life_stage_trend.groupby(["year","lifeStage"]).size().reset_index(name="count")
    life_stage_plot = px.line(
        life_stage_plot_data, x="year", y="count", color="lifeStage",
        title="Ontogenetic Distribution of Observations: Temporal Analysis"
    )
    plotly(life_stage_plot)
else:
    text("⚠️ Need 'year' and 'lifeStage' columns for the temporal analysis.")

