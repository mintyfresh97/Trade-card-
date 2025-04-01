import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Declare component from root directory
my_component = components.declare_component(
    name="trade_card",
    path="."  # path is now root, where index.html lives
)

# Call the component
response = my_component()

# Show data if any
if response:
    st.write("Component says:")
    st.json(response)
