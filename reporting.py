import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.express as px

# =============================================================================
# SUMMARY & INSIGHTS FUNCTIONS
# =============================================================================
def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary DataFrame with key metrics:
      - Total Imports (Tons)
      - Total Records
      - Average Tons per Record
      - Top Reporter (by volume)
      - Top Partner (by volume)
      - Peak Year (by total volume)
      - Top Flow (by volume)
    """
    total_tons = df["Tons"].sum()
    total_records = df.shape[0]
    avg_tons = total_tons / total_records if total_records > 0 else 0

    # Top Reporter
    if "Reporter" in df.columns:
        reporter_agg = df.groupby("Reporter")["Tons"].sum().reset_index()
        if not reporter_agg.empty:
            top_reporter_row = reporter_agg.sort_values("Tons", ascending=False).iloc[0]
            top_reporter = f"{top_reporter_row['Reporter']} ({top_reporter_row['Tons']:,.2f} Tons)"
        else:
            top_reporter = "N/A"
    else:
        top_reporter = "N/A"

    # Top Partner
    if "Partner" in df.columns:
        partner_agg = df.groupby("Partner")["Tons"].sum().reset_index()
        if not partner_agg.empty:
            top_partner_row = partner_agg.sort_values("Tons", ascending=False).iloc[0]
            top_partner = f"{top_partner_row['Partner']} ({top_partner_row['Tons']:,.2f} Tons)"
        else:
            top_partner = "N/A"
    else:
        top_partner = "N/A"

    # Peak Year
    if "Year" in df.columns:
        year_agg = df.groupby("Year")["Tons"].sum().reset_index()
        if not year_agg.empty:
            peak_year_row = year_agg.sort_values("Tons", ascending=False).iloc[0]
            peak_year = f"{peak_year_row['Year']} ({peak_year_row['Tons']:,.2f} Tons)"
        else:
            peak_year = "N/A"
    else:
        peak_year = "N/A"
    
    # Top Flow
    if "Flow" in df.columns:
        flow_agg = df.groupby("Flow")["Tons"].sum().reset_index()
        if not flow_agg.empty:
            top_flow_row = flow_agg.sort_values("Tons", ascending=False).iloc[0]
            top_flow = f"{top_flow_row['Flow']} ({top_flow_row['Tons']:,.2f} Tons)"
        else:
            top_flow = "N/A"
    else:
        top_flow = "N/A"

    summary_data = {
        "Metric": [
            "Total Imports (Tons)",
            "Total Records",
            "Average Tons per Record",
            "Top Reporter",
            "Top Partner",
            "Peak Year",
            "Top Flow"
        ],
        "Value": [
            f"{total_tons:,.2f}",
            total_records,
            f"{avg_tons:,.2f}",
            top_reporter,
            top_partner,
            peak_year,
            top_flow
        ]
    }
    return pd.DataFrame(summary_data)

def generate_auto_insights(df: pd.DataFrame) -> str:
    """
    Generate a natural‑language summary of key insights from the data.
    """
    try:
        total_tons = df["Tons"].sum()
        total_records = df.shape[0]
        avg_tons = total_tons / total_records if total_records > 0 else 0

        insights = []
        insights.append(f"Total imports amount to {total_tons:,.2f} tons over {total_records} records, averaging {avg_tons:,.2f} tons per record.")
        if "Reporter" in df.columns:
            reporter_agg = df.groupby("Reporter")["Tons"].sum()
            top_reporter = reporter_agg.idxmax()
            insights.append(f"The top reporter is {top_reporter} with {reporter_agg.max():,.2f} tons.")
        if "Partner" in df.columns:
            partner_agg = df.groupby("Partner")["Tons"].sum()
            top_partner = partner_agg.idxmax()
            insights.append(f"The leading partner is {top_partner} with {partner_agg.max():,.2f} tons.")
        if "Year" in df.columns:
            year_agg = df.groupby("Year")["Tons"].sum()
            peak_year = year_agg.idxmax()
            insights.append(f"Peak year for imports is {peak_year} with {year_agg.max():,.2f} tons.")
        if "Flow" in df.columns:
            flow_agg = df.groupby("Flow")["Tons"].sum()
            top_flow = flow_agg.idxmax()
            insights.append(f"Most traded flow type is {top_flow} with {flow_agg.max():,.2f} tons.")
        return " ".join(insights)
    except Exception as e:
        return f"Insights not available due to error: {e}"

# =============================================================================
# EXPORT FUNCTIONS (CSV & Excel)
# =============================================================================
def export_to_csv(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to CSV.
    Optionally, prepend summary metrics and auto insights as commented header lines.
    """
    data_to_export = df[columns]
    csv_buffer = io.StringIO()
    if include_summary or include_insights:
        csv_buffer.write("# Auto‑Generated Report Summary\n")
        if include_summary:
            summary_df = generate_summary(df)
            for _, row in summary_df.iterrows():
                csv_buffer.write(f"# {row['Metric']}: {row['Value']}\n")
        if include_insights:
            csv_buffer.write(f"# Insights: {generate_auto_insights(df)}\n")
        csv_buffer.write("\n")
    data_to_export.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode("utf-8")

