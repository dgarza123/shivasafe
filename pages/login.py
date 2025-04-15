from login_manager import login, is_logged_in, logout, current_user, current_role

st.set_page_config(page_title="Login", layout="centered")

if is_logged_in():
    st.success(f"Logged in as {current_user()} ({current_role()})")
    if st.button("Logout"):
        logout()
else:
    login()
