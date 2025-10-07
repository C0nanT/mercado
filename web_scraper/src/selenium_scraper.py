import json
import sys
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database import DatabaseManager
from driver_utils import setup_driver as _setup_driver, close_driver as _close_driver
from config_loader import load_sites_config as _load_sites_config
from page_interactions import (
    handle_zipcode_modal as _handle_zipcode_modal,
    wait_for_complete_loading as _wait_for_complete_loading,
    extract_aside_content_with_monitoring as _extract_aside_content_with_monitoring,
    extract_price_via_js_selector as _extract_price_via_js_selector,
)
from report_utils import (
    display_results as _display_results,
    display_failed_summary as _display_failed_summary,
    display_database_stats as _display_database_stats,
    price_extracted_success as _price_extracted_success,
)


class SeleniumWebScraper:
    def __init__(self, config_file='data/sites.json', headless=True):
        """Inicializa o scraper com Selenium para sites com JavaScript."""
        self.config_file = config_file
        self.headless = headless
        self.sites = []
        self.driver = None
        self.db = DatabaseManager()
        
        # Configurar e inicializar o driver
        self.setup_driver()
        
        # Carregar configuração
        self.load_config()
    
    def setup_driver(self):
        """Configura o driver do Chrome com otimizações."""
        try:
            self.driver = _setup_driver(self.headless)
            print("✅ Driver Chrome configurado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao configurar driver Chrome: {e}")
            sys.exit(1)
    
    def load_config(self):
        """Carrega a configuração dos sites do arquivo JSON."""
        self.sites = _load_sites_config(self.config_file)
        print(f"✅ Configuração carregada: {len(self.sites)} sites encontrados")
    
    def handle_zipcode_modal(self, zipcode=None):
        """
        Detecta e preenche o modal de CEP se aparecer.
        
        Args:
            zipcode (str): CEP a ser inserido
        """
        return _handle_zipcode_modal(self.driver, zipcode=zipcode) or False
    
    def wait_for_complete_loading(self, timeout=30, zipcode=None):
        """
        Aguarda o carregamento completo da página, incluindo JavaScript.
        
        Args:
            timeout (int): Tempo máximo de espera em segundos
        """
        _wait_for_complete_loading(self.driver, timeout=timeout, zipcode=zipcode)
    
    def extract_aside_content_with_monitoring(self):
        """
        Localiza o aside com data-test='product-details-info' e monitora mudanças nas tags <p>.
        
        Returns:
            dict: Dados extraídos do aside com histórico de mudanças
        """
        return _extract_aside_content_with_monitoring(self.driver)

    def extract_price_via_js_selector(self, price_js_expr):
        """
        Extrai o preço executando uma expressão JavaScript (vinda do JSON) que retorna um elemento.
        A expressão deve ser algo como: document.querySelector('...') ou equivalente.

        Retorna um dicionário compatível com o formato 'aside_data' já usado no fluxo atual.
        """
        return _extract_price_via_js_selector(self.driver, price_js_expr)

    def scrape_site(self, site_config):
        """
        Realiza scraping aguardando JavaScript carregar e extraindo dados do aside.
        
        Args:
            site_config (dict): Configuração do site
            
        Returns:
            dict: Dados extraídos
        """
        name = site_config.get('name', 'Site Desconhecido')
        url = site_config.get('url')
        
        if not url:
            print(f"⚠️  Site '{name}': URL não encontrada")
            return None
            
        print(f"\n🔍 Fazendo scraping de: {name}")
        print(f"   URL: {url}")
        
        try:
            # Carregar a página
            self.driver.get(url)
            
            # Aguardar carregamento completo (incluindo JavaScript), com CEP do JSON
            zipcode = site_config.get('cep') or site_config.get('zipcode')
            self.wait_for_complete_loading(zipcode=zipcode)
            
            # Debug: Capturar screenshot e verificar conteúdo da página
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.driver.save_screenshot(f"debug_screenshot_{timestamp}.png")
                print(f"   ✅ Screenshot salvo: debug_screenshot_{timestamp}.png")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar screenshot: {e}")
            
            # Debug: Verificar se há JavaScript ativo
            js_check = self.driver.execute_script("return typeof jQuery !== 'undefined' || typeof $ !== 'undefined' || document.readyState;")
            if not js_check:
                print("   ⚠️  JavaScript não está ativo ou carregado corretamente.")
                raise Exception("JavaScript não carregado")

            # Extrair preço via seletor definido no JSON, com fallback para lógica antiga
            price_js_expr = site_config.get('price_js')
            if price_js_expr:
                aside_data = self.extract_price_via_js_selector(price_js_expr)
                # Se falhar, tenta fallback
                if not aside_data.get('aside_found'):
                    print("   ⚠️  price_js não retornou elemento. Tentando fallback do aside...")
                    aside_data = self.extract_aside_content_with_monitoring()
            else:
                aside_data = self.extract_aside_content_with_monitoring()
            
            # Extrair título da página
            title = ""
            try:
                title_element = self.driver.find_element(By.TAG_NAME, "title")
                title = title_element.get_attribute("text") or ""
            except:
                try:
                    h1_element = self.driver.find_element(By.TAG_NAME, "h1")
                    title = h1_element.text
                except:
                    title = "Título não encontrado"
            
            extracted_data = {
                'site_name': name,
                'url': url,
                'title': title.strip(),
                'scraped_at': datetime.now().isoformat(),
                'aside_data': aside_data
            }
            
            print(f"   ✅ Scraping concluído!")
            return extracted_data
            
        except Exception as e:
            print(f"   ❌ Erro durante scraping: {e}")
            return None
    
    def save_to_database(self, site_config, result):
        """
        Salva os dados extraídos no banco de dados SQLite.
        
        Args:
            site_config (dict): Configuração do site
            result (dict): Dados extraídos do scraping
        """
        try:
            # Salvar produto (usar market do JSON como site_name)
            product_id = self.db.save_product(
                name=result.get('site_name', site_config.get('name', 'Produto')),
                url=site_config.get('url'),
                site_name=site_config.get('market') or 'Desconhecido'
            )
            
            # Salvar preço
            if product_id:
                cep_value = site_config.get('cep') or site_config.get('zipcode')
                price_id = self.db.save_price(product_id, result, cep=cep_value or None)
                if price_id:
                    print(f"   💾 Dados salvos no banco - Produto ID: {product_id}, Preço ID: {price_id}")
                else:
                    print(f"   ⚠️  Produto salvo mas falha ao salvar preço")
            else:
                print(f"   ❌ Falha ao salvar produto no banco")
                
        except Exception as e:
            print(f"   ❌ Erro ao salvar no banco: {e}")
    
    def display_results(self, results):
        """Exibe os resultados do scraping no console de forma formatada."""
        _display_results(results)
    
    def display_database_stats(self):
        """Exibe estatísticas do banco de dados."""
        _display_database_stats(self.db)

    def price_extracted_success(self, result):
        """
        Verifica se a extração do preço foi bem-sucedida.
        Retorna (success: bool, reason_if_fail: str|None)
        """
        return _price_extracted_success(result)

    def display_failed_summary(self, failed_items):
        """Exibe um resumo dos produtos cujo preço não pôde ser extraído."""
        _display_failed_summary(failed_items)

    def run(self):
        """Executa o processo completo de scraping com Selenium."""
        print("🚀 Iniciando Web Scraper")
        print("-" * 50)
            
        # Filtrar sites habilitados
        enabled_sites = [site for site in self.sites if site.get('enabled', False)]
            
        if not enabled_sites:
            print("⚠️  Nenhum site habilitado encontrado.")
            return
            
        print(f"🎯 Processando {len(enabled_sites)} site(s) habilitado(s)...")
            
        # Fazer scraping de cada site
        results = []
        failed_products = []
        for site in enabled_sites:
            result = self.scrape_site(site)
            results.append(result)

            success, reason = self.price_extracted_success(result)
            if success:
                # Salvar no banco de dados apenas quando o preço foi identificado
                self.save_to_database(site, result)
            else:
                failed_products.append({
                    'site_name': site.get('name', 'Desconhecido'),
                    'url': site.get('url'),
                    'reason': reason
                })
            
        # Exibir resultados detalhados
        self.display_results(results)
        
        # Exibir resumo dos que falharam
        self.display_failed_summary(failed_products)
        
        # Exibir estatísticas do banco de dados
        self.display_database_stats()
            
        print(f"\n🎉 Scraping finalizado! Processados {len(enabled_sites)} site(s) com sucesso.")
    
    def close(self):
        _close_driver(self.driver)
        self.driver = None


def main():
    """Função principal."""
    # Detectar modo baseado em argumentos ou usar modo visual por padrão
    import sys
    headless_mode = '--headless' in sys.argv
    
    print(f"🔧 Modo: {'Headless (invisível)' if headless_mode else 'Visual (janela do navegador)'}")
    print(f"💡 Dica: Use 'python run_selenium_scraper.py --headless' para modo invisível")
    
    scraper = SeleniumWebScraper(headless=headless_mode)
    
    try:
        scraper.run()
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()