def export_to_excel(df: pd.DataFrame, columns: list, include_summary: bool, include_insights: bool) -> bytes:
    """
    Export selected columns to an Excel file with two sheets:
      - "Data": The main report data.
      - "Summary": Summary metrics and auto‑generated insights.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[columns].to_excel(writer, index=False, sheet_name="Data")
        if include_summary or include_insights:
            summary_df = generate_summary(df)
            insights_text = generate_auto_insights(df) if include_insights else ""
            insights_df = pd.DataFrame({"Auto Insights": [insights_text]})
            summary_combined = pd.concat([summary_df, insights_df], ignore_index=True)
            summary_combined.to_excel(writer, index=False, sheet_name="Summary")
    return output.getvalue()

# =============================================================================
# OVERALL DASHBOARD REPORT (INTERACTIVE)
# =============================================================================
def overall_dashboard_report(data: pd.DataFrame):
    st.title("📊 Overall Dashboard Summary Report")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return
    
    # Ensure "Tons" is numeric and create a Period column if not present.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    if "Period" not in data.columns:
        data["Period"] = data["Month"].astype(str) + "-" + data["Year"].astype(str)
    
    # Display key metrics
    summary_df = generate_summary(data)
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    metrics = summary_df["Metric"].tolist()
    values = summary_df["Value"].tolist()
    for i in range(len(metrics)):
        st.metric(metrics[i], values[i])
    
    st.markdown("---")
    st.subheader("Interactive Charts")
    tabs = st.tabs(["Market Trend", "Reporter Analysis", "Partner Analysis", "Yearly Trend"])
    
    # Market Trend Tab
    with tabs[0]:
        st.markdown("#### Overall Market Volume Trend")
        market_trend = data.groupby("Period")["Tons"].sum().reset_index()
        fig_market = px.line(market_trend, x="Period", y="Tons", title="Market Volume Trend", markers=True, template="plotly_white")
        st.plotly_chart(fig_market, use_container_width=True)
    
    # Reporter Analysis Tab
    with tabs[1]:
        if "Reporter" in data.columns:
            st.markdown("#### Top Reporters by Volume")
            reporter_summary = data.groupby("Reporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
            fig_reporter = px.bar(reporter_summary.head(5), x="Reporter", y="Tons", title="Top 5 Reporters", text_auto=True, template="plotly_white")
            st.plotly_chart(fig_reporter, use_container_width=True)
        else:
            st.info("Reporter data not available.")
    
    # Partner Analysis Tab
    with tabs[2]:
        if "Partner" in data.columns:
            st.markdown("#### Top Partners by Volume")
            partner_summary = data.groupby("Partner")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
            fig_partner = px.bar(partner_summary.head(5), x="Partner", y="Tons", title="Top 5 Partners", text_auto=True, template="plotly_white")
            st.plotly_chart(fig_partner, use_container_width=True)
        else:
            st.info("Partner data not available.")
    
    # Yearly Trend Tab
    with tabs[3]:
        if "Year" in data.columns:
            st.markdown("#### Yearly Trade Volume Trend")
            yearly_trend = data.groupby("Year")["Tons"].sum().reset_index().sort_values("Year")
            fig_year = px.bar(yearly_trend, x="Year", y="Tons", title="Yearly Trade Volume", text_auto=True, template="plotly_white")
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("Year data not available.")
    
    st.markdown("---")
    st.subheader("Overall Report Summary")
    st.dataframe(summary_df)
    st.markdown(f"**Auto Insights:** {generate_auto_insights(data)}")
    st.success("✅ Overall Dashboard Summary Report Loaded Successfully!")

# =============================================================================
# MAIN REPORTING & EXPORT FUNCTION
# =============================================================================
def reporting_data_exports(data: pd.DataFrame):
    st.title("📄 Reporting & Data Exports Dashboard")
    
    if data is None or data.empty:
        st.warning("⚠️ No data available. Please upload a dataset first.")
        return

    all_columns = list(data.columns)
    selected_columns = st.multiselect("Select Columns to Include in Report:", options=all_columns, default=all_columns)
    include_summary = st.checkbox("Include Summary Metrics", value=True)
    include_insights = st.checkbox("Include Auto Insights", value=True)
    
    st.markdown("### Report Preview")
    preview_df = data[selected_columns].copy()
    st.dataframe(preview_df.head(50))
    
    st.markdown("### Export Options")
    report_format = st.radio("Report Format:", ("CSV", "Excel"))
    
    if report_format == "CSV":
        csv_data = export_to_csv(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download CSV Report", csv_data, "report.csv", "text/csv")
    elif report_format == "Excel":
        excel_data = export_to_excel(data, selected_columns, include_summary, include_insights)
        st.download_button("📥 Download Excel Report", excel_data, "report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.success("✅ Report Generation Ready!")

# =============================================================================
# OVERALL REPORTING DASHBOARD ENTRY-POINT
# =============================================================================
def overall_reporting_dashboard(data: pd.DataFrame):
    st.title("📝 Reporting Dashboard")
    st.markdown("Select a view from the tabs below to explore interactive reports or export data.")
    
    tabs = st.tabs(["Interactive Report", "Export & Download"])
    with tabs[0]:
        overall_dashboard_report(data)
    with tabs[1]:
        reporting_data_exports(data)
    
    st.success("✅ Reporting Dashboard loaded successfully!")
