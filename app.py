import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Fixed path (point to the build directly at root)
my_component = components.declare_component(
    name="my_component",
    path="."  # <-- This means: use the current directory
)

response = my_component()

if response:
    st.write("Component says:")
    st.json(response)
