# 🥧 Torta App - Wurm Online Trade Analyzer

**Versão 2.0** | Análise avançada de trades do Wurm Online usando Pandas

---

## 📋 Descrição

Torta App é um analisador de trades do Wurm Online que oferece:
- ✅ **Interface moderna** com dark theme (CustomTkinter)
- ✅ **Análise estatística avançada** com Pandas
- ✅ **Gráficos interativos** (matplotlib)
- ✅ **Métricas de volatilidade** e médias móveis
- ✅ **Carregamento assíncrono** (não trava a UI)
- ✅ **Console de log** integrado
- ✅ **Sistema de plugins** extensível

---

## 🚀 Instalação

### Requisitos
- Python 3.8 ou superior

### Dependências
```bash
pip install pandas customtkinter matplotlib
```

---

## 💻 Uso

### Iniciar o App
```bash
python superpy_app.py
```

### Carregar Dados
1. Clique na aba **Config**
2. Selecione o arquivo de dados Wurm (`.txt` em formato JSON Lines)
3. Clique em **Aplicar e recarregar**

### Gerar Gráficos
1. Vá na aba **Gráficos**
2. Digite o nome do item
3. Escolha: `Price History` ou `Volume/Activity`
4. Clique em **Gerar Gráfico**

---

## 📊 Features

### Análise Estatística
- **Volatilidade de Preço**: Detecta variação de preços
- **Médias Móveis**: Identifica tendências
- **Top Itens**: Ranking dos mais negociados
- **Exportar CSV**: Salvar dados para Excel

### Interface
- Dark theme profissional
- Console de log com timestamp
- Gráficos embutidos (zoom/pan)
- Tutorial integrado (aba Ajuda)

---

## 🗂️ Estrutura

```
Torta app/
├── superpy_app.py          # GUI principal
├── wurm_stats_engine.py    # Motor Pandas
├── threading_utils.py      # AsyncDataLoader
├── app_icon.png            # Ícone
└── plugins/                # Plugins customizados
```

---

## 📜 Changelog

### v2.0 (2025-11-26)
- ✅ CustomTkinter dark theme
- ✅ Análise de volatilidade/médias móveis
- ✅ Tutorial integrado
- ✅ Console de log
- ✅ Otimização de memória

### v1.0 (2025-11-26)
- ✅ Motor Pandas
- ✅ Gráficos matplotlib
- ✅ Busca avançada

---

## 👤 Autor

**Jotasiete7**  
GitHub: [tortaapp](https://github.com/Jotasiete7/tortaapp)

---

**Divirta-se analisando! 🥧📈**
