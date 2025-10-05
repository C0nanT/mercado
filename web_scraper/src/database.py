import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path='data/scraped_prices.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    site_name TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    price_text TEXT,
                    price_html TEXT,
                    price_numeric REAL,
                    price_formatted TEXT,
                    css_classes TEXT,
                    cep TEXT,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    raw_data TEXT,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            conn.commit()
            print("✅ Banco de dados inicializado!")
    
    def save_product(self, name, url, site_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM products WHERE url = ?', (url,))
            result = cursor.fetchone()
            
            if result:
                product_id = result[0]
                cursor.execute('''
                    UPDATE products 
                    SET name = ?, site_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (name, site_name, product_id))
            else:
                cursor.execute('''
                    INSERT INTO products (name, url, site_name)
                    VALUES (?, ?, ?)
                ''', (name, url, site_name))
                product_id = cursor.lastrowid
            
            conn.commit()
            return product_id
    
    def save_price(self, product_id, price_data, cep='88070150'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            aside_data = price_data.get('aside_data', {})
            p_tags = aside_data.get('p_tags', [])
            
            if p_tags:
                price_tag = None
                for tag in p_tags:
                    if tag.get('hasPrice'):
                        price_tag = tag
                        break
                
                if not price_tag and p_tags:
                    price_tag = p_tags[0]
                
                if price_tag:
                    price_numeric = None
                    price_text = price_tag.get('textContent', '')
                    
                    if 'R$' in price_text:
                        try:
                            price_match = re.search(r'R\$\s*([\d,]+)', price_text.replace('.', '').replace(',', '.'))
                            if price_match:
                                price_numeric = float(price_match.group(1))
                        except:
                            pass
                    
                    cursor.execute('''
                        INSERT INTO price_history (
                            product_id, price_text, price_html, price_numeric,
                            price_formatted, css_classes, cep, status, raw_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product_id,
                        price_tag.get('textContent', ''),
                        price_tag.get('innerHTML', ''),
                        price_numeric,
                        f"R$ {price_numeric:.2f}" if price_numeric else None,
                        price_tag.get('classes', ''),
                        cep,
                        'disponível' if price_tag.get('hasPrice') else 'indisponível',
                        json.dumps(price_data, ensure_ascii=False, indent=2)
                    ))
                    
                    price_id = cursor.lastrowid
                    conn.commit()
                    
                    print(f"💾 Preço salvo no banco: ID {price_id}")
                    return price_id
            
            return None
    
    def get_database_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM price_history')
            total_prices = cursor.fetchone()[0]
            
            return {
                'total_products': total_products,
                'total_prices': total_prices,
                'database_path': self.db_path
            }

def main():
    print("🧪 Testando DatabaseManager...")
    db = DatabaseManager()
    stats = db.get_database_stats()
    print(f"📊 Estatísticas: {stats}")
    print("✅ DatabaseManager funcionando!")

if __name__ == "__main__":
    main()
