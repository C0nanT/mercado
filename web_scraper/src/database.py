#!/usr/bin/env python3
"""
Módulo de banco de dados SQLite para o Web Scraper
Este arquivo está preparado para uso futuro quando for necessário salvar dados.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Gerenciador do banco de dados SQLite para armazenar resultados do scraping."""
    
    def __init__(self, db_path="data/scraper.db"):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_path (str): Caminho para o arquivo do banco SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Cria as tabelas necessárias no banco de dados."""
        # Garantir que o diretório existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela principal para armazenar resultados do scraping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_json TEXT,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT
                )
            ''')
            
            # Índices para otimizar consultas
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_site_name 
                ON scraping_results(site_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scraped_at 
                ON scraping_results(scraped_at)
            ''')
            
            conn.commit()
    
    def save_result(self, site_name, url, data, success=True, error_message=None):
        """
        Salva um resultado de scraping no banco de dados.
        
        Args:
            site_name (str): Nome do site
            url (str): URL processada
            data (dict): Dados extraídos
            success (bool): Se o scraping foi bem-sucedido
            error_message (str): Mensagem de erro, se houver
            
        Returns:
            int: ID do registro inserido
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            data_json = json.dumps(data, ensure_ascii=False) if data else None
            
            cursor.execute('''
                INSERT INTO scraping_results 
                (site_name, url, data_json, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (site_name, url, data_json, success, error_message))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_results(self, site_name=None, limit=100, offset=0):
        """
        Recupera resultados do banco de dados.
        
        Args:
            site_name (str, optional): Filtrar por nome do site
            limit (int): Número máximo de resultados
            offset (int): Número de resultados para pular
            
        Returns:
            list: Lista de resultados
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Para acessar por nome da coluna
            cursor = conn.cursor()
            
            query = '''
                SELECT id, site_name, url, scraped_at, data_json, success, error_message
                FROM scraping_results
            '''
            params = []
            
            if site_name:
                query += ' WHERE site_name = ?'
                params.append(site_name)
            
            query += ' ORDER BY scraped_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result['data_json']:
                    result['data'] = json.loads(result['data_json'])
                else:
                    result['data'] = {}
                del result['data_json']  # Remove o campo JSON raw
                results.append(result)
            
            return results
    
    def get_stats(self):
        """
        Retorna estatísticas do banco de dados.
        
        Returns:
            dict: Estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute('SELECT COUNT(*) FROM scraping_results')
            total = cursor.fetchone()[0]
            
            # Sucessos e falhas
            cursor.execute('SELECT COUNT(*) FROM scraping_results WHERE success = 1')
            successes = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM scraping_results WHERE success = 0')
            failures = cursor.fetchone()[0]
            
            # Sites únicos
            cursor.execute('SELECT COUNT(DISTINCT site_name) FROM scraping_results')
            unique_sites = cursor.fetchone()[0]
            
            # Último scraping
            cursor.execute('SELECT MAX(scraped_at) FROM scraping_results')
            last_scraping = cursor.fetchone()[0]
            
            return {
                'total_records': total,
                'successful_scrapings': successes,
                'failed_scrapings': failures,
                'unique_sites': unique_sites,
                'last_scraping': last_scraping
            }
    
    def clear_data(self, site_name=None, older_than_days=None):
        """
        Remove dados do banco.
        
        Args:
            site_name (str, optional): Remove apenas dados de um site específico
            older_than_days (int, optional): Remove dados mais antigos que N dias
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'DELETE FROM scraping_results'
            params = []
            conditions = []
            
            if site_name:
                conditions.append('site_name = ?')
                params.append(site_name)
            
            if older_than_days:
                conditions.append("scraped_at < datetime('now', '-{} days')".format(older_than_days))
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            cursor.execute(query, params)
            deleted_rows = cursor.rowcount
            conn.commit()
            
            return deleted_rows


# Exemplo de uso (comentado para não executar automaticamente)
if __name__ == "__main__":
    # db = DatabaseManager()
    # 
    # # Exemplo de salvamento
    # result_id = db.save_result(
    #     site_name="Example Site",
    #     url="https://example.com",
    #     data={"title": "Exemplo", "price": "R$ 100,00"}
    # )
    # 
    # # Exemplo de consulta
    # results = db.get_results(limit=10)
    # for result in results:
    #     print(f"Site: {result['site_name']}, Data: {result['data']}")
    # 
    # # Estatísticas
    # stats = db.get_stats()
    # print("Estatísticas:", stats)
    
    pass