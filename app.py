import streamlit as st
import pandas as pd
from data_processing import (
    load_file,
    getMissionCountByCompany,
    getSuccessRate,
    getTopCompaniesByMissionCount,
    getTopCompaniesByMissionCountInRange,
    getMissionsByDateRange,
    getMissionStatusCount,
    getMissionsByYear,
    getAverageMissionsPerYear,
    getSummaryStatistics
)
import plotly.express as px
import plotly.graph_objects as go

# page config
st.set_page_config(
    page_title="Space Missions Dashboard",
    layout="wide"
)


# load data
@st.cache_data
def load_data():
    df = load_file('space_missions.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    return df


@st.cache_data
def load_summary():
    return getSummaryStatistics()


try:
    df = load_data()
    summary_stats = load_summary()

    st.title("Space Missions Dashboard")
    st.markdown("---")

    # Filters
    st.sidebar.header("Filters")

    # reset button
    if st.sidebar.button("Reset Filters"):
        st.session_state["year_slider"] = (int(df['Year'].min()), int(df['Year'].max()))
        st.session_state["selected_companies"] = []
        st.session_state["selected_statuses"] = []
        st.rerun()

    # Derive year bounds from data
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())

    # year range slider
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        key="year_slider"
    )
    start_year, end_year = year_range

    # company filter
    all_companies = sorted(df['Company'].unique().tolist())
    selected_companies = st.sidebar.multiselect(
        "Company",
        options=all_companies,
        default=[],
        key="selected_companies"
    )

    # mission status filter
    all_statuses = sorted(df['MissionStatus'].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Mission Status",
        options=all_statuses,
        default=[],
        key="selected_statuses"
    )

    # filter directly on the Date column to avoid mission-name collision
    start_date_str = f"{start_year}-01-01"
    end_date_str = f"{end_year}-12-31"

    # apply all filters to the main dataframe
    filtered_df = df[
        (df['Date'] >= pd.Timestamp(start_date_str)) &
        (df['Date'] <= pd.Timestamp(end_date_str))
    ].copy()

    if selected_companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]

    if selected_statuses:
        filtered_df = filtered_df[filtered_df['MissionStatus'].isin(selected_statuses)]

    # Summary statistics — always show full dataset stats
    st.header("Summary Statistics")
    st.caption("Statistics represent the entire dataset, unaffected by filters.")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Missions", f"{summary_stats['total_missions']:,}")

    with col2:
        st.metric("Overall Success Rate", f"{summary_stats['overall_success_rate']:.1f}%")

    with col3:
        st.metric("Total Companies", summary_stats['total_companies'])

    with col4:
        st.metric("Avg Missions / Year", f"{summary_stats['avg_missions_per_year']:,}")

    with col5:
        # help tooltip as overflow safety net
        rocket_name = summary_stats['most_used_rocket']
        st.metric("Most Used Rocket", rocket_name, help=rocket_name)

    with col6:
        yr_min, yr_max = summary_stats['year_range']
        st.metric("Year Range", f"{yr_min}–{yr_max}")

    # Top 10 Companies by Mission Count
    st.subheader("Top 10 Companies by Mission Count")
    top_companies = getTopCompaniesByMissionCount(10)
    top_companies_data = []
    for company, _ in top_companies:
        mission_count = getMissionCountByCompany(company)
        sr = getSuccessRate(company)
        top_companies_data.append({
            'Company': company,
            'Total Missions': mission_count,
            'Success Rate (%)': sr
        })

    top_companies_df = pd.DataFrame(top_companies_data)
    st.dataframe(top_companies_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visualizations
    st.header("Visualizations")

    # detect company selection mode
    num_companies = len(selected_companies)
    single_company = num_companies == 1
    multi_company = num_companies > 1
    company_name = selected_companies[0] if single_company else None

    # dynamic status label for headers
    status_label = f" [{', '.join(selected_statuses)}]" if selected_statuses else ""

    # Visualization 1 - Success Rate Over Time
    if single_company:
        viz1_title = f"1. {company_name} – Mission Success Rate Over Time{status_label}"
    elif multi_company:
        viz1_title = f"1. Mission Success Rate Over Time – Selected Companies{status_label}"
    else:
        viz1_title = f"1. Mission Success Rate Over Time{status_label}"
    st.subheader(viz1_title)

    if multi_company:
        # one line per selected company
        fig1 = go.Figure()
        color_sequence = px.colors.qualitative.Plotly
        for i, comp in enumerate(selected_companies):
            comp_df = filtered_df[filtered_df['Company'] == comp]
            rows = []
            for yr in sorted(comp_df['Year'].unique()):
                yr_df = comp_df[comp_df['Year'] == yr]
                total = len(yr_df)
                successes = (yr_df['MissionStatus'] == 'Success').sum()
                rate = round((successes / total * 100) if total > 0 else 0, 2)
                rows.append({'Year': yr, 'Success Rate (%)': rate})
            comp_success = pd.DataFrame(rows)
            color = color_sequence[i % len(color_sequence)]
            fig1.add_trace(go.Scatter(
                x=comp_success['Year'] if not comp_success.empty else [],
                y=comp_success['Success Rate (%)'] if not comp_success.empty else [],
                mode='lines+markers',
                line=dict(color=color, width=2),
                name=comp,
                hovertemplate='%{y:.1f}%<extra>' + comp + '</extra>'
            ))
        fig1.update_layout(
            hovermode='x unified',
            yaxis=dict(range=[0, 100], title='Success Rate (%)'),
            xaxis=dict(range=[start_year - 0.5, end_year + 0.5], dtick=1, tickformat='d')
        )
    else:
        # single company or no filter — one aggregated line
        yearly_success_rows = []
        for yr in sorted(filtered_df['Year'].unique()):
            yr_df = filtered_df[filtered_df['Year'] == yr]
            total = len(yr_df)
            successes = (yr_df['MissionStatus'] == 'Success').sum()
            rate = (successes / total * 100) if total > 0 else 0
            yearly_success_rows.append({'Year': yr, 'Success Rate (%)': round(rate, 2)})

        yearly_success = pd.DataFrame(yearly_success_rows)
        chart_title_1 = (
            f'Success Rate Trend by Year – {company_name}{status_label}'
            if single_company
            else f'Success Rate Trend by Year{status_label}'
        )
        fig1 = px.line(yearly_success, x='Year', y='Success Rate (%)', markers=True, title=chart_title_1)
        fig1.update_traces(line_color='#2ecc71', line_width=3)
        fig1.update_layout(
            hovermode='x unified',
            yaxis=dict(range=[0, 100]),
            xaxis=dict(range=[start_year - 0.5, end_year + 0.5], dtick=1, tickformat='d')
        )

    st.plotly_chart(fig1, use_container_width=True)

    # Visualization 2 - Missions Over Time
    color_sequence = px.colors.qualitative.Plotly
    fig2 = go.Figure()

    if single_company:
        if selected_statuses:
            viz2_title = f"2. {company_name} – Missions Over Time{status_label}"
        else:
            viz2_title = f"2. {company_name} – Total vs Successful Missions Over Time"
        st.subheader(viz2_title)

        co_data = (
            filtered_df
            .groupby('Year')
            .agg(
                Total_Missions=('Mission', 'count'),
                Successful_Missions=('MissionStatus', lambda x: (x == 'Success').sum())
            )
            .reset_index()
            .sort_values('Year')
        )

        color = color_sequence[0]
        fill_color = color.replace('rgb(', 'rgba(').replace(')', ', 0.25)') if color.startswith('rgb(') else color

        if not selected_statuses:
            fig2.add_trace(go.Scatter(
                x=co_data['Year'], y=co_data['Successful_Missions'],
                mode='none', fill='tozeroy', fillcolor=fill_color,
                name='Successful Missions',
                hovertemplate='%{y} successful<extra>Successful</extra>'
            ))

        fig2.add_trace(go.Scatter(
            x=co_data['Year'], y=co_data['Total_Missions'],
            mode='lines+markers', line=dict(color=color, width=2),
            name='Missions' if selected_statuses else 'Total Missions',
            hovertemplate='%{y} total<extra>Total</extra>'
        ))

        chart_title_2 = (
            f'Missions Over Time – {company_name}{status_label}'
            if selected_statuses
            else f'Total vs Successful Missions Over Time – {company_name}'
        )

    elif multi_company:
        # one line per selected company — no top-N slider needed
        viz2_title = f"2. Total Missions Over Time – Selected Companies{status_label}"
        st.subheader(viz2_title)

        for i, comp in enumerate(selected_companies):
            co_data = (
                filtered_df[filtered_df['Company'] == comp]
                .groupby('Year')
                .agg(Total_Missions=('Mission', 'count'))
                .reset_index()
                .sort_values('Year')
            )
            color = color_sequence[i % len(color_sequence)]
            fig2.add_trace(go.Scatter(
                x=co_data['Year'] if not co_data.empty else [],
                y=co_data['Total_Missions'] if not co_data.empty else [],
                mode='lines+markers', line=dict(color=color, width=2),
                name=comp,
                hovertemplate='%{y} missions<extra>' + comp + '</extra>'
            ))

    else:
        # no company filter — show top N companies from the year range
        viz2_title = f"2. Total Missions by Company Over Time{status_label}"
        st.subheader(viz2_title)

        top_n = st.slider("Number of top companies to display", 3, 10, 5)
        top_comp_names = [
            comp[0] for comp in getTopCompaniesByMissionCountInRange(top_n, start_date_str, end_date_str)
        ]

        company_yearly = (
            filtered_df[filtered_df['Company'].isin(top_comp_names)]
            .groupby(['Year', 'Company'])
            .agg(Total_Missions=('Mission', 'count'))
            .reset_index()
        )

        for i, comp in enumerate(top_comp_names):
            color = color_sequence[i % len(color_sequence)]
            co_data = company_yearly[company_yearly['Company'] == comp].sort_values('Year')
            fig2.add_trace(go.Scatter(
                x=co_data['Year'], y=co_data['Total_Missions'],
                mode='lines+markers', line=dict(color=color, width=2),
                name=comp,
                hovertemplate='%{y} missions<extra>' + comp + '</extra>'
            ))

        chart_title_2 = f'Total Missions by Top {top_n} Companies Over Time{status_label}'

    fig2.update_layout(
        xaxis=dict(
            title='Year',
            range=[start_year - 0.5, end_year + 0.5],
            dtick=1,
            tickformat='d'
        ),
        yaxis=dict(title='Missions'),
        hovermode='x unified',
        legend=dict(groupclick='togglegroup')
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Visualization 3 - Mission Status Distribution
    st.subheader(f"3. Mission Status Distribution{status_label}")

    filters_active = bool(selected_companies or selected_statuses or start_year != min_year or end_year != max_year)

    if filters_active:
        status_series = filtered_df['MissionStatus'].value_counts()
        status_counts = status_series.reset_index()
        status_counts.columns = ['Status', 'Count']
    else:
        all_status_counts = getMissionStatusCount()
        status_counts = pd.DataFrame(
            list(all_status_counts.items()), columns=['Status', 'Count']
        )

    fig3 = px.bar(
        status_counts,
        x='Status',
        y='Count',
        color='Status',
        color_discrete_map={
            'Success': 'green',
            'Failure': 'red',
            'Partial Failure': 'yellow',
            'Prelaunch Failure': 'gray'
        }
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # Data Table
    st.header("Data Table")

    search_term = st.text_input("🔍 Search in table", "")

    display_df = filtered_df.copy()
    if search_term:
        display_df = display_df[
            display_df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
        ]

    st.write(f"Showing {len(display_df)} missions")

    display_table = display_df[['Date', 'Company', 'Mission', 'Rocket', 'MissionStatus']].sort_values('Date', ascending=False).copy()
    display_table['Date'] = display_table['Date'].dt.date

    st.dataframe(
        display_table,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="space_missions_filtered.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Quick Loopup
    st.header("Quick Lookup")
    st.caption("Interactive queries using the full dataset.")

    ql_col1, ql_col2 = st.columns(2)

    # Tool 1: Missions by year
    with ql_col1:
        st.subheader("Missions by Year")
        lookup_year = st.number_input(
            "Select a year",
            min_value=min_year,
            max_value=max_year,
            value=max_year,
            step=1,
            key="lookup_year"
        )
        try:
            count = getMissionsByYear(int(lookup_year))
            st.metric(f"Total missions in {int(lookup_year)}", f"{count:,}")
        except ValueError as e:
            st.warning(str(e))

    # Tool 2: Avg missions in year range
    with ql_col2:
        st.subheader("Average Missions per Year")
        avg_col_a, avg_col_b = st.columns(2)
        with avg_col_a:
            avg_start = st.number_input(
                "From year",
                min_value=min_year,
                max_value=max_year,
                value=min_year,
                step=1,
                key="avg_start"
            )
        with avg_col_b:
            avg_end = st.number_input(
                "To year",
                min_value=min_year,
                max_value=max_year,
                value=max_year,
                step=1,
                key="avg_end"
            )
        try:
            avg = getAverageMissionsPerYear(int(avg_start), int(avg_end))
            st.metric(f"Avg missions/year ({int(avg_start)}–{int(avg_end)})", f"{avg:,}")
        except ValueError as e:
            st.warning(str(e))

    # Tool 3: Missions in Custom Date Range (getMissionsByDateRange)
    st.subheader("Missions in Custom Date Range")
    dr_col1, dr_col2 = st.columns(2)
    with dr_col1:
        range_start = st.date_input(
            "Start date",
            value=pd.Timestamp(f"{min_year}-01-01"),
            min_value=pd.Timestamp(f"{min_year}-01-01"),
            max_value=pd.Timestamp(f"{max_year}-12-31"),
            key="range_start"
        )
    with dr_col2:
        range_end = st.date_input(
            "End date",
            value=pd.Timestamp(f"{max_year}-12-31"),
            min_value=pd.Timestamp(f"{min_year}-01-01"),
            max_value=pd.Timestamp(f"{max_year}-12-31"),
            key="range_end"
        )

    if st.button("Find Missions"):
        try:
            missions = getMissionsByDateRange(str(range_start), str(range_end))
            st.success(f"Found **{len(missions):,}** missions between {range_start} and {range_end}.")
            with st.expander(f"View all {len(missions):,} missions", expanded=len(missions) <= 50):
                range_df = df[
                    (df['Date'] >= pd.Timestamp(str(range_start))) &
                    (df['Date'] <= pd.Timestamp(str(range_end)))
                ][['Date', 'Company', 'Mission', 'Rocket', 'MissionStatus']].copy()
                range_df['Date'] = range_df['Date'].dt.date
                st.dataframe(range_df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
        except ValueError as e:
            st.warning(str(e))

except FileNotFoundError:
    st.error("❌ Error: space_missions.csv file not found. Please ensure the file is in the same directory as this app.")
except Exception as e:
    st.error(f"❌ An error occurred: {e}")