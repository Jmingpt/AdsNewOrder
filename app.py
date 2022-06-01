import streamlit as st
import pandas as pd
from io import StringIO
from module.report_transformation import report_trans
from module.dataframe_excel import to_excel

def run():
    st.set_page_config(page_title="UQMY AdsNewOrder", page_icon="📈")
    st.title("UQMY AdsNewOrder")
    
    uploaded_files = st.file_uploader("Choose a .xlsx/.csv file", accept_multiple_files=True)
    
    if uploaded_files:
        for f in uploaded_files:
            if str(f.name).startswith("ga_"):
                bytes_data = f.read()
                s = str(bytes_data, 'utf-8')
                data = StringIO(s)
                df_ga = pd.read_csv(data)
                st.write("GA file is loaded into Dataframe.")
                
            elif str(f.name).startswith("gads_"):
                bytes_data = f.read()
                s = str(bytes_data, 'utf-8')
                data = StringIO(s)
                df_gads = pd.read_csv(data)
                st.write("GAds file is loaded into Dataframe.")
            
            elif str(f.name).startswith("fb3_"):
                bytes_data = f.read()
                s = str(bytes_data, 'utf-8')
                data = StringIO(s)
                df_fb3 = pd.read_csv(data)
                st.write("FB3 file is loaded into Dataframe.")
                
            elif str(f.name).startswith("fb2_"):
                bytes_data = f.read()
                s = str(bytes_data, 'utf-8')
                data = StringIO(s)
                df_fb2 = pd.read_csv(data)
                st.write("FB2 file is loaded into Dataframe.")
                
        # st.write(df_ga, df_gads, df_fb3)
        
        try:
            df_fb2['Date'] = pd.to_datetime(df_fb2['Date'])
        except:
            pass

        try:
            df_fb3['Date'] = pd.to_datetime(df_fb3['Date'])
        except:
            pass

        df_ga = df_ga.rename(columns={'Google Ads Campaign ID': 'Campaign ID'})
        df_ga['Date'] = pd.to_datetime(df_ga['Date'])
        df_gads['Date'] = pd.to_datetime(df_gads['Date'])
        
        try:
            df_fb = pd.concat([df_fb2, df_fb3], ignore_index=True)
        except:
            try:
                df_fb = df_fb3
            except:
                df_fb = df_fb2
                
        df_result = report_trans(df_fb, df_ga, df_gads)
        st.title("Result:")
        st.write(df_result)
        df_xlsx = to_excel(df_result)
        st.download_button(label='Download as Excel Workbook', 
                            data=df_xlsx, 
                            file_name= 'report_result.xlsx')
    else:
        pass
    
    
if __name__ == "__main__":
    run()
