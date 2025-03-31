import streamlit as st
import streamlit.components.v1 as components

# Page config
st.set_page_config(page_title="PnL & Risk Dashboard", layout="wide")

# Title
st.markdown("<h1 style='color:white;'>PnL & Risk Dashboard</h1>", unsafe_allow_html=True)

# Declare and render the component (located in the root directory)
my_component = components.declare_component(
    name="my_component",
    path="."  # current directory
)

# Call the component and get response (optional)
response = my_component()

if response:
    st.subheader("Component Output")
    st.json(response)
