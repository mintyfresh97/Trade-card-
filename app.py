import streamlit as st
import streamlit.components.v1 as components

# Set Streamlit page config
st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Declare component from root folder
my_component = components.declare_component(
    name="my_component",
    path="."  # root directory because index.html is now here
)

# Render component
response = my_component()

# Show any response data (optional)
if response:
    st.write("Component says:")
    st.json(response)
