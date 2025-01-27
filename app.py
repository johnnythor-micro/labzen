import streamlit as st
import pandas as pd
from io import BytesIO

# Import your existing calculators
from calculators.molarity import (
    calculate_mass,
    calculate_molarity,
    calculate_volume
)
from calculators.assembly import (
    Fragment,
    compute_assembly_protocol
)

def main():
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio(
        "Go to:",
        ("Home", "Molarity Calculator", "Gibson Assembly Calculator")
    )

    if page_selection == "Home":
        show_home()
    elif page_selection == "Molarity Calculator":
        show_molarity_calculator()
    elif page_selection == "Gibson Assembly Calculator":
        show_gibson_assembly_calculator()


def show_home():
    st.title("LabZen")
    st.header("Welcome to LabZen!")
    st.markdown("""
    **LabZen** is your streamlined lab assistant, designed for quick, everyday
    calculations. Use the sidebar to access:
    
    - **Molarity Calculator**: Includes unit conversions, predefined reagents,
      and multi-mode calculations.
    - **Gibson Assembly Calculator**: Quickly compute volumes for vector and insert(s)
      using NEBuilder HiFi or Gibson-style assembly.
      
    More features on the way!
    """)


def show_molarity_calculator():
    # Your existing “complicated” molarity calculator code
    st.title("Molarity Calculator")
    # ... (omitted for brevity)
    # See earlier sections for the full code
    pass


def show_gibson_assembly_calculator():
    """
    Displays the Gibson/NEBuilder Assembly Calculator UI with an export-to-Excel option.
    """

    st.title("Gibson/NEBuilder Assembly Calculator")
    st.markdown("""
    This calculator helps you set up a Gibson or NEBuilder HiFi DNA Assembly reaction.
    
    1. **Add each fragment** (vector + inserts).
    2. **Specify** length (bp) and concentration (ng/µL).
    3. **Choose** your desired total reaction volume, Master Mix concentration,
       and stoichiometric ratios.
    4. **Calculate** recommended volumes for each fragment, Master Mix, and water.
    5. **Optionally**, export your results to Excel.
    """)

    # User inputs
    total_rxn_vol = st.number_input("Total Reaction Volume (µL):", value=10.0, step=1.0)
    master_mix_conc = st.selectbox("Master Mix Concentration (X):", [1.33, 2.0])
    vector_pmol = st.number_input("Target Vector pmol:", value=0.02, format="%.3f")
    insert_excess = st.number_input("Insert Molar Excess (relative to vector):", value=2.0)

    # Number of fragments
    fragment_count = st.number_input(
        "Number of fragments (including vector):",
        min_value=1,
        max_value=10,
        value=2
    )

    fragments = []
    for i in range(int(fragment_count)):
        st.write(f"### Fragment {i+1}")
        name = st.text_input(f"Name for fragment {i+1}:", value=f"Fragment_{i+1}")
        length = st.number_input(f"Length (bp) for {name}:", min_value=1.0, value=1000.0)
        conc = st.number_input(f"Concentration (ng/µL) for {name}:", min_value=0.0, value=50.0)
        is_vec = st.checkbox(f"Is {name} the vector?", key=f"is_vector_{i}")

        fragments.append(
            Fragment(name=name, length_bp=length, concentration_ng_ul=conc, is_vector=is_vec)
        )

    # Button to compute the protocol
    if st.button("Compute Assembly Protocol"):
        try:
            result = compute_assembly_protocol(
                fragments=fragments,
                total_reaction_volume=total_rxn_vol,
                master_mix_concentration=master_mix_conc,
                vector_pmol=vector_pmol,
                insert_molar_excess=insert_excess
            )
            st.success("Assembly Protocol Computed!")

            # Display results on the UI
            st.write("**Fragment Volumes (µL):**")
            for f_name, vol in result["fragment_volumes"].items():
                st.write(f"- {f_name}: {vol:.2f} µL")

            st.write(f"**Master Mix Volume:** {result['master_mix_volume']:.2f} µL")
            st.write(f"**Water Volume:** {result['water_volume']:.2f} µL")
            st.write(f"**Total Reaction Volume:** {result['total_reaction_volume']:.2f} µL")

            # --- EXPORT TO EXCEL FEATURE ---
            # Create a DataFrame for easy Excel export
            data_rows = []
            for f_name, vol in result["fragment_volumes"].items():
                data_rows.append({"Component": f_name, "Volume (µL)": round(vol, 2)})
            data_rows.append({"Component": "Master Mix", "Volume (µL)": round(result["master_mix_volume"], 2)})
            data_rows.append({"Component": "Water", "Volume (µL)": round(result["water_volume"], 2)})
            data_rows.append({"Component": "Total Reaction Volume", "Volume (µL)": round(result["total_reaction_volume"], 2)})

            df = pd.DataFrame(data_rows)

            # Build an Excel file in memory
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='GibsonAssembly')

            # Provide a download button
            st.download_button(
                label="Export to Excel",
                data=buffer.getvalue(),
                file_name="gibson_assembly_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except ValueError as e:
            st.error(str(e))


if __name__ == "__main__":
    main()
