# calculators/assembly.py

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Fragment:
    name: str
    length_bp: float # length in base pairs
    concentration_ng_ul: float # concentration in ng/uL
    is_vector: bool = False # flag to mark if it's the vector
    
def compute_assembly_protocol(
    fragments: List[Fragment],
    total_reaction_volume: float = 20.0,
    master_mix_concentration: float = 2.0,
    vector_pmol: float = 0.05,
    insert_molar_excess: float = 2.0
) -> Dict:
    """
    
    Compute recommended volumes for Gibson/NEB HiFi assembly:
    
    :param fragments: List of Fragment objects.
    :param total_reaction_volume: Final reaction volume in uL (commonly 20 or 10 uL).
    :param master_mix_concentration: 2.0 for the 2X HiFi master mix.
    :param vector_pmol: pmol of vector to target.
    :param insert_molar_excess: how many times more insert relative to vector (molar basis).
    :return: Dictionary with volume recommendations for each fragment and total reaction setup.
    """
    
    # Molar mass of a 1 bp dsDNA is roughly 650 g/mol (approx).
    # This is a simplification; actual values can vary slightly.
    avg_bp_molecular_weight = 650
    
    # First, identify the vector
    vector_list = [f for f in fragments if f.is_vector]
    if len(vector_list) != 1:
        raise ValueError("Exactly one fragment must be flagged as vector.")
    vector = vector_list[0]
    
    # Calculate volume for vector
    # 1) Convert desired vector pmol into mass in ng:
    #    pmol -> mol: vector_pmol * 1e-12
    #    mol -> grams: * (length_bp * 650 g/mol)
    #    grams -> ng: * 1e9
    #    mass_ng = vector_pmol * 1e-12 * (vector.length_bp * avg_bp_molecular_weight) * 1e9
    vector_mass_ng = vector_pmol * 1e-12 * (vector.length_bp * avg_bp_molecular_weight) * 1e9
    
    # The volume needed for the vector in uL:
    # concentration_ng_ul is how many ng per uL
    # volume_vector_ul = mass_ng / concentration_ng_ul
    if vector.concentration_ng_ul <= 0:
        raise ValueError(f"Vector concentration must be > 0 ng/uL for {vector.name}")
    
    vector_volume_ul = vector_mass_ng / vector.concentration_ng_ul
    
    # 2) Calculate volumes for each insert
    fragment_volumes = {}
    fragment_volumes[vector.name] = vector_volume_ul
    
    for frag in fragments:
        if frag.is_vector:
            continue # already handled
        # Insert pmol = insert_molar_excess * vector_pmol
        insert_pmol = insert_molar_excess * vector_pmol
        
        # mass in ng for the insert
        insert_mass_ng = insert_pmol * 1e-12 * (frag.length_bp * avg_bp_molecular_weight) * 1e9
        
        if frag.concentration_ng_ul <= 0:
            raise ValueError(f"Insert concentration must be > 0 ng/uL for {frag.name}")
        
        insert_volume_ul = insert_mass_ng / frag.concentration_ng_ul
        fragment_volumes[frag.name] = insert_volume_ul
        
    # 3) Sum volumes
    sum_fragments_volume = sum(fragment_volumes.values())
    
    # 4) Master Mix Volume
    # If master mix is 2x, half of the total reaction volume is Master Mix
    master_mix_volume = total_reaction_volume / master_mix_concentration
    
    # 5) Water Volume
    # total reaction volume - master_mix_volume - sum of fragment volumes
    water_volume = total_reaction_volume - master_mix_volume - sum_fragments_volume
    if water_volume < 0:
        # This means we've exceeded the total reaction volume with the set pmol, might need to scale down
        raise ValueError("Calculated volumes exceed total reaction volume. Try reducing vector pmol or total fragment count.")
    
    return {
        "fragment_volumes": fragment_volumes, # uL for each fragment
        "master_mix_volume": master_mix_volume, # uL
        "water_volume": water_volume, # uL
        "total_reaction_volume": total_reaction_volume
    }