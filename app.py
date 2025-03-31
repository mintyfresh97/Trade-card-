import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

my_component = components.declare_component(
    name="my_component",
    path="build"
)

response = my_component()

if response:
    st.write("Component says:")
    st.json(response)
