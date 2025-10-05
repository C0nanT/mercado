import sqlite3

def view_database():
    with sqlite3.connect('data/scraped_prices.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM price_history')
        total = cursor.fetchone()[0]
        print(f"Total preços: {total}")
        
        cursor.execute('''
            SELECT p.name, ph.price_text, ph.scraped_at
            FROM price_history ph
            JOIN products p ON ph.product_id = p.id
            ORDER BY ph.scraped_at DESC
        ''')
        
        for row in cursor.fetchall():
            print(f"{row[1]} - {row[0]} - {row[2]}")

if __name__ == "__main__":
    view_database()
