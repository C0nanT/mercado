# 🛒 Web Scraper Atacadão - Python 3

Um web scraper automatizado para extrair preços de produtos do site do Atacadão, com suporte completo a JavaScript e configuração automática de CEP.

## 🚀 Funcionalidades

- ✅ **Selenium WebDriver** - Suporte completo a JavaScript
- ✅ **Configuração automática de CEP** - Detecta e preenche modal automaticamente
- ✅ **Extração precisa de preços** - Localiza aside específico com data-test
- ✅ **Modo Visual e Headless** - Escolha entre monitorar ou executar invisível
- ✅ **Monitoramento de mudanças** - Detecta atualizações dinâmicas de preço
- ✅ **Screenshots de debug** - Capturas automáticas para troubleshooting
- ✅ **Configuração JSON** - Sites gerenciados via arquivo de configuração

## 📋 Pré-requisitos

- Python 3.12+
- Google Chrome instalado
- Conexão com internet

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositório>
cd mercado/web_scraper
```

### 2. Criar e ativar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install selenium beautifulsoup4 requests webdriver-manager
```

## 📦 Estrutura do Projeto

```
web_scraper/
├── src/
│   ├── selenium_scraper.py     # Scraper principal com Selenium
│   └── database.py            # Módulo SQLite (futuro)
├── data/
│   └── sites.json            # Configuração de sites
├── run_selenium_scraper.py   # Script de execução
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md               # Este arquivo
```

## 🎯 Como Usar

### Modo Visual (recomendado para debug)
```bash
python run_selenium_scraper.py
```

### Modo Headless (invisível)
```bash
python run_selenium_scraper.py --headless
```

## ⚙️ Configuração

### Editar sites.json
```json
{
    "sites": [
        {
            "name": "Produto Atacadão",
            "url": "https://www.atacadao.com.br/produto/url-aqui",
            "enabled": true
        }
    ]
}
```

### Configurar CEP
O CEP padrão é `88070150`. Para alterar, modifique a função `handle_zipcode_modal()` em `selenium_scraper.py`.

## 🔄 Fluxo de Funcionamento

1. **🌐 Carrega página** do produto
2. **🏠 Detecta modal de CEP** automaticamente  
3. **📝 Preenche CEP** (88070150)
4. **🎯 Submete formulário** e aguarda carregamento
5. **📋 Localiza aside** com `data-test="product-details-info"`
6. **💲 Extrai todas as tags** `<p>` do aside
7. **🎯 Detecta preços** automaticamente (padrão R$)
8. **📊 Exibe resultados** formatados

## 📊 Exemplo de Resultado

```
🏷️  SITE 1: Atacadão Leite 1L
🔗 URL: https://www.atacadao.com.br/leite-longa-vida-aurora-integral-com-tampa-88650-39196/p
📅 Extraído em: 2025-10-05T10:59:29.538661

✅ ASIDE ENCONTRADO:
   Total de tags <p>: 1

💲 TAGS <P> EXTRAÍDAS:
   P1:
     TextContent: R$ 4,19
     InnerHTML: R$&nbsp;4,19
     Classes: text-2xl text-neutral-500 font-bold
     🎯 CONTÉM PREÇO!
```

## 🛡️ Recursos de Segurança

- **Anti-detecção**: User-agent personalizado e mascaramento de webdriver
- **Timeouts configuráveis**: Evita travamentos
- **Error handling**: Tratamento robusto de erros
- **Screenshots automáticos**: Debug visual quando necessário

## 🐛 Troubleshooting

### ChromeDriver não encontrado
O webdriver-manager instala automaticamente. Se houver problemas:
```bash
pip install --upgrade webdriver-manager
```

### Timeout ao carregar página
Aumente o timeout em `wait_for_complete_loading()`:
```python
def wait_for_complete_loading(self, timeout=60):  # Aumentar para 60s
```

### Modal de CEP não detectado
Verifique se o site mudou a estrutura. O seletor atual é:
```python
By.NAME, "zipcode"
```

## 📝 Logs e Debug

- **Screenshots**: `debug_screenshot.png` (criado automaticamente)
- **Console output**: Logs detalhados de cada etapa
- **HTML size**: Verificação do tamanho do conteúdo carregado

## 🔧 Customização

### Alterar CEP padrão
```python
def handle_zipcode_modal(self, zipcode="SEU_CEP_AQUI"):
```

### Adicionar novos sites
Edite `data/sites.json` e adicione configurações:
```json
{
    "name": "Novo Produto",
    "url": "URL_DO_PRODUTO",
    "enabled": true
}
```

### Modificar seletores
O scraper busca automaticamente por:
- `aside[data-test='product-details-info']`
- Todas as tags `<p>` dentro do aside

## 📋 TODO / Melhorias Futuras

- [ ] Integração com banco de dados SQLite
- [ ] Sistema de notificações de preço
- [ ] Suporte a múltiplos CEPs
- [ ] Interface web para configuração
- [ ] Agendamento automático de scraping
- [ ] Exportação para CSV/Excel

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## ⚠️ Aviso Legal

Este scraper é destinado apenas para fins educacionais e de pesquisa. Respeite os termos de uso dos sites e as políticas de rate limiting. O uso responsável é essencial.

---

**Desenvolvido com ❤️ usando Python e Selenium**