#!/usr/bin/env python3
"""
Script de execução do scraper com Selenium (aguarda JavaScript)
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from selenium_scraper import main

if __name__ == "__main__":
    main()