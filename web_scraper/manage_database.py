#!/usr/bin/env python3
"""
Script para manipular dados do banco SQLite - Ferramenta de Testes
"""
import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='data/scraped_prices.db'):
        self.db_path = db_path

    def show_tables(self):
        """Mostra todas as tabelas do banco."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("📋 Tabelas no banco:")
            for table in tables:
                print(f"  - {table[0]}")

    def show_table_structure(self, table_name):
        """Mostra a estrutura de uma tabela."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n🔧 Estrutura da tabela '{table_name}':")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'PRIMARY KEY' if col[5] else ''}")

    def count_records(self, table_name):
        """Conta registros em uma tabela."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"📊 Total de registros em '{table_name}': {count}")
            return count

    def show_all_products(self):
        """Mostra todos os produtos."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
            print("\n🏷️  PRODUTOS:")
            for p in products:
                print(f"  ID: {p[0]} | Nome: {p[1]} | Site: {p[3]}")

    def show_all_prices(self):
        """Mostra todos os preços."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ph.id, p.name, ph.price_text, ph.scraped_at 
                FROM price_history ph 
                JOIN products p ON ph.product_id = p.id 
                ORDER BY ph.scraped_at DESC
            """)
            prices = cursor.fetchall()
            print("\n💰 PREÇOS:")
            for pr in prices:
                print(f"  ID: {pr[0]} | {pr[2]} | {pr[1]} | {pr[3]}")

    def delete_price_by_id(self, price_id):
        """Deleta um preço específico pelo ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM price_history WHERE id = ?", (price_id,))
            affected = cursor.rowcount
            conn.commit()
            print(f"🗑️  Deletado {affected} registro(s) de preços")

    def delete_product_by_id(self, product_id):
        """Deleta um produto e todos os preços relacionados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Primeiro deleta os preços
            cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
            prices_deleted = cursor.rowcount
            # Depois deleta o produto
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            products_deleted = cursor.rowcount
            conn.commit()
            print(f"🗑️  Deletado {products_deleted} produto(s) e {prices_deleted} preço(s)")

    def clear_all_prices(self):
        """Apaga todos os preços (mantém produtos)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM price_history")
            affected = cursor.rowcount
            conn.commit()
            print(f"🗑️  Deletados {affected} preços")

    def clear_all_data(self):
        """Apaga todos os dados (produtos e preços)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM price_history")
            prices_deleted = cursor.rowcount
            cursor.execute("DELETE FROM products")
            products_deleted = cursor.rowcount
            conn.commit()
            print(f"🗑️  Deletados {products_deleted} produtos e {prices_deleted} preços")

    def add_test_product(self, name, url, site_name="Teste"):
        """Adiciona um produto de teste."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, url, site_name)
                VALUES (?, ?, ?)
            """, (name, url, site_name))
            product_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Produto teste criado - ID: {product_id}")
            return product_id

    def add_test_price(self, product_id, price_text, price_numeric=None):
        """Adiciona um preço de teste."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_history (
                    product_id, price_text, price_numeric, 
                    cep, status, scraped_at
                ) VALUES (?, ?, ?, '88070150', 'teste', ?)
            """, (product_id, price_text, price_numeric, datetime.now()))
            price_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Preço teste criado - ID: {price_id}")
            return price_id

    def execute_custom_sql(self, sql_query):
        """Executa uma query SQL personalizada."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql_query)
                if sql_query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    print("📊 Resultados:")
                    for row in results:
                        print(f"  {row}")
                else:
                    affected = cursor.rowcount
                    conn.commit()
                    print(f"✅ Query executada - {affected} linha(s) afetada(s)")
        except Exception as e:
            print(f"❌ Erro na query: {e}")

def main():
    """Menu interativo para manipular o banco."""
    db = DatabaseManager()
    
    while True:
        print("\n" + "="*50)
        print("🛠️  FERRAMENTA DE MANIPULAÇÃO DO BANCO")
        print("="*50)
        print("1.  Mostrar estrutura do banco")
        print("2.  Contar registros")
        print("3.  Ver todos os produtos")
        print("4.  Ver todos os preços")
        print("5.  Deletar preço por ID")
        print("6.  Deletar produto por ID")
        print("7.  Limpar todos os preços")
        print("8.  Limpar todos os dados")
        print("9.  Adicionar produto teste")
        print("10. Adicionar preço teste")
        print("11. Executar SQL personalizado")
        print("0.  Sair")
        print("-"*50)
        
        try:
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '0':
                print("👋 Saindo...")
                break
            elif choice == '1':
                db.show_tables()
                db.show_table_structure('products')
                db.show_table_structure('price_history')
            elif choice == '2':
                db.count_records('products')
                db.count_records('price_history')
            elif choice == '3':
                db.show_all_products()
            elif choice == '4':
                db.show_all_prices()
            elif choice == '5':
                price_id = input("ID do preço para deletar: ")
                db.delete_price_by_id(int(price_id))
            elif choice == '6':
                product_id = input("ID do produto para deletar: ")
                db.delete_product_by_id(int(product_id))
            elif choice == '7':
                confirm = input("Tem certeza? (s/N): ")
                if confirm.lower() == 's':
                    db.clear_all_prices()
            elif choice == '8':
                confirm = input("ATENÇÃO: Apagar TUDO? (s/N): ")
                if confirm.lower() == 's':
                    db.clear_all_data()
            elif choice == '9':
                name = input("Nome do produto teste: ")
                url = input("URL do produto: ")
                db.add_test_product(name, url)
            elif choice == '10':
                product_id = input("ID do produto: ")
                price_text = input("Texto do preço (ex: R$ 10,50): ")
                try:
                    price_num = float(input("Valor numérico (ex: 10.50): "))
                except:
                    price_num = None
                db.add_test_price(int(product_id), price_text, price_num)
            elif choice == '11':
                sql = input("Query SQL: ")
                db.execute_custom_sql(sql)
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()