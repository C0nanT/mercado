# 💰 Guia de Seleção de Preços - Web Scraper Mercado

Documentação especializada para entender e modificar a lógica de extração de preços.

## 🎯 Lógica Atual de Seleção

### **Seletor Principal:**
```css
aside[data-test="product-details-info"]
```

**Por que este seletor?**
- ✅ Específico para área de preços do Atacadão
- ✅ Estável (não muda frequentemente)
- ✅ Contém informações estruturadas
- ✅ Carregado via JavaScript

### **Algoritmo de Extração:**

```javascript
// 1. Localiza o aside
const aside = document.querySelector('aside[data-test="product-details-info"]');

// 2. Encontra todas as tags <p> dentro do aside
const pTags = aside.querySelectorAll('p');

// 3. Para cada tag <p>, extrai:
for (let p of pTags) {
    const data = {
        index: i + 1,
        textContent: p.textContent.trim(),
        innerHTML: p.innerHTML,
        classes: p.className,
        hasPrice: /R\$\s*[\d,]+/.test(p.textContent)  // Detecta preço
    };
}
```

## 🔍 Como Identificar Preços

### **Padrão de Reconhecimento:**
```regex
/R\$\s*[\d,]+/
```

**Exemplos que detecta:**
- `R$ 4,19`
- `R$4,19`
- `R$ 29,90`
- `R$   15,50`

### **Priorização de Preços:**
1. **Primeiro**: Tag com `hasPrice: true`
2. **Fallback**: Primeira tag `<p>` encontrada
3. **Backup**: Qualquer texto com "R$"

## ⚙️ Modificando a Lógica de Seleção

### **1. Alterar Seletor Principal**

**Arquivo:** `src/selenium_scraper.py`
**Método:** `extract_aside_content_with_monitoring()`

```python
# ANTES (linha ~200)
aside_selector = 'aside[data-test="product-details-info"]'

# DEPOIS - Exemplo para outro seletor
aside_selector = 'div[class*="price-container"]'  # Novo seletor
```

### **2. Modificar Estratégia de Extração**

**Alterar JavaScript de extração:**

```javascript
// LÓGICA ATUAL - extrai todas as tags <p>
const pTags = aside.querySelectorAll('p');

// NOVA LÓGICA - focar em classes específicas
const pTags = aside.querySelectorAll('p[class*="price"], span[class*="value"]');

// OU - usar múltiplos seletores
const priceElements = aside.querySelectorAll([
    'p[class*="price"]',
    'span[data-test="price"]', 
    '.price-value',
    '[data-price]'
].join(','));
```

### **3. Alterar Regex de Detecção**

```javascript
// ATUAL - detecta R$ + números
hasPrice: /R\$\s*[\d,]+/.test(p.textContent)

// NOVA - mais flexível (aceita centavos)
hasPrice: /R\$\s*[\d,]+(?:\.\d{2})?/.test(p.textContent)

// OU - detectar outros formatos
hasPrice: /(R\$|BRL)\s*[\d,\.]+/.test(p.textContent)

// OU - apenas números com vírgula
hasPrice: /\d+,\d{2}/.test(p.textContent)
```

## 🛠️ Casos de Uso Específicos

### **Caso 1: Site com Estrutura Diferente**

**Problema:** Novo site não usa `aside[data-test="product-details-info"]`

**Solução:**
```python
# Em extract_aside_content_with_monitoring()

# Detectar site pela URL
if 'novosite.com' in self.driver.current_url:
    aside_selector = 'div[class="product-price-area"]'
elif 'outrosite.com' in self.driver.current_url:
    aside_selector = 'section#price-section'
else:
    aside_selector = 'aside[data-test="product-details-info"]'  # Padrão
```

### **Caso 2: Múltiplos Preços na Página**

**Problema:** Página tem preço normal e preço promocional

**Solução:**
```javascript
// Modificar JavaScript para priorizar preços
const results = [];
const pTags = aside.querySelectorAll('p');

// Primeiro, procurar preço promocional
for (let p of pTags) {
    if (p.className.includes('promotional') || p.className.includes('sale')) {
        if (/R\$\s*[\d,]+/.test(p.textContent)) {
            results.unshift({  // Adiciona no início
                index: 0,
                textContent: p.textContent.trim(),
                innerHTML: p.innerHTML,
                classes: p.className + ' PRIORITY',
                hasPrice: true
            });
            break;
        }
    }
}

// Depois, preços normais
// ... resto da lógica
```

### **Caso 3: Preço Carregado Assincronamente**

