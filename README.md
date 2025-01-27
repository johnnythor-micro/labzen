# LabZen

**LabZen** is a streamlined, Python-based lab assistant designed to handle common calculations that researchers and scientists encounter daily. 

Currently, LabZen provides a **Molarity Calculator** with multiple calculation modes:

1. **Calculate Mass** – Given a target concentration and volume, determine how much solute (in grams) you need.
2. **Calculate Molarity** – Given a solute mass and total solution volume, figure out the final molar concentration.
3. **Calculate Volume** – Given a solute mass and a target molar concentration, compute how much total solution volume (in liters) you should prepare.

LabZen also includes:
- **Unit Conversions** for concentration (M, mM, µM, nM) and volume (L, mL, µL) so you can work in whatever scale your experiment requires.
- **Common Reagents** with predefined molecular weights (NaCl, IPTG, Tris base, etc.), or choose a custom reagent with a user-specified molecular weight.

---

## Current Features

1. **Multi-Mode Molarity Calculator**  
   - Easily switch between calculating mass, molarity, or volume in a single interface.  
   - Option to choose from a dropdown of common reagents or specify a custom molecular weight.  

2. **Streamlit Dashboard**  
   - A clean, browser-based user interface running locally.  
   - No need for external hosting or advanced setup—just install the dependencies and launch!

3. **Local Usage**  
   - Designed to run on your own machine (no cloud service required).  
   - Great for quick daily calculations in the lab.

---

## Roadmap / Future Plans

- **Additional Lab Calculators**  
  1. **Buffer Preparation**: Automatic pH and volume calculations, especially for common buffers like PBS, Tris-HCl, etc.  
  2. **PCR Master Mix**: Compute reagent volumes for different reaction setups, including enzyme, primers, and template.  
  3. **Dilution Calculators**: Quickly handle C1V1 = C2V2 scenarios.  
  4. **Spectrophotometry**: Calculate concentrations using Beer–Lambert law, handle extinction coefficients, etc.

- **Enhanced Database of Reagents**  
  - Add more built-in reagents or connect to an external database for real-time molecular weight lookups.

- **Export / Reporting**  
  - Generate PDF or CSV summaries of the calculations for record keeping.

---

## Installation & Usage

1. **Clone or Download** the project:
   ```bash
   git clone https://github.com/<your-username>/labzen.git
   cd labzen
   ```
2. **Create & Activate** a Python environment (using conda or venv):
    ```bash
    conda create -n labzen-env python=3.11
    conda activate labzen-env
    ```
3. **Install dependencies** (e.g., Streamlit):
    ```bash
    pip install streamlit
    ```
4. **Run the App:**
    ```bash
    streamlit run app.py
    ```
5. **Open the local link (usually http://localhost:8501) in your browser.**

---

## Contributing
We welcome suggestions, bug reports, and feature requests!
- Branch off main for new features or fixes.
- Submit a Pull Request once your changes are tested and documented.
- Future expansions will follow the same structure

## License
MIT

## Contact
For questions or suggestions, please open an issue on GitHub or reach out to the repository manager. We appreciate any and all feedback that helps improve LabZen for everyday lab use!
