import streamlit as st
import pandas as pd
import io
import docx
from fpdf import FPDF

st.set_page_config(page_title="השוואת קבצים בעברית", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        direction: rtl;
        text-align: right;
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
    .highlight {
        background-color: #ffcccc;
        font-weight: bold;
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

    styled_data = []
    differences_for_pdf = []
    max_rows = max(len(df1), len(df2))
    all_columns = sorted(set(df1.columns).union(set(df2.columns)))

    for row in range(max_rows):
        styled_row = {}
        row1 = df1.iloc[row] if row < len(df1) else pd.Series(dtype=object)
        row2 = df2.iloc[row] if row < len(df2) else pd.Series(dtype=object)

        for col in all_columns:
            val1 = row1.get(col, "")
            val2 = row2.get(col, "")
            if str(val1) != str(val2):
                diff_text = f"שורה {row + 1}, עמודה '{col}': קובץ 1: {val1} | קובץ 2: {val2}"
                differences_for_pdf.append(diff_text)
                styled_row[col] = f"❌ קובץ 1: {val1} | קובץ 2: {val2}"
            else:
                styled_row[col] = str(val1)
        styled_data.append(styled_row)

    return pd.DataFrame(styled_data), differences_for_pdf

def generate_pdf_report(differences):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.cell(200, 10, txt="דו"ח השוואת קבצים", ln=True, align='C')
    pdf.ln(10)
    for line in differences:
        pdf.multi_cell(0, 10, txt=line, align='R')
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

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
        result_df, differences = compare_data(df1, df2)
        if result_df.empty:
            st.info("✨ לא נמצאו הבדלים בין הקבצים.")
        else:
            st.subheader("📌 תצוגה ויזואלית של ההבדלים:")
            def highlight_diff(val):
                return 'background-color: #ffcccc' if '❌' in str(val) else ''
            st.dataframe(result_df.style.applymap(highlight_diff))

            # הורדה כ-Excel
            csv_buffer = io.BytesIO()
            result_df.to_excel(csv_buffer, index=False, engine='openpyxl')
            st.download_button("📥 הורד את ההבדלים כקובץ Excel", data=csv_buffer.getvalue(), file_name="הבדלים.xlsx")

            # הורדה כ-PDF
            pdf_file = generate_pdf_report(differences)
            st.download_button("📄 הורד את הדו"ח כ-PDF", data=pdf_file, file_name="דו"ח_השוואה.pdf")
