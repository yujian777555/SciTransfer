import csv
import os

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs, FilterCatalog


def main():
    dataset_dir = "benchmark/datasets/compound_filter"
    hits_path = os.path.join(dataset_dir, "hits.csv")
    train_path = os.path.join(dataset_dir, "train.csv")
    output_dir = "pred_results"
    output_path = os.path.join(output_dir, "compound_filter_results.txt")

    # Set up PAINS and Brenk filters
    params = FilterCatalog.FilterCatalogParams()
    fc = FilterCatalog.FilterCatalogParams.FilterCatalogs

    if hasattr(fc, "PAINS"):
        params.AddCatalog(fc.PAINS)
    else:
        # Newer RDKit versions may only expose split PAINS catalogs
        for name in ("PAINS_A", "PAINS_B", "PAINS_C"):
            params.AddCatalog(getattr(fc, name))

    if hasattr(fc, "BRENK"):
        params.AddCatalog(fc.BRENK)

    catalog = FilterCatalog.FilterCatalog(params)

    # Read active compounds from train.csv
    active_mols = []
    with open(train_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("ACTIVITY", "").strip() == "1":
                smi = row.get("SMILES", "").strip()
                if not smi:
                    continue
                mol = Chem.MolFromSmiles(smi)
                if mol is not None:
                    active_mols.append(mol)

    active_fps = [
        AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        for mol in active_mols
    ]

    kept_smiles = []

    # Read and filter hits
    with open(hits_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            smi = row.get("SMILES", "").strip()
            if not smi:
                continue

            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue

            # Remove compounds matching PAINS/Brenk filters
            if catalog.GetFirstMatch(mol) is not None:
                continue

            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

            # Keep only if max similarity to any active is < 0.5
            max_sim = 0.0
            for active_fp in active_fps:
                sim = DataStructs.TanimotoSimilarity(fp, active_fp)
                if sim > max_sim:
                    max_sim = sim
                    if max_sim >= 0.5:
                        break

            if max_sim < 0.5:
                kept_smiles.append(smi)

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for smi in kept_smiles:
            f.write(smi + "\n")

    print(f"Saved {len(kept_smiles)} compounds to {output_path}")


if __name__ == "__main__":
    main()