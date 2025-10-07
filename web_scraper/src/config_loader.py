"""Load scraping configuration from a JSON file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def load_sites_config(config_file: str) -> List[Dict[str, Any]]:
    """Load the sites configuration file and return the list of site dicts.

    Args:
        config_file: Path to the sites.json configuration.

    Returns:
        List of site configuration dictionaries. Returns empty list on failure.
    """
    path = Path(config_file)
    if not path.is_absolute() and not path.exists():
        # Try resolving relative to this module's directory and its parent (src -> project)
        module_dir = Path(__file__).resolve().parent
        candidates = [
            module_dir / config_file,
            module_dir.parent / config_file,
        ]
        for cand in candidates:
            if cand.exists():
                path = cand
                break
    if not path.exists():
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON em {config_file}: {e}")
        return []

    sites = data.get("sites") if isinstance(data, dict) else None
    if not isinstance(sites, list):
        print(f"❌ Estrutura inválida em {config_file}: chave 'sites' ausente ou não é lista.")
        return []

    return sites
