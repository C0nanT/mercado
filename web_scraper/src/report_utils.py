"""Console reporting helpers for scraper results and stats."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def display_results(results: List[Dict[str, Any]]) -> None:
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DO WEB SCRAPING - ASIDE EXTRACTION")
    print("=" * 80)

    if not results:
        print("❌ Nenhum resultado encontrado.")
        return

    for i, result in enumerate(results, 1):
        if not result:
            continue
        name = result.get("site_name") or result.get("name") or "Desconhecido"
        url = result.get("url") or "-"
        aside = result.get("aside_data") or {}
        ok = bool(aside and aside.get("aside_found") and any(p.get("hasPrice") for p in aside.get("p_tags", [])))
        status = "✅" if ok else "❌"
        print(f"{i:02d}. {status} {name}")
        print(f"    URL: {url}")
        if ok:
            # Show the first price-like snippet
            p = next((p for p in aside.get("p_tags", []) if p.get("hasPrice")), None) or (aside.get("p_tags", [])[:1] or [None])[0]
            if p:
                txt = (p.get("textContent") or "").strip().replace("\n", " ")
                print(f"    Preço: {txt}")
        else:
            print(f"    Motivo: {aside.get('error') or 'Preço não identificado'}")


def display_failed_summary(failed_items: List[Dict[str, Any]]) -> None:
    print("\n" + "=" * 80)
    print("❗ RESUMO: PRODUTOS SEM PREÇO EXTRAÍDO")
    print("=" * 80)
    if not failed_items:
        print("✅ Todos os produtos tiveram o preço extraído com sucesso.")
        return
    print(f"Total com falha: {len(failed_items)}")
    for idx, item in enumerate(failed_items, 1):
        name = item.get("site_name") or "Desconhecido"
        url = item.get("url") or "-"
        reason = item.get("reason") or "Motivo não informado"
        print(f"{idx}. {name}")
        print(f"   URL: {url}")
        print(f"   Motivo: {reason}")


def display_database_stats(db) -> None:
    try:
        stats = db.get_database_stats()
        print("\n" + "=" * 60)
        print("💾 ESTATÍSTICAS DO BANCO DE DADOS")
        print("=" * 60)
        print(f"🏷️  Total de produtos: {stats['total_products']}")
        print(f"💲 Total de preços: {stats['total_prices']}")
        print(f"🗃️  Banco: {stats['database_path']}")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas do banco: {e}")


def price_extracted_success(result: Dict[str, Any]) -> tuple[bool, str | None]:
    if not result:
        return False, "Erro durante scraping"
    aside_data = result.get("aside_data") or {}
    if not aside_data.get("aside_found"):
        return False, aside_data.get("error") or "Bloco de informações (aside) não encontrado"
    p_tags = aside_data.get("p_tags", [])
    if not any(p.get("hasPrice") for p in p_tags):
        return False, "Preço não identificado no conteúdo extraído"
    return True, None
