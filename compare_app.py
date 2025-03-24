import streamlit as st
import pandas as pd
import io
import docx

st.set_page_config(page_title="השוואת קבצים בעברית", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 10px;
    }
    .stDownloadButton>button {
        background-color: #2196F3;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄🔍 השוואת קבצים: CSV, Excel, TXT, Word")

file_types = {
    "csv": "CSV",
    "excel": "Excel",
    "txt": "TXT",
    "word": "Word"
}

def read_file(file, filetype):
    if filetype == 'csv':
        return pd.read_csv(file)
    elif filetype == 'excel':
        return pd.read_excel(file)
    elif filetype == 'txt':
        return pd.read_csv(file, delimiter='\t')
    elif filetype == 'word':
        doc = docx.Document(file)
        content = "\n".join([para.text for para in doc.paragraphs])
        return pd.DataFrame({"תוכן": content.splitlines()})
    else:
        return pd.DataFrame()

def compare_data(df1, df2):
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    differences = []
    max_rows = max(len(df1), len(df2))
    all_columns = sorted(set(df1.columns).union(set(df2.columns)))

    for row in range(max_rows):
        row1 = df1.iloc[row] if row < len(df1) else pd.Series(dtype=object)
        row2 = df2.iloc[row] if row < len(df2) else pd.Series(dtype=object)

        for col in all_columns:
            val1 = row1.get(col, "")
            val2 = row2.get(col, "")
            if str(val1) != str(val2):
                differences.append({
                    "שורה": row + 1,
                    "עמודה": col,
                    "ערך בקובץ 1": val1,
                    "ערך בקובץ 2": val2
                })

    return pd.DataFrame(differences)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader("📁 בחר קובץ ראשון", type=["csv", "xlsx", "xls", "txt", "docx"], key="file1")
        filetype1 = st.selectbox("📂 סוג הקובץ הראשון", options=list(file_types.keys()), format_func=lambda x: file_types[x], key="type1")

    with col2:
        file2 = st.file_uploader("📁 בחר קובץ שני", type=["csv", "xlsx", "xls", "txt", "docx"], key="file2")
        filetype2 = st.selectbox("📂 סוג הקובץ השני", options=list(file_types.keys()), format_func=lambda x: file_types[x], key="type2")

if file1 and file2:
    st.success("הקבצים נטענו בהצלחה. לוחץ על כפתור ההשוואה!")
    if st.button("🔍 השווה קבצים"):
        df1 = read_file(file1, filetype1)
        df2 = read_file(file2, filetype2)
        result = compare_data(df1, df2)
        if result.empty:
            st.info("✨ לא נמצאו הבדלים בין הקבצים.")
        else:
            st.subheader("📌 הבדלים שנמצאו:")
            st.dataframe(result)
            csv_buffer = io.BytesIO()
            result.to_excel(csv_buffer, index=False, engine='openpyxl')
            st.download_button("📥 הורד את ההבדלים כקובץ Excel", data=csv_buffer.getvalue(), file_name="הבדלים.xlsx")
