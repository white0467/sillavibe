import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="경제활동인구 대시보드")

# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='cp949')
    return None

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, '경제활동_통합.csv')
df = load_data(csv_file_path)

# --- Main Application ---
if df is not None:
    st.title("📊 대한민국 경제활동인구 대시보드")

    # --- Sidebar for Filters ---
    st.sidebar.header("🔍 필터")
    
    # Year selection
    sorted_years = sorted(df['년도'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("년도를 선택하세요:", sorted_years)

    # Region selection
    regions = ['계'] + list(df[df['지역'] != '계']['지역'].unique())
    selected_region = st.sidebar.selectbox("지역을 선택하세요:", regions)

    # --- Filtered Data ---
    df_selected_year = df[df['년도'] == selected_year]
    df_selected_region_all_years = df[df['지역'] == selected_region]
    df_selection = df[(df['년도'] == selected_year) & (df['지역'] == selected_region)]

    # --- KPI Metrics ---
    st.header(f"{selected_year}년 {selected_region} 주요 지표", divider='rainbow')

    if not df_selection.empty:
        kpi_data = df_selection.iloc[0]
        econ_active = kpi_data['경제활동인구 (천명)']
        employed = kpi_data['취업자 (천명)']
        unemployed = kpi_data['실업자 (천명)']
        
        # Avoid division by zero
        unemployment_rate = (unemployed / econ_active * 100) if econ_active > 0 else 0
        employment_rate = (employed / econ_active * 100) if econ_active > 0 else 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("경제활동인구 (천명)", f"{econ_active:,.0f}")
        col2.metric("취업자 (천명)", f"{employed:,.0f}")
        col3.metric("실업자 (천명)", f"{unemployed:,.0f}")
        col4.metric("실업률 (%)", f"{unemployment_rate:.2f}%")
        col5.metric("고용률 (%)", f"{employment_rate:.2f}%")
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

    st.markdown("---")

    # --- Chart ---
    st.subheader(f"📈 {selected_region} 연도별 추이")
    if not df_selected_region_all_years.empty:
        trend_data = df_selected_region_all_years.set_index('년도')[['취업자 (천명)', '실업자 (천명)']]
        st.line_chart(trend_data)
    else:
        st.info("추이 데이터를 표시할 수 없습니다.")

    # --- Bar Chart for Regional Comparison ---
    st.subheader(f"📊 {selected_year}년 지역별 고용/실업률 비교", divider='rainbow')
    df_regional_comp = df_selected_year[df_selected_year['지역'] != '계'].copy()
    
    # Calculate employment and unemployment rates
    df_regional_comp['고용률'] = (df_regional_comp['취업자 (천명)'] / df_regional_comp['경제활동인구 (천명)'] * 100)
    df_regional_comp['실업률'] = (df_regional_comp['실업자 (천명)'] / df_regional_comp['경제활동인구 (천명)'] * 100)

    if not df_regional_comp.empty:
        bar_chart_data = df_regional_comp.melt(id_vars=['지역'], value_vars=['고용률', '실업률'], 
                                        var_name='지표', value_name='비율 (%)')
        
        fig = px.bar(bar_chart_data, x='지역', y='비율 (%)', color='지표', 
                    barmode='group', title=f'{selected_year}년 지역별 비교',
                    labels={'비율 (%)': '비율 (%)', '지역': '지역'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("비교 데이터를 표시할 수 없습니다.")

    # --- Raw Data Expander ---
    with st.expander("전체 데이터 보기"):
        st.dataframe(df)

else:
    st.error(f"'{csv_file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
