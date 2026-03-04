import io
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Excel Dashboard Builder", layout="wide")


@dataclass
class ColumnProfile:
    numeric: List[str]
    categorical: List[str]
    datetime: List[str]
    boolean: List[str]
    id_like: List[str]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Best-effort type inference for mixed Excel inputs."""
    df = df.copy()

    for col in df.columns:
        series = df[col]

        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_datetime64_any_dtype(series):
            continue

        if series.dtype == "object":
            sample = series.dropna().astype(str).head(50)
            if not sample.empty:
                date_hits = sample.str.contains(r"[-/]|:|T", regex=True).mean()
                if date_hits > 0.4:
                    datetime_series = pd.to_datetime(series, errors="coerce")
                    if datetime_series.notna().mean() > 0.6:
                        df[col] = datetime_series
                        continue

        if series.dtype == "object":
            cleaned = (
                series.astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.strip()
            )
            numeric_series = pd.to_numeric(cleaned, errors="coerce")
            if numeric_series.notna().mean() > 0.8:
                df[col] = numeric_series
                continue

        if series.dtype == "object":
            lowered = series.astype(str).str.strip().str.lower()
            bool_map = {
                "true": True,
                "false": False,
                "yes": True,
                "no": False,
                "y": True,
                "n": False,
                "1": True,
                "0": False,
            }
            mapped = lowered.map(bool_map)
            if mapped.notna().mean() > 0.9:
                df[col] = mapped.astype("boolean")

    return df


def profile_columns(df: pd.DataFrame) -> ColumnProfile:
    numeric = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    boolean = [
        col
        for col in df.columns
        if pd.api.types.is_bool_dtype(df[col]) or str(df[col].dtype) == "boolean"
    ]

    categorical: List[str] = []
    id_like: List[str] = []

    for col in df.columns:
        if col in numeric or col in datetime_cols or col in boolean:
            continue

        distinct = df[col].nunique(dropna=True)
        uniqueness_ratio = distinct / max(len(df), 1)

        if uniqueness_ratio > 0.9 and distinct > 20:
            id_like.append(col)
        else:
            categorical.append(col)

    return ColumnProfile(
        numeric=numeric,
        categorical=categorical,
        datetime=datetime_cols,
        boolean=boolean,
        id_like=id_like,
    )


def apply_filters(df: pd.DataFrame, profile: ColumnProfile) -> pd.DataFrame:
    st.sidebar.subheader("Filters")
    filtered = df.copy()

    for col in profile.datetime:
        values = filtered[col].dropna()
        if values.empty:
            continue

        min_date = values.min().date()
        max_date = values.max().date()
        selected = st.sidebar.date_input(
            f"{col} range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if isinstance(selected, tuple) and len(selected) == 2:
            start, end = selected
        else:
            start, end = min_date, max_date

        filtered = filtered[(filtered[col].dt.date >= start) & (filtered[col].dt.date <= end)]

    for col in profile.categorical + profile.boolean:
        options = filtered[col].dropna().unique().tolist()
        if 1 < len(options) <= 50:
            selected_options = st.sidebar.multiselect(
                col,
                options=sorted(options),
                default=sorted(options),
            )
            filtered = filtered[filtered[col].isin(selected_options)]

    return filtered


def default_kpis(df: pd.DataFrame, profile: ColumnProfile) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", f"{df.shape[1]:,}")
    col3.metric("Numeric columns", f"{len(profile.numeric):,}")
    col4.metric("Categorical columns", f"{len(profile.categorical):,}")


def auto_dashboard(df: pd.DataFrame, profile: ColumnProfile) -> None:
    st.subheader("Auto Dashboard")

    if profile.datetime and profile.numeric:
        date_col = profile.datetime[0]
        value_col = profile.numeric[0]
        grouped = df.groupby(pd.Grouper(key=date_col, freq="ME"))[value_col].sum().reset_index()
        fig = px.line(grouped, x=date_col, y=value_col, title=f"Monthly {value_col} over time")
        st.plotly_chart(fig, use_container_width=True)

    if profile.categorical and profile.numeric:
        category_col = profile.categorical[0]
        value_col = profile.numeric[0]
        grouped = (
            df.groupby(category_col, dropna=False)[value_col]
            .sum()
            .reset_index()
            .sort_values(value_col, ascending=False)
            .head(15)
        )
        fig = px.bar(grouped, x=category_col, y=value_col, title=f"Top {category_col} by {value_col}")
        st.plotly_chart(fig, use_container_width=True)

    if profile.numeric:
        value_col = profile.numeric[0]
        fig = px.histogram(df, x=value_col, nbins=30, title=f"Distribution of {value_col}")
        st.plotly_chart(fig, use_container_width=True)


def custom_chart_builder(df: pd.DataFrame, profile: ColumnProfile) -> None:
    st.subheader("Custom Chart Builder")
    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Histogram", "Box"])

    all_cols = df.columns.tolist()
    if not all_cols:
        st.warning("No columns available for charting.")
        return

    x_axis = st.selectbox("X-axis", all_cols)
    y_candidates = profile.numeric if profile.numeric else all_cols
    y_axis = st.selectbox("Y-axis", y_candidates)
    color = st.selectbox("Color (optional)", ["(none)"] + all_cols)
    color = None if color == "(none)" else color

    if st.button("Generate chart"):
        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, color=color)
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, color=color)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color)
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=x_axis, color=color)
        else:
            fig = px.box(df, x=x_axis, y=y_axis, color=color)

        st.plotly_chart(fig, use_container_width=True)


@st.cache_data(show_spinner=False)
def load_workbook(file_bytes: bytes) -> Dict[str, pd.DataFrame]:
    workbook = pd.ExcelFile(io.BytesIO(file_bytes))
    sheets: Dict[str, pd.DataFrame] = {}

    for sheet_name in workbook.sheet_names:
        raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
        normalized = normalize_columns(raw)
        typed = coerce_types(normalized)
        sheets[sheet_name] = typed

    return sheets


st.title("📊 Excel Dashboard Builder")
st.caption("Upload Excel files with varying columns; auto-generate dashboards + custom charts.")

uploads = st.file_uploader(
    "Upload one or more Excel files",
    type=["xlsx", "xlsm", "xls"],
    accept_multiple_files=True,
)

if not uploads:
    st.info("Upload at least one Excel file to begin.")
    st.stop()

all_data: Dict[str, Dict[str, pd.DataFrame]] = {}
for uploaded_file in uploads:
    all_data[uploaded_file.name] = load_workbook(uploaded_file.getvalue())

selected_file = st.selectbox("Choose file", list(all_data.keys()))
selected_sheet = st.selectbox("Choose sheet", list(all_data[selected_file].keys()))

source_df = all_data[selected_file][selected_sheet]
profile = profile_columns(source_df)

st.write("### Preview")
st.dataframe(source_df.head(200), use_container_width=True)

filtered_df = apply_filters(source_df, profile)
st.write(f"Filtered rows: **{len(filtered_df):,}** / {len(source_df):,}")

default_kpis(filtered_df, profile)
auto_dashboard(filtered_df, profile)
custom_chart_builder(filtered_df, profile)

with st.expander("Column type summary"):
    st.json(
        {
            "numeric": profile.numeric,
            "categorical": profile.categorical,
            "datetime": profile.datetime,
            "boolean": profile.boolean,
            "id_like": profile.id_like,
        }
    )