**Problema:** Preço demora para aparecer

**Solução:**
```python
# Aumentar tempo de monitoramento
def extract_aside_content_with_monitoring(self):
    # ... código anterior ...
    
    # ANTES
    time.sleep(3)  # 3 segundos
    
    # DEPOIS - monitoramento ativo
    max_attempts = 10
    for attempt in range(max_attempts):
        result = self.driver.execute_script(js_extract_code)
        if result and any(tag.get('hasPrice') for tag in result):
            break  # Preço encontrado
        time.sleep(1)  # Aguarda mais 1 segundo
        print(f"   ⏳ Tentativa {attempt + 1} - aguardando preço...")
```

### **Caso 4: Site com Anti-Bot Protection**

**Problema:** Site detecta scraper

**Solução:**
```python
# Adicionar delays mais naturais
import random

def human_like_wait(self):
    """Simula comportamento humano."""
    delay = random.uniform(1.5, 3.5)  # Entre 1.5 e 3.5 segundos
    time.sleep(delay)

# Usar em pontos críticos
def handle_zipcode_modal(self):
    # ... preencher CEP ...
    self.human_like_wait()  # Pausa natural
    # ... clicar botão ...
```

## 🔧 Debugging de Seleção

### **1. Modo Debug Detalhado**

**Adicionar em `extract_aside_content_with_monitoring()`:**
```python
# Após executar JavaScript
result = self.driver.execute_script(js_extract_code)

# DEBUG: Salvar HTML do aside
try:
    aside_html = self.driver.execute_script("""
        const aside = document.querySelector('aside[data-test="product-details-info"]');
        return aside ? aside.outerHTML : 'ASIDE NÃO ENCONTRADO';
    """)
    with open('debug_aside.html', 'w', encoding='utf-8') as f:
        f.write(aside_html)
except Exception as e:
    print(f"Erro ao salvar debug: {e}")
```

### **2. Inspector de Elementos**

**JavaScript para executar no console do navegador:**
```javascript
// Encontrar todos os possíveis containers de preço
console.log('=== ANÁLISE DE PREÇOS ===');

// 1. Procurar por texto com R$
const allElements = document.querySelectorAll('*');
const priceElements = [];

allElements.forEach(el => {
    if (el.textContent && /R\$\s*[\d,]+/.test(el.textContent)) {
        priceElements.push({
            tagName: el.tagName,
            className: el.className,
            textContent: el.textContent.trim(),
            selector: el.getAttribute('data-test') || el.id || 'no-id'
        });
    }
});

console.table(priceElements);

// 2. Testar seletor atual
const currentAside = document.querySelector('aside[data-test="product-details-info"]');
console.log('Aside atual:', currentAside);

if (currentAside) {
    const pTags = currentAside.querySelectorAll('p');
    console.log('Tags P encontradas:', pTags.length);
    pTags.forEach((p, i) => {
        console.log(`P${i+1}:`, p.textContent, '|', p.className);
    });
}
```

### **3. Seletores Alternativos**

**Lista de seletores comuns para preços:**
```css
/* Seletores por data attributes */
[data-test*="price"]
[data-testid*="price"]
[data-price]
[data-value]

/* Seletores por classe */
.price
.valor
.preco
.cost
.amount
.currency

/* Seletores por estrutura */
div[class*="price"]
span[class*="valor"]
p[class*="preco"]

/* Seletores específicos do e-commerce */
.product-price
.item-price
.final-price
.current-price
.sale-price
```

## 📝 Template para Novo Site

**Função para adicionar suporte a novo site:**
```python
def extract_price_from_new_site(self):
    """Extrai preço de um novo site com lógica específica."""
    try:
        # 1. Identificar seletor do site
        site_url = self.driver.current_url
        
        if 'novosite.com' in site_url:
            price_selector = '.product-final-price'
        elif 'outrosite.com.br' in site_url:
            price_selector = '[data-testid="product-price"]'
        else:
            return None  # Site não suportado
        
        # 2. Aguardar elemento aparecer
        price_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
        )
        
        # 3. Extrair texto
        price_text = price_element.text.strip()
        
        # 4. Validar formato
        if re.search(r'R\$\s*[\d,]+', price_text):
            return {
                'price_text': price_text,
                'price_element': price_element,
                'selector_used': price_selector
            }
        
        return None
        
    except Exception as e:
        print(f"Erro ao extrair preço do novo site: {e}")
        return None
```

---
💰 **Dica:** Sempre teste mudanças em modo visual primeiro para ver o comportamento do site antes de automatizar!