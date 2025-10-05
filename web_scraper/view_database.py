#!/usr/bin/env python3
"""
Script para visualizar dados salvos no banco de dados SQLite.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def view_database(db_path='data/scraped_prices.db'):
    """Exibe todos os dados salvos no banco de forma organizada."""
    
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    print("="*80)
    print("📊 VISUALIZADOR DO BANCO DE DADOS - WEB SCRAPER")
    print("="*80)
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        cursor = conn.cursor()
        
        # Estatísticas gerais
        cursor.execute('SELECT COUNT(*) as total FROM products')
        total_products = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM price_history')
        total_prices = cursor.fetchone()['total']
        
        print(f"🏷️  Total de produtos: {total_products}")
        print(f"💲 Total de registros de preços: {total_prices}")
        print(f"🗃️  Banco: {db_path}")
        print()
        
        if total_products == 0:
            print("❌ Nenhum produto encontrado no banco.")
            return
        
        # Listar todos os produtos
        cursor.execute('''
            SELECT p.*, COUNT(ph.id) as total_prices
            FROM products p
            LEFT JOIN price_history ph ON p.id = ph.product_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        ''')
        
        products = cursor.fetchall()
        
        for i, product in enumerate(products, 1):
            print("="*60)
            print(f"🏷️  PRODUTO {i}: {product['name']}")
            print("="*60)
            print(f"🆔 ID: {product['id']}")
            print(f"🌐 URL: {product['url']}")
            print(f"🏪 Site: {product['site_name']}")
            print(f"📅 Criado: {product['created_at']}")
            print(f"🔄 Atualizado: {product['updated_at']}")
            print(f"💲 Total de preços salvos: {product['total_prices']}")
            print()
            
            # Histórico de preços para este produto
            cursor.execute('''
                SELECT * FROM price_history 
                WHERE product_id = ? 
                ORDER BY scraped_at DESC
            ''', (product['id'],))
            
            prices = cursor.fetchall()
            
            if prices:
                print(f"💰 HISTÓRICO DE PREÇOS:")
                print("-" * 40)
                
                for j, price in enumerate(prices, 1):
                    print(f"   📊 Registro {j}:")
                    print(f"      💲 Preço: {price['price_text']}")
                    print(f"      🏠 CEP: {price['cep']}")
                    print(f"      📅 Data: {price['scraped_at']}")
                    print(f"      ✅ Status: {price['status']}")
                    
                    if price['css_classes']:
                        print(f"      🎨 Classes CSS: {price['css_classes']}")
                    
                    # Mostrar dados brutos se disponível
                    if price['raw_data']:
                        try:
                            raw_data = json.loads(price['raw_data'])
                            aside_data = raw_data.get('aside_data', {})
                            if aside_data.get('p_tags'):
                                p_tag = aside_data['p_tags'][0]
                                print(f"      🔧 HTML: {p_tag.get('innerHTML', 'N/A')}")
                        except:
                            pass
                    
                    print()
            else:
                print("❌ Nenhum preço encontrado para este produto.")
                print()

def main():
    """Função principal."""
    print("🔍 Iniciando visualizador do banco de dados...")
    view_database()
    print("\n✅ Visualização concluída!")

if __name__ == "__main__":
    main()