import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from io import BytesIO

# --- Molarity logic imports ---
from calculators.molarity import (
    calculate_mass,
    calculate_molarity,
    calculate_volume
)

# --- Gibson Assembly logic imports ---
from calculators.assembly import (
    Fragment,
    compute_assembly_protocol
)

# --- Protein (BCA) logic imports ---
from calculators.protein_conc import (
    parse_standard_duplicates,
    compute_standard_regression,
    compute_sample_concentration,
    compute_total_yield
)

def main():
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio(
        "Go to:",
        (
            "Home",
            "Molarity Calculator",
            "Gibson Assembly Calculator",
            "Protein (BCA) Calculator"
        )
    )

    if page_selection == "Home":
        show_home()
    elif page_selection == "Molarity Calculator":
        show_molarity_calculator()
    elif page_selection == "Gibson Assembly Calculator":
        show_gibson_assembly_calculator()
    elif page_selection == "Protein (BCA) Calculator":
        show_bca_protein_calculator()


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
    - **Protein (BCA) Calculator**: Analyze protein concentration and yield with 
      a standard BCA assay approach.

    More features on the way!
    """)


def show_molarity_calculator():
    """
    Displays an advanced Molarity Calculator with multiple modes:
    1) Calculate Mass: (desired M, volume) => grams
    2) Calculate Molarity: (mass, volume) => M
    3) Calculate Volume: (mass, desired M) => liters
    Includes unit conversions and reagent selection.
    """
    st.title("Molarity Calculator")
    st.markdown("""
    This calculator supports:
    - **Calculate Mass** – Given a target concentration (M) and volume (L), determine
      how much solute (in grams) you need.
    - **Calculate Molarity** – Given a solute mass (g) and total solution volume (L),
      figure out the final molar concentration (M).
    - **Calculate Volume** – Given a solute mass (g) and a target molar concentration (M),
      compute how much total solution volume you should prepare.
    - **Unit Conversions** for concentration (M, mM, µM, nM) and volume (L, mL, µL).
    - **Common Reagents** with predefined molecular weights or a custom option.
    """)

    # Dictionary of common reagents and their MW
    common_reagents = {
        "NaCl": 58.44,
        "IPTG": 238.31,
        "Tris Base": 121.14,
        "EDTA (disodium salt)": 372.24,
        "Glucose (Dextrose)": 180.16
    }

    # Let user select calculation mode
    calc_mode = st.radio(
        "Select Calculation Mode:",
        ["Calculate Mass", "Calculate Molarity", "Calculate Volume"]
    )

    # Reagent selection
    reagent_options = ["Custom"] + list(common_reagents.keys())
    selected_reagent = st.selectbox("Select a reagent or 'Custom':", reagent_options)

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

    # Dictionaries for unit conversions
    conc_unit_factors = {"M": 1.0, "mM": 1e-3, "µM": 1e-6, "nM": 1e-9}
    vol_unit_factors = {"L": 1.0, "mL": 1e-3, "µL": 1e-6}
    mass_unit_factors = {"g": 1.0, "mg": 1e-3, "µg": 1e-6}

    if calc_mode == "Calculate Mass":
        # M & Volume -> Mass in grams
        conc_val = st.number_input("Concentration value:", min_value=0.0, value=1.0, format="%.4f")
        conc_unit = st.selectbox("Concentration units:", list(conc_unit_factors.keys()))

        vol_val = st.number_input("Volume value:", min_value=0.0, value=1.0, format="%.4f")
        vol_unit = st.selectbox("Volume units:", list(vol_unit_factors.keys()))

        if st.button("Calculate Required Mass"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                # Convert to M, L
                concentration_m = conc_val * conc_unit_factors[conc_unit]
                volume_l = vol_val * vol_unit_factors[vol_unit]

                mass_needed = calculate_mass(molecular_weight, concentration_m, volume_l)
                st.success(f"Mass required: {mass_needed:.4f} g")

    elif calc_mode == "Calculate Molarity":
        # Mass & Volume -> M
        mass_val = st.number_input("Mass value:", min_value=0.0, value=1.0)
        mass_unit = st.selectbox("Mass units:", list(mass_unit_factors.keys()))

        vol_val = st.number_input("Volume value:", min_value=0.0, value=1.0)
        vol_unit = st.selectbox("Volume units:", list(vol_unit_factors.keys()))

        if st.button("Calculate Molarity"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                mass_g = mass_val * mass_unit_factors[mass_unit]
                volume_l = vol_val * vol_unit_factors[vol_unit]

                molarity_m = calculate_molarity(molecular_weight, mass_g, volume_l)
                st.success(f"Molarity: {molarity_m:.4f} M")

    else:  # "Calculate Volume"
        # Mass & M -> Volume in liters
        mass_val = st.number_input("Mass value:", min_value=0.0, value=1.0)
        mass_unit = st.selectbox("Mass units:", list(mass_unit_factors.keys()))

        conc_val = st.number_input("Desired Concentration:", min_value=0.0, value=1.0, format="%.4f")
        conc_unit = st.selectbox("Concentration units:", list(conc_unit_factors.keys()))

        if st.button("Calculate Volume"):
            if molecular_weight <= 0:
                st.error("Molecular weight must be greater than 0.")
            else:
                mass_g = mass_val * mass_unit_factors[mass_unit]
                concentration_m = conc_val * conc_unit_factors[conc_unit]

                volume_l = calculate_volume(molecular_weight, mass_g, concentration_m)
                st.success(f"Volume required: {volume_l:.4f} L")


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

            # --- EXPORT TO EXCEL ---
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


def show_bca_protein_calculator():
    """
    Streamlit UI for the Protein Concentration & Yield Calculator (BCA),
    using fixed standard concentrations (A1–A9) with duplicates,
    generating a line graph with slope/intercept, and optional Excel export.
    """
    st.title("Protein Concentration & Yield Calculator (BCA) - Fixed Standards")
    st.markdown("""
    This calculator uses **fixed standard concentrations** for wells A1–A9:
    **2.0, 1.5, 1.0, 0.75, 0.5, 0.25, 0.125, 0.025, 0.0 mg/mL** (each in duplicate).
    
    **Steps**:
    1. **Paste Standard Duplicates**: 9 lines, each with 2 columns of absorbance (rep1, rep2).
    2. **Compute** the standard curve. A chart will appear showing your data + best-fit line.
    3. **Sample Info**: up to 3 dilutions.
    4. **Export** to Excel if desired.
    """)

    # 1) Paste standard data
    st.subheader("1. Paste Standard Duplicate Absorbances (A1–A9)")
    st.markdown("""
    - Provide **9 lines** of data, each with **2 columns** for the duplicate absorbances.
    - Example (tabs/spaces):
      ```
      0.200 0.210
      0.155 0.158
      0.105 0.110
      ...
      0.010 0.012
      ```
    """)

    raw_std_text = st.text_area("Paste standard duplicates here:", height=200)

    # Initialize placeholders
    standard_df = None
    slope, intercept = None, None

    if raw_std_text.strip():
        try:
            standard_df = parse_standard_duplicates(raw_std_text)
            st.write("**Parsed Standard Data**:")
            st.dataframe(standard_df)

            slope, intercept = compute_standard_regression(standard_df)
            st.write(f"**Linear Fit**: Abs = {slope:.4f} * Conc + {intercept:.4f}")

            # 2) Show line graph with data + regression line
            st.subheader("Standard Curve Graph")
            chart = create_standard_curve_plot(standard_df, slope, intercept)
            st.altair_chart(chart, use_container_width=True)

        except ValueError as ve:
            st.error(str(ve))

    # 3) Sample info
    st.subheader("2. Sample Information & Dilutions")
    sample_name = st.text_input("Protein Sample Name:", value="MyProtein")
    total_volume_uL = st.number_input("Total Sample Volume (µL):", value=1000.0, step=100.0)

    st.markdown("""
    **Dilutions (technical)**:
    - Up to 3 different dilutions tested in the BCA assay.
    - For each, specify **Dilution Factor** and **Absorbance** (single reading).
    """)

    dilutions_data = []
    for i in range(1, 4):
        col1, col2 = st.columns(2)
        with col1:
            dil_factor = st.number_input(f"Dilution {i} Factor:", min_value=1.0, value=1.0, step=0.5, key=f"dil_factor_{i}")
        with col2:
            abs_val = st.number_input(f"Dilution {i} Absorbance:", min_value=0.0, value=0.0, format="%.4f", key=f"dil_abs_{i}")
        dilutions_data.append((dil_factor, abs_val))

    if st.button("Compute Protein Concentration & Yield"):
        if standard_df is None or slope is None or intercept is None:
            st.error("Cannot compute: standard curve not established.")
        else:
            # Compute concentration for each valid dilution
            computed_concs = []
            for (dfactor, abs_val) in dilutions_data:
                if abs_val > 0:
                    c_val = compute_sample_concentration(abs_val, slope, intercept, dfactor)
                    computed_concs.append(c_val)

            if len(computed_concs) == 0:
                st.error("No positive absorbance readings were provided.")
            else:
                avg_conc = sum(computed_concs) / len(computed_concs)
                total_mg = compute_total_yield(avg_conc, total_volume_uL)

                st.success(f"**Results for {sample_name}**")
                st.write(f"- Final Protein Concentration: **{avg_conc:.3f} mg/mL**")
                st.write(f"- Total Yield: **{total_mg:.3f} mg** (in {total_volume_uL:.1f} µL)")

                # 4) Offer Excel download
                df_result = build_excel_output(
                    standard_df, slope, intercept, sample_name, avg_conc, total_mg
                )
                st.download_button(
                    label="Download Results (Excel)",
                    data=df_to_excel_bytes(df_result),
                    file_name=f"BCA_results_{sample_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ------------- SUPPORT FUNCTIONS FOR PLOTTING & EXCEL EXPORT -----------------

def create_standard_curve_plot(standard_df: pd.DataFrame, slope: float, intercept: float):
    """
    Create an Altair plot showing the standard points (mean Abs) vs. concentration,
    plus a best-fit line using slope/intercept.
    """
    # data points
    points = alt.Chart(standard_df).mark_point(size=80, color="blue").encode(
        x=alt.X("conc_mg_mL", title="Concentration (mg/mL)"),
        y=alt.Y("abs_mean", title="Absorbance"),
        tooltip=["conc_mg_mL", "abs_mean"]
    )

    # regression line
    x_min = standard_df["conc_mg_mL"].min()
    x_max = standard_df["conc_mg_mL"].max()
    line_x = np.linspace(x_min, x_max, 50)
    line_y = slope * line_x + intercept
    line_source = pd.DataFrame({"conc_mg_mL": line_x, "abs_fit": line_y})

    fit_line = alt.Chart(line_source).mark_line(color="red").encode(
        x="conc_mg_mL",
        y="abs_fit"
    )

    chart = alt.layer(points, fit_line).properties(
        width=600,
        height=400,
        title=f"Standard Curve (slope={slope:.4f}, intercept={intercept:.4f})"
    )
    return chart


def build_excel_output(
    standard_df: pd.DataFrame,
    slope: float,
    intercept: float,
    sample_name: str,
    avg_concentration: float,
    total_mg: float
) -> pd.DataFrame:
    """
    Build a single DataFrame with standard results + final sample results,
    ready for Excel export.
    """
    df_out = standard_df.copy()
    df_out["slope"] = slope
    df_out["intercept"] = intercept

    for col in ["Sample_Name", "Total_mg"]:
        if col not in df_out.columns:
            df_out[col] = None

    extra_data = {
        "conc_mg_mL": None,
        "abs_rep1": None,
        "abs_rep2": None,
        "abs_mean": None,
        "slope": slope,
        "intercept": intercept,
        "Sample_Name": None,
        "Total_mg": None
    }
    sample_info = {
        "conc_mg_mL": avg_concentration,
        "abs_rep1": None,
        "abs_rep2": None,
        "abs_mean": None,
        "slope": slope,
        "intercept": intercept,
        "Sample_Name": sample_name,
        "Total_mg": total_mg
    }

    df_extra = pd.DataFrame([extra_data])
    df_sample = pd.DataFrame([sample_info])
    df_out = pd.concat([df_out, df_extra, df_sample], ignore_index=True)

    return df_out


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert a DataFrame to an Excel file in-memory, returning the raw bytes.
    """
    import io
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_workbook
    from pandas import ExcelWriter

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="BCA_Results")
    return buffer.getvalue()


if __name__ == "__main__":
    main()
