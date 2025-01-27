# app.py

import streamlit as st
from calculators.molarity import (
    calculate_mass,
    calculate_molarity,
    calculate_volume
)

def main():
    st.title("LabZen")
    st.subheader("Molarity Calculator")

    st.markdown("""
    This tool can:
    1. **Calculate Mass** (Given molarity + volume)
    2. **Calculate Molarity** (Given mass + volume)
    3. **Calculate Volume** (Given mass + molarity)

    **Tip:** You can select common reagents to pre-fill molecular weight.
    """)

    # Dictionary of common reagents and their molecular weights in g/mol
    common_reagents = {
        "NaCl": 58.44,
        "IPTG": 238.31,
        "Tris Base": 121.14,
        "EDTA (disodium salt)": 372.24,
        "Glucose (Dextrose)": 180.16
        # Add more as needed
    }

    # Reagent / Molecular Weight
    reagent_options = ["Custom"] + list(common_reagents.keys())
    selected_reagent = st.selectbox("Select reagent or 'Custom':", reagent_options)

    if selected_reagent == "Custom":
        molecular_weight = st.number_input(
            "Molecular Weight (g/mol)", 
            min_value=0.0, 
            value=0.0, 
            format="%.2f"
        )
    else:
        molecular_weight = common_reagents[selected_reagent]
        st.write(f"**Molecular Weight (g/mol):** {molecular_weight}")

    # Select Calculation Mode
    calc_mode = st.radio(
        "Choose your calculation mode:",
        ("Calculate Mass", "Calculate Molarity", "Calculate Volume")
    )

    # Dictionaries for unit conversions
    conc_unit_factors = {
        "M": 1.0,
        "mM": 1e-3,
        "µM": 1e-6,
        "nM": 1e-9
    }
    vol_unit_factors = {
        "L": 1.0,
        "mL": 1e-3,
        "µL": 1e-6
    }
    mass_unit_factors = {
        "g": 1.0,
        "mg": 1e-3,
        "µg": 1e-6
    }

    if calc_mode == "Calculate Mass":
        # User inputs: Concentration + Volume
        concentration_value = st.number_input("Concentration value:", min_value=0.0, value=1.0)
        concentration_unit = st.selectbox("Concentration units:", list(conc_unit_factors.keys()))

        volume_value = st.number_input("Volume value:", min_value=0.0, value=1.0)
        volume_unit = st.selectbox("Volume units:", list(vol_unit_factors.keys()))

        if st.button("Calculate Mass"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                # Convert to standard SI units
                concentration_m = concentration_value * conc_unit_factors[concentration_unit]
                volume_l = volume_value * vol_unit_factors[volume_unit]

                try:
                    mass_needed = calculate_mass(molecular_weight, concentration_m, volume_l)
                    st.success(f"Mass required: {mass_needed:.4f} g")
                except ValueError as e:
                    st.error(str(e))

    elif calc_mode == "Calculate Molarity":
        # User inputs: Mass + Volume
        mass_value = st.number_input("Mass value:", min_value=0.0, value=1.0)
        mass_unit = st.selectbox("Mass units:", list(mass_unit_factors.keys()))

        volume_value = st.number_input("Volume value:", min_value=0.0, value=1.0)
        volume_unit = st.selectbox("Volume units:", list(vol_unit_factors.keys()))

        if st.button("Calculate Molarity"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                mass_g = mass_value * mass_unit_factors[mass_unit]
                volume_l = volume_value * vol_unit_factors[volume_unit]

                try:
                    molarity_m = calculate_molarity(molecular_weight, mass_g, volume_l)
                    # Convert to best scale? We'll just display in M for now
                    st.success(f"Molarity: {molarity_m:.4f} M")
                except ValueError as e:
                    st.error(str(e))

    elif calc_mode == "Calculate Volume":
        # User inputs: Mass + Concentration
        mass_value = st.number_input("Mass value:", min_value=0.0, value=1.0)
        mass_unit = st.selectbox("Mass units:", list(mass_unit_factors.keys()))

        concentration_value = st.number_input("Concentration value:", min_value=0.0, value=1.0)
        concentration_unit = st.selectbox("Concentration units:", list(conc_unit_factors.keys()))

        if st.button("Calculate Volume"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                mass_g = mass_value * mass_unit_factors[mass_unit]
                concentration_m = concentration_value * conc_unit_factors[concentration_unit]

                try:
                    volume_l = calculate_volume(molecular_weight, mass_g, concentration_m)
                    st.success(f"Volume required: {volume_l:.4f} L")
                except ValueError as e:
                    st.error(str(e))

if __name__ == "__main__":
    main()
