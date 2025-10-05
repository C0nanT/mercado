# 🏗️ Estrutura e Lógica do Sistema - Web Scraper Mercado

Documentação técnica detalhada da arquitetura e funcionamento interno.

## 📁 Estrutura de Arquivos

```
web_scraper/
├── src/
│   ├── selenium_scraper.py    # 🤖 Scraper principal
│   └── database.py           # 💾 Gerenciador SQLite
├── data/
│   ├── sites.json           # ⚙️ Configuração de sites
│   └── scraped_prices.db    # 🗃️ Banco SQLite
├── run_selenium_scraper.py  # 🚀 Script de execução
├── view_database.py         # 👁️ Visualizador simples
├── manage_database.py       # 🛠️ Ferramenta completa
├── db_quick.py             # ⚡ Comandos rápidos
├── venv/                   # 🐍 Ambiente virtual
└── README*.md             # 📚 Documentação
```

## 🔧 Componentes Principais

### **1. SeleniumWebScraper (`src/selenium_scraper.py`)**

#### **Responsabilidades:**
- Automação do navegador Chrome
- Preenchimento automático do modal CEP
- Extração de dados de elementos JavaScript
- Integração com banco de dados

#### **Métodos Principais:**
```python
class SeleniumWebScraper:
    def __init__(self, config_file, headless=True)
    def setup_driver()                    # Configura ChromeDriver
    def handle_zipcode_modal()            # Automatiza modal CEP
    def extract_aside_content_with_monitoring()  # Extrai dados
    def scrape_site(site_config)          # Processo completo
    def save_to_database()                # Salva no SQLite
```

#### **Fluxo de Execução:**
1. **Inicialização**: Carrega configurações e setup do driver
2. **Navegação**: Acessa URL do produto
3. **Modal CEP**: Detecta e preenche automaticamente
4. **Aguarda JS**: Espera carregamento completo
5. **Extração**: Localiza aside e extrai dados
6. **Persistência**: Salva no banco SQLite
7. **Cleanup**: Fecha driver

### **2. DatabaseManager (`src/database.py`)**

#### **Responsabilidades:**
- Gerenciamento do banco SQLite
- Criação automática de tabelas
- Operações CRUD para produtos e preços

#### **Estrutura do Banco:**
```sql
-- Tabela de produtos
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    site_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de histórico de preços
CREATE TABLE price_history (
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
);
```

### **3. Configuração (`data/sites.json`)**

#### **Formato:**
```json
{
  "sites": [
    {
      "name": "Nome do Produto",
      "url": "https://www.atacadao.com.br/produto/url",
      "enabled": true
    }
  ]
}
```

## ⚙️ Lógica de Funcionamento

### **1. Processo de Scraping**

```
Inicia Scraper → Carrega sites.json → Setup ChromeDriver → 
Para cada site habilitado → Navega para URL → Detecta modal CEP? →
Se Sim: Preenche CEP 88070150 → Aguarda JS carregar → 
Localiza aside → Monitora mudanças 3s → Extrai dados → 
Salva no banco → Próximo site → Finaliza
```

### **2. Extração de Dados**

**Seletor Principal:**
```css
aside[data-test="product-details-info"]
```

**JavaScript de Extração:**
```javascript
// Localiza aside
const aside = document.querySelector('aside[data-test="product-details-info"]');

// Extrai todas as tags <p>
const pTags = aside.querySelectorAll('p');

// Para cada tag, captura:
const data = {
    textContent: p.textContent.trim(),
    innerHTML: p.innerHTML,
    classes: p.className,
    hasPrice: /R\$\s*[\d,]+/.test(p.textContent)
};
```

### **3. Automação do Modal CEP**

**Estratégia Multi-Seletor:**
```python
modal_selectors = [
    "div[data-testid='zipcode-modal']",
    "div[class*='modal']",
    "div[class*='cep']",
    "div[class*='zipcode']"
]

button_selectors = [
    "button[data-testid='zipcode-continue']",
    "button[type='submit']",
    "button:contains('Confirmar')",
    "button:contains('Continuar')"
]
```

## 🔄 Como Fazer Alterações

### **1. Adicionar Novo Site**

**Editar `data/sites.json`:**
```json
{
  "sites": [
    {
      "name": "Novo Produto",
      "url": "https://site.com/produto",
      "enabled": true
    }
  ]
}
```

### **2. Modificar CEP Padrão**

**Em `src/selenium_scraper.py`:**
```python
def handle_zipcode_modal(self):
    # Alterar CEP aqui
    cep = "12345678"  # Novo CEP
```

### **3. Alterar Tempo de Espera**

**Configurações de timeout:**
```python
# Aguardar modal aparecer
WebDriverWait(self.driver, 30)  # 30 segundos

# Monitoramento de mudanças no aside
time.sleep(3)  # 3 segundos

# Aguardar após submit CEP
time.sleep(5)  # 5 segundos
```

### **4. Modificar Seletores**

**Para novo site com estrutura diferente:**
```python
# Em extract_aside_content_with_monitoring()
aside_selector = 'div[data-test="new-selector"]'  # Novo seletor
```

### **5. Adicionar Novos Campos no Banco**

**Adicionar coluna:**
```python
def add_new_column(self):
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE price_history ADD COLUMN new_field TEXT')
        conn.commit()
```

### **6. Modificar Logs**

**Níveis de log:**
```python
# Detalhado (desenvolvimento)
print(f"🔧 Debug: {info}")

# Normal (produção)
print(f"✅ {action} realizada")

# Erro
print(f"❌ Erro: {error}")
```

## 🛡️ Tratamento de Erros

### **Hierarquia de Exceções:**
1. **TimeoutException**: Elemento não encontrado
2. **NoSuchElementException**: Seletor inválido  
3. **WebDriverException**: Problemas com Chrome
4. **sqlite3.Error**: Erros de banco
5. **Exception**: Erros gerais

### **Estratégias de Recuperação:**
```python
try:
    # Operação principal
    element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
except TimeoutException:
    # Fallback 1: Tentar seletor alternativo
    try:
        element = self.driver.find_element(By.CSS_SELECTOR, fallback_selector)
    except:
        # Fallback 2: Log e continuar
        print(f"⚠️ Elemento não encontrado: {selector}")
        return None
```

## 🔧 Configurações Avançadas

### **ChromeOptions Personalizadas:**
```python
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
```

### **WebDriverWait Customizado:**
```python
# Wait personalizado para diferentes condições
self.wait = WebDriverWait(self.driver, 30)
self.short_wait = WebDriverWait(self.driver, 5)
self.long_wait = WebDriverWait(self.driver, 60)
```

---
🔧 **Para desenvolvedores:** Este sistema foi projetado para ser modular e extensível. Cada componente tem responsabilidades bem definidas e pode ser modificado independentemente.