#!/usr/bin/env python
"""
MCP server minimal qui édite contacts.csv via deux outils :
  • list_columns()   – retourne les colonnes
  • update_cell()    – modifie une cellule
"""
from pathlib import Path
import pandas as pd
import sys, traceback
from mcp.server.fastmcp import FastMCP

# ----- Chemins -----
BASE_DIR = Path(__file__).parent            # dossier du script
CSV_FILE = BASE_DIR / "data" / "contacts.csv"

# ----- Définition du serveur -----
mcp = FastMCP(
    "CSV Editor",
    description="Éditeur CSV local très simple",
    dependencies=["pandas"],               # pour le packaging ultérieur
)

# ----- Outils exposés -----
@mcp.tool()
def list_columns() -> list[str]:
    """Renvoie la liste des colonnes du CSV."""
    return pd.read_csv(CSV_FILE).columns.tolist()

@mcp.tool()
def update_cell(row: int, column: str, value: str) -> str:
    """
    Met à jour la valeur de la cellule (row, column).
    - row : index 0-based
    - column : nom de la colonne
    - value : nouvelle valeur
    """
    df = pd.read_csv(CSV_FILE)
    if column not in df.columns:
        raise ValueError(f"Colonne inconnue : {column}")
    if row < 0 or row >= len(df):
        raise ValueError(f"Ligne {row} hors limites")
    df.at[row, column] = value
    df.to_csv(CSV_FILE, index=False)
    return f"OK – ({row}, {column}) ← {value}"

# ----- Boucle MCP -----
if __name__ == "__main__":
    try:
        # transport="stdio" => dialogue JSON-RPC sur stdin/stdout (requis par Claude & Inspector)
        mcp.run(transport="stdio")
    except Exception:
        # Toute exception survient => trace dans stderr (visible dans les logs Claude)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)