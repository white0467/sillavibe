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

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("경제활동인구 (천명)", f"{econ_active:,.0f}")
        col2.metric("취업자 (천명)", f"{employed:,.0f}")
        col3.metric("실업자 (천명)", f"{unemployed:,.0f}")
        col4.metric("실업률 (%)", f"{unemployment_rate:.2f}%")
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

    st.markdown("---")

    # --- Charts ---
    col1, col2 = st.columns((6, 4)) # Give more space to the line chart

    with col1:
        st.subheader(f"📈 {selected_region} 연도별 추이")
        if not df_selected_region_all_years.empty:
            trend_data_for_plotly = df_selected_region_all_years[['년도', '취업자 (천명)', '실업자 (천명)']].copy()
            trend_data_long = trend_data_for_plotly.melt(id_vars='년도', 
                    value_vars=['취업자 (천명)', '실업자 (천명)'], 
                    var_name='구분', 
                    value_name='인원 (천명)')
            
            fig_line = px.line(trend_data_long,
                x='년도',
                y='인원 (천명)',
                color='구분',
                markers=True,
                text='인원 (천명)',
                template='streamlit') # Use streamlit's theme
            
            fig_line.update_traces(textposition='top center')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("추이 데이터를 표시할 수 없습니다.")

    with col2:
        st.subheader(f"📊 {selected_year}년 {selected_region} 구성")
        if not df_selection.empty:
            composition_data = {
                '항목': ['취업자', '실업자'],
                '인원 (천명)': [employed, unemployed]
            }
            df_composition = pd.DataFrame(composition_data)
            
            fig_pie = px.pie(df_composition, 
                            names='항목', 
                            values='인원 (천명)', 
                            title='취업자/실업자 비율',
                            hole=0.4,
                            template='streamlit') # Use streamlit's theme
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("구성 데이터를 표시할 수 없습니다.")

    # --- Raw Data Expander ---
    with st.expander("전체 데이터 보기"):
        st.dataframe(df)

else:
    st.error(f"'{csv_file_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")