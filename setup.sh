#!/bin/bash

# ==============================================================================
# SETUP SCRIPT - WEB SCRAPER ATACADÃO
# ==============================================================================

echo "🚀 Iniciando setup do Web Scraper Atacadão..."
echo "================================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor instale Python 3.8+."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual se não existir
if [ ! -d "web_scraper/venv" ]; then
    echo "📦 Criando ambiente virtual..."
    cd web_scraper
    python3 -m venv venv
    cd ..
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source web_scraper/venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se Chrome está instalado
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "✅ Chrome/Chromium encontrado"
else
    echo "⚠️  Chrome não encontrado. Instale Google Chrome ou Chromium."
    echo "   Ubuntu/Debian: sudo apt install google-chrome-stable"
    echo "   Ou visite: https://www.google.com/chrome/"
fi

# Testar importações
echo "🧪 Testando importações..."
cd web_scraper
python3 -c "
import selenium
import requests
import bs4
from webdriver_manager.chrome import ChromeDriverManager
print('✅ Todas as dependências importadas com sucesso!')
" 2>/dev/null || echo "❌ Erro ao importar dependências"

# Verificar estrutura do projeto
echo "📁 Verificando estrutura do projeto..."
if [ -f "src/selenium_scraper.py" ] && [ -f "data/sites.json" ] && [ -f "run_selenium_scraper.py" ]; then
    echo "✅ Estrutura do projeto OK"
else
    echo "❌ Arquivos do projeto não encontrados"
    exit 1
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo "================================================="
echo ""
echo "📋 Como usar:"
echo "   1. Ativar ambiente virtual:"
echo "      cd web_scraper && source venv/bin/activate"
echo ""
echo "   2. Executar scraper (modo visual):"
echo "      python run_selenium_scraper.py"
echo ""
echo "   3. Executar scraper (modo headless):"
echo "      python run_selenium_scraper.py --headless"
echo ""
echo "   4. Editar sites para scraping:"
echo "      nano data/sites.json"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Se houver erro de ChromeDriver, ele será baixado automaticamente"
echo "   - Logs detalhados são exibidos durante a execução"
echo "   - Screenshots de debug são salvos como 'debug_screenshot.png'"
echo ""
echo "📚 Documentação completa no README.md"
echo ""