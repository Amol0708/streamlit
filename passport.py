import streamlit as st
import snowflake.connector
import os
import base64
from snowflake.connector.errors import ProgrammingError
 
# Snowflake connection configuration
SNOWFLAKE_USER = "HARISH2"
SNOWFLAKE_PASSWORD = "H@rry2wrk123"
SNOWFLAKE_ACCOUNT = "GUGERKF-RKB53072"
SNOWFLAKE_STAGE = "TB_DOC_AI.RAW_DOC.INSPECTION_REPORTS"
SNOWFLAKE_TABLE = "TB_DOC_AI.RAW_DOC.IR_STRUCTURED"
 
# Function to add custom header
def add_custom_header():
    logo_image_path = r"C:\Users\Admin\streamlit doc\relay\logoleh.png"
 
    def get_base64_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
 
    logo_base64 = get_base64_image(logo_image_path)
 
    st.markdown(
        f"""
        <style>
        .header {{
            background-color: #004d99 !important;
            padding: 10px !important;
            color: white !important;
            width: 100% !important;
            border-radius: 5px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin-bottom: 15px !important;
        }}
        .header .logo-container {{
            position: absolute !important;
            left: 20px !important;
        }}
        .header .title-container {{
            flex: 1 !important;
            text-align: center !important;
        }}
        .header img {{
            width: 80px !important;
            height: 80px !important;
            border-radius: 50% !important;
        }}
        .header h1 {{
            font-size: 46px !important;
            margin: 0 !important;
            line-height: 1.5 !important;
            color: white !important;
        }}
        </style>
        <div class="header">
            <div class="logo-container">
                <img src="data:image/jpeg;base64,{logo_base64}" alt="TechJar Logo">
            </div>
            <div class="title-container">
                <h1>Ladakh Police - Citizen Portal</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
# Enhanced footer
def add_footer():
    st.markdown(
        """
        <style>
        .footer {
            background-color: #004d99 !important;
            color: white !important;
            padding: 10px !important;
            width: 100% !important;
            border-radius: 5px !important;
            text-align: center !important;
            font-size: 16px !important;
            font-weight: bold !important;
            margin-top: 50px !important; /* Adds space above footer */
            box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1); /* Adds a subtle shadow for better visibility */
        }
        </style>
        <div class="footer">
            © 2024 Ladakh Police - Citizen Portal All rights reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )
 
def upload_to_snowflake_stage(file_name, file_content):
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT
        )
        cursor = conn.cursor()
 
        local_file_path = os.path.join(os.getcwd(), file_name)
        with open(local_file_path, "wb") as file:
            file.write(file_content)
 
        upload_query = f"PUT 'file://{local_file_path.replace(os.sep, '/')}' @{SNOWFLAKE_STAGE} AUTO_COMPRESS = FALSE"
        cursor.execute(upload_query)
        st.success(f"File '{file_name}' successfully uploaded to Snowflake stage '{SNOWFLAKE_STAGE}' without compression!")
 
        os.remove(local_file_path)
    except ProgrammingError as e:
        st.error(f"Snowflake error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
 
def fetch_table_data():
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT
        )
        cursor = conn.cursor()
 
        query = f"SELECT * FROM {SNOWFLAKE_TABLE} LIMIT 10"
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return columns, rows
    except ProgrammingError as e:
        st.error(f"Snowflake error: {e}")
        return [], []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], []
    finally:
        cursor.close()
        conn.close()
 
# Streamlit Layout
st.set_page_config(layout="wide")  # Enable wide layout
 
# Add custom header
add_custom_header()
st.text("Upload or capture an image.")
 
# Use columns for layout
col1, col2 = st.columns([1, 1])  # Equal column widths for full-screen view
 
with col1:
    st.subheader("Upload or Capture Image")
    option = st.radio("Select an option:", ["Upload a File", "Capture an Image"])
    file_name = None
    file_content = None
 
    if option == "Upload a File":
        uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg", "pdf"])
        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_content = uploaded_file.read()
            st.image(file_content, caption="Uploaded Image", use_column_width=True)
 
    elif option == "Capture an Image":
        captured_image = st.camera_input("Capture an image using your camera")
        if captured_image is not None:
            file_name = "captured_image.png"
            file_content = captured_image.read()
            st.image(file_content, caption="Captured Image", use_column_width=True)
 
    if file_name and file_content and st.button("Upload to Snowflake"):
        upload_to_snowflake_stage(file_name, file_content)
 
with col2:
    st.subheader("Snowflake Table Data")
    columns, rows = fetch_table_data()
    if columns and rows:
        st.table([dict(zip(columns, row)) for row in rows])
    else:
        st.text("No data available or failed to fetch data.")
 
# Add custom footer
add_footer()
 
 