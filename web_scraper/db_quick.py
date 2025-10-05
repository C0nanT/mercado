#!/usr/bin/env python3
"""
Comandos rápidos para manipular o banco SQLite
"""
import sqlite3
import sys

def quick_commands():
    if len(sys.argv) < 2:
        print("📋 Comandos disponíveis:")
        print("  python db_quick.py count     # Conta registros")
        print("  python db_quick.py list      # Lista preços")
        print("  python db_quick.py clear     # Limpa preços")
        print("  python db_quick.py reset     # Limpa tudo")
        print("  python db_quick.py sql 'SELECT ...' # SQL personalizado")
        return
    
    command = sys.argv[1].lower()
    db_path = 'data/scraped_prices.db'
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        if command == 'count':
            cursor.execute('SELECT COUNT(*) FROM products')
            products = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM price_history')
            prices = cursor.fetchone()[0]
            print(f"Produtos: {products} | Preços: {prices}")
            
        elif command == 'list':
            cursor.execute('''
                SELECT ph.id, p.name, ph.price_text, ph.scraped_at 
                FROM price_history ph 
                JOIN products p ON ph.product_id = p.id 
                ORDER BY ph.id DESC LIMIT 10
            ''')
            for row in cursor.fetchall():
                print(f"ID:{row[0]} | {row[2]} | {row[1]} | {row[3]}")
                
        elif command == 'clear':
            cursor.execute('DELETE FROM price_history')
            affected = cursor.rowcount
            conn.commit()
            print(f"Deletados {affected} preços")
            
        elif command == 'reset':
            cursor.execute('DELETE FROM price_history')
            prices_del = cursor.rowcount
            cursor.execute('DELETE FROM products')  
            products_del = cursor.rowcount
            conn.commit()
            print(f"Deletados {products_del} produtos e {prices_del} preços")
            
        elif command == 'sql':
            if len(sys.argv) >= 3:
                sql_query = sys.argv[2]
                try:
                    cursor.execute(sql_query)
                    if sql_query.strip().upper().startswith('SELECT'):
                        for row in cursor.fetchall():
                            print(row)
                    else:
                        conn.commit()
                        print(f"Query executada: {cursor.rowcount} linha(s)")
                except Exception as e:
                    print(f"Erro: {e}")
            else:
                print("Informe a query SQL")
        else:
            print("Comando inválido!")

if __name__ == "__main__":
    quick_commands()