import json
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumWebScraper:
    def __init__(self, config_file='data/sites.json', headless=True):
        """Inicializa o scraper com Selenium para sites com JavaScript."""
        self.config_file = config_file
        self.headless = headless
        self.sites = []
        self.driver = None
        
        # Configurar e inicializar o driver
        self.setup_driver()
        
        # Carregar configuração
        self.load_config()
    
    def setup_driver(self):
        """Configura o driver do Chrome com otimizações."""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless=new')  # Novo modo headless
                # Configurações para headless funcionar melhor com JS
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--allow-running-insecure-content')
            
            # Otimizações de performance
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--silent')
            chrome_options.add_argument('--log-level=3')
            
            # User agent mais recente
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Configurações de viewport
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Desabilitar automação detectável
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Configurar service
            service = Service(ChromeDriverManager().install())
            
            # Criar driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Executar script para mascarar webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.set_page_load_timeout(30)
            
            print("✅ Driver Chrome configurado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao configurar driver Chrome: {e}")
            sys.exit(1)
    
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
    
    def handle_zipcode_modal(self, zipcode="88070150"):
        """
        Detecta e preenche o modal de CEP se aparecer.
        
        Args:
            zipcode (str): CEP a ser inserido
        """
        try:
            print(f"   🏠 Verificando se há modal de CEP...")
            
            # Aguardar o input de CEP aparecer (máximo 15 segundos)
            zipcode_input = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.NAME, "zipcode"))
            )
            
            print(f"   ✅ Modal de CEP encontrado!")
            print(f"   📝 Preenchendo CEP: {zipcode}")
            
            # Limpar o campo e inserir o novo CEP
            zipcode_input.clear()
            time.sleep(1)  # Pausa pequena após limpar
            zipcode_input.send_keys(zipcode)
            
            print(f"   ⏳ Aguardando 5 segundos antes do submit...")
            time.sleep(5)
            
            # Procurar botão de submit com seletores mais específicos
            submit_success = False
            
            try:
                # Tentar diferentes seletores para o botão
                possible_buttons = [
                    "//button[contains(@class, 'submit') or contains(@class, 'btn') or contains(@class, 'button')]",
                    "//button[@type='submit']",
                    "//input[@type='submit']", 
                    "//button[contains(text(), 'Confirmar')]",
                    "//button[contains(text(), 'OK')]",
                    "//button[contains(text(), 'Salvar')]",
                    "//form//button",
                    "//div[contains(@class, 'modal')]//button"
                ]
                
                for selector in possible_buttons:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, selector)
                        print(f"   🎯 Encontrado botão: {submit_button.text or 'Sem texto'}")
                        print(f"   🖱️  Clicando no botão...")
                        submit_button.click()
                        submit_success = True
                        break
                    except:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️  Erro ao procurar botão: {e}")
            
            if not submit_success:
                # Se não encontrar botão, pressionar Enter
                print(f"   ⌨️  Nenhum botão encontrado, pressionando Enter...")
                zipcode_input.send_keys(Keys.RETURN)
                submit_success = True
            
            print(f"   ⏳ Aguardando dados carregarem após CEP (5s)...")
            time.sleep(5)
            
            print(f"   ✅ CEP configurado com sucesso!")
            return True
            
        except Exception as e:
            print(f"   ℹ️  Nenhum modal de CEP encontrado ou erro: {e}")
            return False
    
    def wait_for_complete_loading(self, timeout=30):
        """
        Aguarda o carregamento completo da página, incluindo JavaScript.
        
        Args:
            timeout (int): Tempo máximo de espera em segundos
        """
        print(f"   ⏳ Aguardando carregamento completo da página ({timeout}s)...")
        
        # 1. Aguardar body estar presente
        print(f"   📄 Aguardando body...")
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"   ✅ Body encontrado!")
        
        # 2. Aguardar JavaScript terminar de executar
        print(f"   🔄 Aguardando JavaScript...")
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        print(f"   ✅ JavaScript carregado!")
        
        # 3. Verificar URL atual e título
        current_url = self.driver.current_url
        current_title = self.driver.title
        print(f"   🌐 URL atual: {current_url}")
        print(f"   📋 Título atual: {current_title}")
        
        # 4. Lidar com modal de CEP se aparecer
        self.handle_zipcode_modal()
        
        # 5. Aguardar aside aparecer especificamente
        print(f"   🎯 Aguardando aside aparecer...")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "aside[data-test='product-details-info']"))
            )
            print(f"   ✅ Aside encontrado!")
        except:
            print(f"   ⚠️  Aside ainda não apareceu, continuando...")
        
        # 6. Aguardar um pouco mais para garantir que conteúdo dinâmico carregue
        print(f"   ⏳ Aguardando conteúdo dinâmico (5s)...")
        time.sleep(5)
        
        print(f"   ✅ Página carregada completamente!")
    
    def extract_aside_content_with_monitoring(self):
        """
        Localiza o aside com data-test='product-details-info' e monitora mudanças nas tags <p>.
        
        Returns:
            dict: Dados extraídos do aside com histórico de mudanças
        """
        try:
            # Localizar o aside usando data-test
            print(f"   🎯 Procurando aside com data-test='product-details-info'...")
            
            aside_element = self.driver.find_element(By.CSS_SELECTOR, "aside[data-test='product-details-info']")
            print(f"   ✅ Aside encontrado!")
            
            # JavaScript para extrair tags <p>
            js_code = """
            const aside = document.querySelector("aside[data-test='product-details-info']");
            const allPTags = aside ? aside.querySelectorAll('p') : [];
            const results = [];
            
            console.log('=== TODAS AS TAGS <p> DENTRO DO ASIDE ===');
            
            for (let i = 0; i < allPTags.length; i++) {
                const pTag = allPTags[i];
                const textContent = pTag.textContent || pTag.innerText || '';
                const innerHTML = pTag.innerHTML || '';
                const classes = pTag.className || '';
                
                console.log(`P Tag ${i+1}:`);
                console.log(`  TextContent: "${textContent}"`);
                console.log(`  InnerHTML: "${innerHTML}"`);
                console.log(`  Classes: "${classes}"`);
                console.log('---');
                
                results.push({
                    index: i+1,
                    textContent: textContent.trim(),
                    innerHTML: innerHTML.trim(),
                    classes: classes,
                    hasPrice: innerHTML.includes('R$') || textContent.includes('R$')
                });
            }
            
            console.log(`Total de tags <p> encontradas: ${results.length}`);
            
            return results;
            """
            
            # Primeira captura
            print(f"   📋 Captura inicial...")
            p_tags_data = self.driver.execute_script(js_code)
            
            # Monitorar mudanças por 10 segundos
            print(f"   ⏱️  Monitorando mudanças no aside por 10 segundos...")
            all_captures = [{'timestamp': '0s', 'data': p_tags_data}]
            
            for second in range(1, 11):
                time.sleep(1)
                new_data = self.driver.execute_script(js_code)
                
                # Verificar se houve mudança
                if new_data != p_tags_data:
                    print(f"   � Mudança detectada aos {second}s!")
                    all_captures.append({'timestamp': f'{second}s', 'data': new_data})
                    p_tags_data = new_data  # Atualizar dados principais
            
            print(f"   �📋 Dados finais - Encontradas {len(p_tags_data)} tag(s) <p> no aside:")
            for p_data in p_tags_data:
                print(f"     P{p_data['index']}:")
                print(f"       TextContent: '{p_data['textContent']}'")
                print(f"       InnerHTML: '{p_data['innerHTML']}'")
                if p_data['classes']:
                    print(f"       Classes: {p_data['classes']}")
                if p_data['hasPrice']:
                    print(f"       💰 PREÇO ENCONTRADO!")
            
            return {
                'aside_found': True,
                'p_tags': p_tags_data,
                'total_p_tags': len(p_tags_data),
                'monitoring_history': all_captures,
                'total_captures': len(all_captures)
            }
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair conteúdo do aside: {e}")
            return {
                'aside_found': False,
                'error': str(e),
                'p_tags': [],
                'total_p_tags': 0,
                'monitoring_history': [],
                'total_captures': 0
            }

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
            print(f"   🌐 Navegando para a URL...")
            self.driver.get(url)
            
            # Aguardar carregamento completo (incluindo JavaScript)
            self.wait_for_complete_loading()
            
            # Debug: Capturar screenshot e verificar conteúdo da página
            print(f"   📸 Salvando screenshot para debug...")
            try:
                self.driver.save_screenshot("debug_screenshot.png")
                print(f"   ✅ Screenshot salvo: debug_screenshot.png")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar screenshot: {e}")
            
            # Debug: Verificar se há conteúdo na página
            page_source_length = len(self.driver.page_source)
            print(f"   📄 Tamanho do HTML: {page_source_length} caracteres")
            
            # Debug: Verificar se há JavaScript ativo
            js_check = self.driver.execute_script("return typeof jQuery !== 'undefined' || typeof $ !== 'undefined' || document.readyState;")
            print(f"   🔧 Status JavaScript: {js_check}")
            
            # Extrair dados do aside com monitoramento
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
    
    def display_results(self, results):
        """Exibe os resultados do scraping no console de forma formatada."""
        print("\n" + "="*80)
        print("📊 RESULTADOS DO WEB SCRAPING - ASIDE EXTRACTION")
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
            
            print(f"📋 TITLE:")
            print(f"   {result.get('title', 'Não encontrado')}")
            print()
            
            aside_data = result.get('aside_data', {})
            
            if aside_data.get('aside_found'):
                print(f"✅ ASIDE ENCONTRADO:")
                print(f"   Total de tags <p>: {aside_data['total_p_tags']}")
                print(f"   Capturas durante monitoramento: {aside_data.get('total_captures', 1)}")
                print()
                
                print(f"💲 TAGS <P> EXTRAÍDAS (DADOS FINAIS):")
                for p_data in aside_data.get('p_tags', []):
                    print(f"   P{p_data['index']}:")
                    print(f"     TextContent: {p_data['textContent']}")
                    print(f"     InnerHTML: {p_data['innerHTML']}")
                    if p_data['classes']:
                        print(f"     Classes: {p_data['classes']}")
                    if p_data.get('hasPrice'):
                        print(f"     🎯 CONTÉM PREÇO!")
                    print()
                
                # Mostrar histórico se houve mudanças
                if aside_data.get('total_captures', 1) > 1:
                    print(f"🔄 HISTÓRICO DE MUDANÇAS:")
                    for capture in aside_data.get('monitoring_history', []):
                        print(f"   📸 Captura em {capture['timestamp']}:")
                        for p_data in capture['data']:
                            if p_data.get('hasPrice'):
                                print(f"     P{p_data['index']}: {p_data['innerHTML']} 💰")
                            else:
                                print(f"     P{p_data['index']}: {p_data['textContent']}")
                    print()
            else:
                print(f"❌ ASIDE NÃO ENCONTRADO:")
                print(f"   Erro: {aside_data.get('error', 'Desconhecido')}")
                print()
    
    def run(self):
        """Executa o processo completo de scraping com Selenium."""
        print("🚀 Iniciando Web Scraper - ASIDE Extraction")
        print("-" * 50)
        
        # Filtrar sites habilitados
        enabled_sites = [site for site in self.sites if site.get('enabled', False)]
        
        if not enabled_sites:
            print("⚠️  Nenhum site habilitado encontrado.")
            return
        
        print(f"🎯 Processando {len(enabled_sites)} site(s) habilitado(s)...")
        
        # Fazer scraping de cada site
        results = []
        for site in enabled_sites:
            result = self.scrape_site(site)
            results.append(result)
        
        # Exibir resultados
        self.display_results(results)
        
        print(f"\n🎉 Scraping finalizado! Processados {len(enabled_sites)} site(s) com sucesso.")
    
    def close(self):
        """Fecha o driver do navegador."""
        if self.driver:
            self.driver.quit()
            print("🔧 Driver encerrado.")


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