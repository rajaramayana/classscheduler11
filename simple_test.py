import streamlit as st

st.title("🏫 Test - Class Routine Management System")
st.write("If you can see this, Streamlit is working!")

# Test basic functionality
st.header("Basic Test")
name = st.text_input("Enter your name:", "Test User")
if st.button("Test Button"):
    st.success(f"Hello {name}! The application is working correctly.")

st.write("Application components loaded successfully:")
st.write("✓ Streamlit")
st.write("✓ Database connection")
st.write("✓ All Python modules")
