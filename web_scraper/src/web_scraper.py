#!/usr/bin/env python3
"""
Web Scraper Principal
Este script lê o arquivo JSON de configuração e realiza web scraping das páginas especificadas.
"""

import json
import requests
import sqlite3
import time
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime


class WebScraper:
    def __init__(self, config_file="data/sites.json"):
        """
        Inicializa o WebScraper com o arquivo de configuração.
        
        Args:
            config_file (str): Caminho para o arquivo JSON de configuração
        """
        self.config_file = config_file
        self.sites = []
        self.session = requests.Session()
        
    def load_config(self):
        """Carrega a configuração dos sites do arquivo JSON."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.sites = config.get('sites', [])
                print(f"✅ Configuração carregada: {len(self.sites)} sites encontrados")
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo de configuração '{self.config_file}' não encontrado")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            sys.exit(1)
    
    def scrape_site(self, site_config):
        """
        Realiza o scraping de um site específico.
        
        Args:
            site_config (dict): Configuração do site a ser processado
            
        Returns:
            dict: Dados extraídos do site
        """
        name = site_config.get('name', 'Site Desconhecido')
        url = site_config.get('url')
        selectors = site_config.get('selectors', {})
        headers = site_config.get('headers', {})
        
        if not url:
            print(f"⚠️  Site '{name}': URL não encontrada")
            return None
            
        print(f"\n🔍 Fazendo scraping de: {name}")
        print(f"   URL: {url}")
        
        try:
            # Fazer a requisição HTTP
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse do HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados baseado nos seletores
            extracted_data = {
                'site_name': name,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'data': {}
            }
            
            for field, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    # Se há múltiplos elementos, pegar o texto de todos
                    if len(elements) == 1:
                        extracted_data['data'][field] = elements[0].get_text(strip=True)
                    else:
                        extracted_data['data'][field] = [elem.get_text(strip=True) for elem in elements]
                else:
                    extracted_data['data'][field] = None
                    print(f"   ⚠️  Seletor '{selector}' para '{field}' não encontrou elementos")
            
            # Extração abrangente de preços
            print(f"   🔍 Extraindo preços de múltiplas fontes...")
            
            # Primeira extração imediata
            prices_found = self.extract_price_comprehensive(soup, url)
            
            # Se não encontrou preços satisfatórios, aguardar e tentar novamente
            if not prices_found or (len(prices_found) == 1 and 'json_structured' in prices_found):
                print(f"   ⏳ Aguardando 3 segundos para carregamento dinâmico...")
                time.sleep(3)
                
                # Fazer nova requisição para pegar conteúdo atualizado
                try:
                    response2 = self.session.get(url, headers=headers, timeout=30)
                    response2.raise_for_status()
                    soup2 = BeautifulSoup(response2.content, 'html.parser')
                    prices_found2 = self.extract_price_comprehensive(soup2, url)
                    
                    # Combinar resultados, priorizando os mais recentes
                    prices_found.update(prices_found2)
                    
                except Exception:
                    print(f"   ⚠️  Segunda tentativa falhou, usando dados iniciais")
            
            # Determinar o melhor preço
            best_price = None
            price_source = None
            
            if prices_found:
                # Prioridade: NextJS data > Script data > JSON structured > Text content
                if 'nextjs_data' in prices_found:
                    best_price = prices_found['nextjs_data']
                    price_source = "NextJS"
                elif 'script_data' in prices_found and isinstance(prices_found['script_data'], list):
                    # Pegar o preço mais comum ou o último
                    script_prices = prices_found['script_data']
                    best_price = script_prices[-1]  # Último encontrado
                    price_source = "Script"
                elif 'json_structured' in prices_found:
                    best_price = prices_found['json_structured']
                    price_source = "JSON"
                elif 'text_content' in prices_found and isinstance(prices_found['text_content'], list):
                    text_prices = prices_found['text_content']
                    best_price = text_prices[-1]  # Último encontrado
                    price_source = "Texto"
            
            if best_price:
                extracted_data['data']['price_final'] = f"R$ {best_price:.2f}"
                extracted_data['data']['price_source'] = price_source
                print(f"   ✅ Melhor preço encontrado: R$ {best_price:.2f} (fonte: {price_source})")
                
                # Adicionar todos os preços encontrados para debug
                extracted_data['data']['all_prices_debug'] = {
                    k: (f"R$ {v:.2f}" if isinstance(v, (int, float)) else 
                        [f"R$ {p:.2f}" for p in v] if isinstance(v, list) else str(v))
                    for k, v in prices_found.items()
                }
            else:
                print(f"   ⚠️  Nenhum preço válido encontrado")
                extracted_data['data']['price_final'] = "Não encontrado"
            
            print(f"   ✅ Scraping concluído com sucesso!")
            return extracted_data
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro na requisição: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Erro durante o scraping: {e}")
            return None
    
    def display_results(self, results):
        """
        Exibe os resultados do scraping no console de forma formatada.
        
        Args:
            results (list): Lista com os dados extraídos
        """
        print("\n" + "="*80)
        print("📊 RESULTADOS DO WEB SCRAPING")
        print("="*80)
        
        if not results:
            print("❌ Nenhum resultado encontrado.")
            return
        
        for i, result in enumerate(results, 1):
            if result is None:
                continue
                
            print(f"\n🏷️  SITE {i}: {result['site_name']}")
            print(f"🔗 URL: {result['url']}")
            print(f"📅 Extraído em: {result['scraped_at']}")
            print("-" * 60)
            
            data = result.get('data', {})
            if not data:
                print("   ⚠️  Nenhum dado extraído")
                continue
                
            for field, value in data.items():
                print(f"📋 {field.upper()}:")
                if isinstance(value, list):
                    for item in value:
                        print(f"   • {item}")
                elif value:
                    print(f"   {value}")
                else:
                    print(f"   (não encontrado)")
                print()
    
    def run(self):
        """Executa o processo completo de scraping."""
        print("🚀 Iniciando Web Scraper")
        print("-" * 40)
        
        # Carregar configuração
        self.load_config()
        
        if not self.sites:
            print("❌ Nenhum site configurado para scraping")
            return
        
        # Filtrar apenas sites habilitados
        enabled_sites = [site for site in self.sites if site.get('enabled', True)]
        
        if not enabled_sites:
            print("❌ Nenhum site habilitado para scraping")
            return
            
        print(f"🎯 Processando {len(enabled_sites)} site(s) habilitado(s)...")
        
        # Fazer scraping de cada site
        results = []
        for site in enabled_sites:
            result = self.scrape_site(site)
            results.append(result)
            
            # Pausa entre requisições para ser educado com os servidores
            time.sleep(1)
        
        # Exibir resultados
        self.display_results(results)
        
        print(f"\n🎉 Scraping finalizado! Processados {len([r for r in results if r])} site(s) com sucesso.")

    def extract_price_comprehensive(self, soup, url):
        """
        Extrai preço de múltiplas fontes para pegar o valor mais atualizado.
        
        Args:
            soup: BeautifulSoup object
            url: URL da página
            
        Returns:
            dict: Dicionário com diferentes preços encontrados
        """
        prices = {}
        
        # 1. Extrair do JSON estruturado (pode ser o preço inicial)
        try:
            json_scripts = soup.select('script[type="application/ld+json"]')
            for script in json_scripts:
                script_content = script.get_text()
                if '"offers"' in script_content and '"price"' in script_content:
                    try:
                        data = json.loads(script_content)
                        if isinstance(data, dict) and 'offers' in data:
                            if isinstance(data['offers'], dict) and 'price' in data['offers']:
                                prices['json_structured'] = data['offers']['price']
                            elif isinstance(data['offers'], list) and len(data['offers']) > 0:
                                offer = data['offers'][0]
                                if 'price' in offer:
                                    prices['json_structured'] = offer['price']
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        
        # 2. Buscar preços no JavaScript/Next.js data
        try:
            next_data_scripts = soup.select('script#__NEXT_DATA__')
            for script in next_data_scripts:
                script_content = script.get_text()
                # Procurar por padrões de preço no JavaScript
                price_patterns = [
                    r'"price":\s*(\d+\.?\d*)',
                    r'"lowPrice":\s*(\d+\.?\d*)',
                    r'"value":\s*(\d+\.?\d*)',
                    r'"Price":\s*(\d+\.?\d*)'
                ]
                
                for pattern in price_patterns:
                    matches = re.findall(pattern, script_content)
                    if matches:
                        # Pegar o último preço encontrado (geralmente o mais atualizado)
                        latest_price = matches[-1]
                        prices['nextjs_data'] = float(latest_price)
                        break
        except Exception:
            pass
        
        # 3. Buscar preços em todos os scripts que contenham dados de preço
        try:
            all_scripts = soup.find_all('script')
            for script in all_scripts:
                if script.string:
                    content = script.string
                    # Procurar por diferentes padrões de preço
                    patterns = [
                        r'"price":\s*(\d+\.?\d*)',
                        r'"valor":\s*(\d+\.?\d*)',
                        r'"preco":\s*(\d+\.?\d*)',
                        r'price:\s*(\d+\.?\d*)',
                        r'valor:\s*(\d+\.?\d*)'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            # Converter todos os preços encontrados
                            script_prices = [float(price) for price in matches if float(price) > 0]
                            if script_prices:
                                prices['script_data'] = script_prices
                                break
        except Exception:
            pass
        
        # 4. Buscar padrões de preço no texto da página
        try:
            page_text = soup.get_text()
            # Padrões brasileiros de preço
            price_patterns = [
                r'R\$\s*(\d+[.,]\d{2})',
                r'(\d+[.,]\d{2})\s*reais?',
                r'valor:\s*R\$\s*(\d+[.,]\d{2})',
                r'preço:\s*R\$\s*(\d+[.,]\d{2})'
            ]
            
            found_text_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Converter vírgula para ponto
                        clean_price = match.replace(',', '.')
                        price_value = float(clean_price)
                        if 1.0 <= price_value <= 1000.0:  # Preços razoáveis para produtos
                            found_text_prices.append(price_value)
                    except ValueError:
                        continue
            
            if found_text_prices:
                prices['text_content'] = found_text_prices
        except Exception:
            pass
        
        return prices


def main():
    """Função principal do script."""
    scraper = WebScraper()
    
    try:
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()