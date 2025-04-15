if submitted:
    if login(username, password):
        st.success("Login successful.")
        st.experimental_rerun()
    else:
        st.error("Invalid credentials.")
