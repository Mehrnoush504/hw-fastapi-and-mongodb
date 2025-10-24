import streamlit as st
import requests

st.set_page_config(page_title="Nationality Predictor", page_icon="🌍")

st.title("🌍 Nationality Predictor")
name = st.text_input("Enter a name")

if name:
    with st.spinner("Predicting ..."):
        response = requests.get(f"https://api.nationalize.io/?name={name}")
        if response.status_code == 200:
            data = response.json()
            countries = data.get('country', [])[:3]  # Top 3 countries

            if countries:
                for c in countries:
                    country_id = c.get('country_id', '')
                    probability = c.get('probability', 0)  # Corrected key

                    # Display result block (like in your screenshot)
                    with st.container():
                        st.subheader(country_id)  # Country code (e.g., GR, AL, CY)
                        st.write(f"Probability: {probability:.2%}")
                        st.markdown("---")  # Divider line
            else:
                st.warning("No country prediction found.")
        else:
            st.error("Failed to fetch data from API.")
