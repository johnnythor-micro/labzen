# calculators/molarity.py

def calculate_molarity(molecular_weight: float, desired_conc_m: float, volume_l: float) -> float:
    """
    Calculate the mass (in grams) needed to prepare a solution at a given molar concentration.

    :param molecular_weight: Molecular weight of the solute (g/mol)
    :param desired_conc_m: Desired molar concentration (M)
    :param volume_l: Volume of solution in liters (L)
    :return: mass_needed in grams
    """
    return molecular_weight * desired_conc_m * volume_l