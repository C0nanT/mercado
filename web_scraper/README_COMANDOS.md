# 🚀 Guia de Comandos - Web Scraper Mercado

Guia prático para usar todos os comandos e funcionalidades do sistema.

## ⚡ Comandos Principais

### 1. **Executar o Scraper**

**Modo visual (com navegador visível):**
```bash
python run_selenium_scraper.py
```

**Modo headless (invisível - recomendado):**
```bash
python run_selenium_scraper.py --headless
```

### 2. **Ver Dados Salvos**

**Visualização simples:**
```bash
python view_database.py
```
*Saída: Lista de preços no formato "Preço - Produto - Data"*

### 3. **Gerenciar Banco de Dados**

**Ferramenta interativa completa:**
```bash
python manage_database.py
```
*Menu com 11 opções para manipular dados*

**Comandos rápidos:**
```bash
# Contar registros
python db_quick.py count

# Listar últimos preços
python db_quick.py list

# Limpar apenas preços (mantém produtos)
python db_quick.py clear

# Limpar tudo (produtos + preços)
python db_quick.py reset

# Executar SQL personalizado
python db_quick.py sql "SELECT * FROM products"
```

## 🔧 Comandos de Desenvolvimento

### **Testar Banco de Dados**
```bash
python src/database.py
```
*Testa conexão e inicialização do banco*

### **Ativar Ambiente Virtual**
```bash
source venv/bin/activate
```

## 📊 Exemplos de Uso

### **Fluxo Típico de Monitoramento:**
```bash
# 1. Ver dados atuais
python db_quick.py count

# 2. Executar scraping
python run_selenium_scraper.py --headless

# 3. Ver novos dados
python view_database.py
```

### **Fluxo de Teste:**
```bash
# 1. Limpar dados antigos
python db_quick.py clear

# 2. Rodar teste
python run_selenium_scraper.py --headless

# 3. Verificar resultado
python db_quick.py list
```

### **Manipulação de Dados:**
```bash
# Ver estrutura do banco
python manage_database.py
# Escolher opção 1

# Deletar preço específico
python db_quick.py sql "DELETE FROM price_history WHERE id = 5"

# Adicionar produto teste
python manage_database.py
# Escolher opção 9
```

## 🎯 Comandos por Cenário

### **📈 Monitoramento Diário**
```bash
#!/bin/bash
# Script para monitoramento automático
cd /path/to/web_scraper
source venv/bin/activate
python run_selenium_scraper.py --headless
python view_database.py
```

### **🧪 Desenvolvimento/Testes**
```bash
# Limpar e testar
python db_quick.py reset
python run_selenium_scraper.py
python db_quick.py count
```

### **🔍 Análise de Dados**
```bash
# Ver todos os dados
python db_quick.py sql "SELECT p.name, ph.price_text, ph.scraped_at FROM price_history ph JOIN products p ON ph.product_id = p.id ORDER BY ph.scraped_at DESC"

# Contar preços por produto
python db_quick.py sql "SELECT p.name, COUNT(*) FROM price_history ph JOIN products p ON ph.product_id = p.id GROUP BY p.name"
```

## ⚠️ Dicas Importantes

### **Performance:**
- Use sempre `--headless` para execução automática
- O modo visual é só para debug

### **Dados:**
- `clear` remove só preços, mantém produtos
- `reset` remove tudo
- Sempre faça backup antes de `reset`

### **Troubleshooting:**
- Se der erro de ChromeDriver: `pip install --upgrade webdriver-manager`
- Se der erro de banco: `python src/database.py`
- Se der erro de modal CEP: execute em modo visual para ver o que acontece

### **Automação:**
- Crie scripts bash para rotinas repetitivas
- Use cron para execução agendada
- Monitore logs para detectar problemas

## 📋 Referência Rápida

| Comando | Função |
|---------|--------|
| `python run_selenium_scraper.py --headless` | Executar scraping |
| `python view_database.py` | Ver dados |
| `python db_quick.py count` | Contar registros |
| `python db_quick.py list` | Listar preços |
| `python db_quick.py clear` | Limpar preços |
| `python manage_database.py` | Menu completo |
| `python src/database.py` | Testar banco |

---
💡 **Dica:** Sempre execute comandos dentro da pasta do projeto com o venv ativado!