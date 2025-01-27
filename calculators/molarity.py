# calculators/molarity.py

def calculate_mass(molecular_weight: float, concentration_m: float, volume_l: float) -> float:
    """
    Calculate the mass (in grams) needed to achieve the given molar concentration.

    :param molecular_weight: MW in g/mol
    :param concentration_m: Concentration in M (mol/L)
    :param volume_l: Volume in L
    :return: Mass in grams
    """
    return molecular_weight * concentration_m * volume_l

def calculate_molarity(molecular_weight: float, mass_g: float, volume_l: float) -> float:
    """
    Calculate the molar concentration (M) given mass and volume.

    :param molecular_weight: MW in g/mol
    :param mass_g: Mass in grams
    :param volume_l: Volume in L
    :return: Molar concentration in M (mol/L)
    """
    if molecular_weight == 0 or volume_l == 0:
        raise ValueError("Molecular weight and volume must be greater than 0.")
    return mass_g / (molecular_weight * volume_l)

def calculate_volume(molecular_weight: float, mass_g: float, concentration_m: float) -> float:
    """
    Calculate the volume (in liters) required given mass and molar concentration.

    :param molecular_weight: MW in g/mol
    :param mass_g: Mass in grams
    :param concentration_m: Concentration in M
    :return: Volume in liters
    """
    if molecular_weight == 0 or concentration_m == 0:
        raise ValueError("Molecular weight and concentration must be greater than 0.")
    return mass_g / (molecular_weight * concentration_m)
