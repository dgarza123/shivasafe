import streamlit as st

uploaded_file = st.file_uploader("Upload a file", type=["csv", "pdf", "yaml"])

if uploaded_file:
    st.write("File name:", uploaded_file.name)

    # Preview content (optional, depending on file type)
    if uploaded_file.name.endswith(".csv"):
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

    # Save to disk
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.read())
        st.success(f"Saved {uploaded_file.name} to local directory.")
