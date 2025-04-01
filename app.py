import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# This must match your actual build path
my_component = components.declare_component(
    name="my_component",
    path="frontend/my_component/build"
)

# Call the component and optionally capture data
response = my_component()

# Debug output
if response:
    st.write("Component says:")
    st.json(response)
