import streamlit as st
import pandas as pd
import altair as alt
from pycountry_convert import country_alpha2_to_continent_code

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/preprocessed_data.csv', parse_dates=['date', 'date_day'])
    
    # Add continent mapping
    def get_continent(country_code):
        try:
            continent_code = country_alpha2_to_continent_code(country_code)
            continent_mapping = {
                'AF': 'Africa',
                'AS': 'Asia',
                'EU': 'Europe',
                'NA': 'North America',
                'SA': 'South America',
                'OC': 'Oceania',
                'AN': 'Antarctica'
            }
            return continent_mapping.get(continent_code, 'Unknown')
        except:
            return 'Unknown'
    
    df['continent'] = df['country'].apply(get_continent)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_continents = st.sidebar.multiselect(
    "Select continents",
    df['continent'].unique(),
    default='Europe'
)
selected_devices = st.sidebar.multiselect(
    "Select devices",
    df['device'].unique(),
    default=df['device'].unique()
)
date_range = st.sidebar.date_input(
    "Date range", 
    [df['date_day'].min(), df['date_day'].max()],
    min_value=df['date_day'].min(),
    max_value=df['date_day'].max()
)

# Convert date_range to datetime
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1]) if len(date_range) > 1 else start_date

# Filter data
filtered_df = df[
    (df['continent'].isin(selected_continents)) &
    (df['device'].isin(selected_devices)) &
    (df['date_day'] >= start_date) &
    (df['date_day'] <= end_date)
]

# Main dashboard
st.title("Google Merchandise Shop Analytics")
st.markdown("### Interactive Performance Report")

# Key Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${filtered_df[filtered_df['type'] == 'purchase']['price_in_usd'].sum():,.0f}")
with col2:
    st.metric("Avg Order Value", f"${filtered_df[filtered_df['type'] == 'purchase']['price_in_usd'].mean():.1f}")
with col3:
    st.metric("Unique Users", filtered_df['user_id'].nunique())

# Visualization 1: Sales Trend by Date
st.markdown("### Sales Trend Over Time")
trend_chart = alt.Chart(filtered_df[filtered_df['type'] == 'purchase']).mark_line().encode(
    x='date_day:T',
    y='sum(price_in_usd):Q',
    color='device:N',
    tooltip=['date_day', 'sum(price_in_usd)', 'device']
).interactive()
st.altair_chart(trend_chart, use_container_width=True)

# Visualization 2: Top Categories
st.markdown("### Top Product Categories")
category_chart = alt.Chart(filtered_df).mark_bar().encode(
    y=alt.Y('category:N', sort='-x'),
    x='count():Q',
    color=alt.Color('category:N', legend=None),
    tooltip=['category', 'count()']
).transform_filter(
    alt.FieldEqualPredicate(field='type', equal='purchase')
)
st.altair_chart(category_chart, use_container_width=True)

# Visualization 3: Device Distribution by Continent
st.markdown("### Device Usage by Continent")
heatmap = alt.Chart(filtered_df).mark_rect().encode(
    y='continent:N',
    x='device:N',
    color='count():Q',
    tooltip=['continent', 'device', 'count()']
).interactive()
st.altair_chart(heatmap, use_container_width=True)

# Visualization 4: Price Distribution by Brand
st.markdown("### Price Distribution by Brand")
scatter = alt.Chart(filtered_df).mark_circle(size=60).encode(
    x='brand:N',
    y='price_in_usd:Q',
    color='brand:N',
    tooltip=['brand', 'price_in_usd']
).interactive()
st.altair_chart(scatter, use_container_width=True)

# Visualization 5: Conversion Funnel
st.markdown("### Conversion Funnel")
funnel_data = filtered_df.groupby('type').agg(total=('type', 'count')).reset_index()
funnel = alt.Chart(funnel_data).mark_bar().encode(
    y='type:N',
    x='total:Q',
    color='type:N'
)
st.altair_chart(funnel, use_container_width=True)