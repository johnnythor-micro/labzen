# app.py

import streamlit as st
from calculators.molarity import calculate_molarity

def main():
    st.title("LabZen")
    st.subheader("Molarity Calculator")

    molecular_weight = st.number_input(
        "Molecular Weight (g/mol)", 
        min_value=0.0, 
        value=0.0, 
        format="%.4f"
    )
    desired_concentration = st.number_input(
        "Concentration (M)", 
        min_value=0.0, 
        value=0.0, 
        format="%.4f"
    )
    volume = st.number_input(
        "Volume (L)", 
        min_value=0.0, 
        value=0.0, 
        format="%.4f"
    )

    if st.button("Calculate Mass"):
        # Basic validation
        if molecular_weight <= 0:
            st.error("Molecular weight must be greater than 0.")
        else:
            mass_needed = calculate_molarity(molecular_weight, desired_concentration, volume)
            st.success(f"Mass required: {mass_needed:.4f} g")

if __name__ == "__main__":
    main()
