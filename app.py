import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# This assumes index.html is in the root
my_component = components.declare_component(
    name="trade_card",
    path="."  # Refers to the root folder of the repo
)

response = my_component()

if response:
    st.write("Component says:")
    st.json(response)
