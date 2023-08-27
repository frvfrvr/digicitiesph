from modules.extract import preview, extract
import streamlit as st
import datetime

def main():
    # import list of provinces from txt file "provinces_list.txt"
    with open('./provinces_list.txt', 'r') as f:
        provinces = f.read().splitlines()
    
    st.set_page_config(page_title='DigiCitiesPH Data Extractor', 
                       page_icon='🏙', 
                       layout="wide", 
                       initial_sidebar_state="auto", 
                       menu_items={
        'Get Help': 'https://github.com/frvfrvr/digicitiesph/issues/new',
        'Report a bug': "https://github.com/frvfrvr/digicitiesph/issues/new",
    })
    
    st.title('DigiCitiesPH')
    st.write('A web app that extracts the profile of cities of the Philippines from the website [Digital Cities PH](https://www.digitalcitiesph.com/).')
    st.info('**Tip:** For faster preview and extraction (cached after preview), choose a province with fewer cities in Simple mode.', icon="💡")
    
    tab1, tab2 = st.tabs(["⛏ Extract", "🚚 Export"])
    
    with tab1:
        preview_container = st.container()
        selected_mode_description = st.empty()
        preview_disabled = st.checkbox("Check to ready the preview button")
        
        # dropdown list of provinces
        selected_province = preview_container.selectbox(
            'Select province',
            list(provinces), placeholder="Select a province", disabled=preview_disabled)
        
        selected_mode = preview_container.selectbox(
            'Mode of extraction',
            ["Simple", "Advanced"], placeholder="Select a mode of extraction",disabled=True)
        
        if selected_mode == "Simple":
            selected_mode_description.write("""
                     This mode extracts only general information about cities of selected province.
                     
                     Talent table will include only total number of graduates of school levels (senior high school, technical vocational, higher education).
                     """)
        elif selected_mode == "Advanced":
            selected_mode_description.write("""
                     This mode extracts general information and more details of cities of selected province. 
                     
                     Talent table will include not only total number of graduates of school levels but also graduates of specific fields and specializations.
                     """)
        
        if st.button('Preview', disabled=not preview_disabled, type='primary'):
            talent_table, infra_table, business_table, digital_table = preview(selected_province, selected_mode.lower())
            
            talent_tab, infra_tab, business_tab, digital_tab = st.tabs(["Talent", "Infrastructure", "Business Environment", "Digital Parameters"])
            
            with talent_tab:
                # display talent_table dataframe in streamlit
                st.dataframe(talent_table, use_container_width=True)
                
            with infra_tab:
                st.dataframe(infra_table, use_container_width=True)
                
            with business_tab:
                st.dataframe(business_table, use_container_width=True)
                
            with digital_tab:
                st.dataframe(digital_table, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write('Cite the data source:')
            now = datetime.datetime.now()
            st.code(f"IBPAP (n.d.). Digital Cities - Philippines. Digital Cities - Philippines. Retrieved {now.strftime('%B %d, %Y')}, from https://www.digitalcitiesph.com/", language='html')
            st.write('Hover above the code and click the copy button to copy the code.')
            st.divider()
            st.write('Clear cache (Preview and extraction will take a while initially):')
            if st.button('Clear cache'):
                st.cache_data.clear()
                st.success('Cache cleared!')
        with col2:
            st.text_input('Select province',placeholder=selected_province,disabled=True)
            st.text_input('Mode of extraction:',placeholder=selected_mode,disabled=True)
            
            selected_filetype = st.selectbox(
                'Select a file type',
                ['Excel', 'CSV'], disabled=True)
            st.write(f"""
                    You selected: {selected_filetype}

                    Tables will be {'separated by `.csv` files (CSV) in zipped file' if selected_filetype == 'CSV' else 'worksheets in single `.xlsx` file (Excel)'}
                    """)
            
            with st.expander('Extract'):
                'Are you sure about that?'
                confirm_extract = st.text_input('Name of selected province:', placeholder=selected_province)
                
                if st.button('Yes'):
                    
                    if confirm_extract != selected_province:
                        st.error('Province name does not match. Please try again.')
                    else:
                        # extract data
                        extracted_file = extract(selected_province, selected_mode.lower(), selected_filetype.lower())
                        st.success('Extraction successful!')
                        st.download_button(label=f"Download {'Zip File' if selected_mode.lower() == 'csv' else 'Excel File'}", data=extracted_file, file_name=f"output.{'zip' if selected_mode.lower() == 'csv' else 'xlsx'}")
                
    st.markdown('''<hr>''', unsafe_allow_html=True)
    st.markdown('''<small>Support by giving [**this app**](https://github.com/frvfrvr/digicitiesph) a ⭐ and follow the [**developer on GitHub**](https://github.com/frvfrvr) for more apps like this. Thank you.</small>''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()