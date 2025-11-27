# SuperPy - Wurm Online Trade Analyzer

Analisador avançado de dados de trade do Wurm Online com Machine Learning e estatísticas otimizadas.

## 🚀 Características

- **Carregamento Inteligente**: Sistema de cache automático (Parquet/Pickle) para carregamento instantâneo
- **Análise ML**: Detecção de anomalias de preço usando Z-Score
- **Estatísticas Avançadas**: Análise de volatilidade, risco e tendências
- **Interface Moderna**: GUI responsiva com CustomTkinter
- **Processamento Assíncrono**: UI nunca trava durante operações pesadas
- **Visualizações**: Gráficos de preço, volume e atividade

## 📋 Requisitos

### Executável (Recomendado)
- Windows 10/11
- Nenhuma instalação adicional necessária

### Executar do Código-Fonte
- Python 3.10 ou superior
- Dependências listadas em `requirements.txt`

## 🔧 Instalação

### Opção 1: Usar Executável (Mais Fácil)
1. Baixe `SuperPy.exe` da pasta `dist/`
2. Execute o arquivo
3. Pronto! 🎉

### Opção 2: Executar do Código-Fonte
```bash
# Clone ou baixe o repositório
cd "Torta app"

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python superpy_app.py
```

## 📖 Como Usar

### 1. Carregar Dados
- Clique em **"Config"** → **"Selecionar Arquivo de Dados"**
- Escolha o arquivo `.txt` com os dados de trade
- Aguarde o carregamento (primeira vez é mais lenta, depois usa cache)

### 2. Buscar Itens
- **Busca Simples**: Digite o nome do item e clique em "Buscar"
- **Busca Avançada**: Use filtros por operação (WTS/WTB), data, preço, etc.

### 3. Ver Estatísticas
- Clique em **"Estatísticas"**
- Clique em **"Atualizar Estatísticas"**
- Veja resumo, top itens e análise de risco

### 4. Gerar Insights de ML
- Clique em **"Insights" (🔮)**
- Clique em **"Gerar Insights"**
- Veja oportunidades de compra/venda detectadas automaticamente

### 5. Visualizar Gráficos
- Clique em **"Gráficos"**
- Selecione um item da lista
- Escolha o tipo de gráfico (Preço ou Volume)
- Clique em **"Gerar Gráfico"**

## 🗂️ Estrutura de Arquivos

```
Torta app/
├── superpy_app.py          # Aplicativo principal (GUI)
├── wurm_stats_engine.py    # Motor de estatísticas (Pandas)
├── ml_predictor.py         # Preditor de ML (Z-Score)
├── wurm_parser.py          # Parser com cache inteligente
├── threading_utils.py      # Utilitários de threading
├── requirements.txt        # Dependências Python
├── build_exe.py           # Script de build (PyInstaller)
├── README.md              # Este arquivo
└── data/                  # Cache e dados (criado automaticamente)
    ├── trade_data_cache.parquet  # Cache rápido
    └── trade_data_cache.pkl      # Cache fallback
```

## 🛠️ Desenvolvimento

### Construir Executável
```bash
# Instale PyInstaller
pip install pyinstaller

# Execute o script de build
python build_exe.py

# Executável estará em: dist/SuperPy.exe
```

### Executar Testes
```bash
# Instale dependências de teste
pip install pytest pytest-cov

# Execute testes
pytest tests/

# Com cobertura
pytest --cov=. tests/
```

## 🐛 Solução de Problemas

### "Erro ao carregar dados"
- Verifique se o arquivo está no formato correto (JSON Lines)
- Tente deletar a pasta `data/` para forçar reconstrução do cache

### "UI travando"
- Isso não deveria acontecer! Reporte o bug com detalhes da operação

### "Gráfico não aparece"
- Verifique se há dados suficientes para o item selecionado
- Tente outro item com mais transações

### "Cache desatualizado"
- Delete os arquivos em `data/` para forçar rebuild
- Ou use a opção "Recarregar" (se disponível)

## 📊 Formato de Dados

O aplicativo espera arquivos `.txt` no formato JSON Lines:
```json
{"timestamp": "2025-01-01 12:00:00", "main_item": "iron lump", "price_s": 50, "operation": "WTS", ...}
{"timestamp": "2025-01-01 12:05:00", "main_item": "silver lump", "price_s": 100, "operation": "WTB", ...}
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é de código aberto. Use livremente!

## 🙏 Agradecimentos

- Comunidade Wurm Online
- Desenvolvedores de Pandas, Matplotlib e CustomTkinter
- Todos os contribuidores

---

**Desenvolvido com ❤️ para a comunidade Wurm Online**
