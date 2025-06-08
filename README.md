# Buscador de Bares e Restaurantes de BH

Este projeto é uma aplicação web interativa para visualização, busca e filtragem de bares e restaurantes de Belo Horizonte, utilizando dados públicos e informações do concurso Comida di Buteco.

## Funcionalidades

- **Mapa Interativo:** Visualize todos os bares/restaurantes em um mapa de Belo Horizonte usando [Dash](https://dash.plotly.com/) e [Dash Leaflet](https://dash-leaflet.herokuapp.com/).
- **Filtragem Geográfica:** Selecione uma área retangular no mapa para filtrar os estabelecimentos exibidos.
- **Tabela de Dados:** Veja informações detalhadas dos estabelecimentos filtrados em uma tabela.
- **Detalhes dos Bares:** Passe o mouse sobre um marcador para ver informações do bar, prato inscrito, descrição, endereço e imagem.
- **Busca eficiente:** Utiliza uma árvore KD (KdTree) para busca espacial eficiente dos pontos.

## Estrutura do Projeto
```text
├── map.py               # Aplicação principal Dash (frontend e backend)
├── tp.py                # Lógica de dados, estruturas e busca espacial
├── dados.csv            # Dados dos estabelecimentos (geolocalização, CNPJ, etc)
├── bares.csv            # Dados detalhados dos bares do Comida di Buteco
├── output.csv           # (opcional) Saídas processadas
├── scraper.ipynb        # Notebook para coleta/processamento de dados
├── relatorio-alg2.pdf   # Relatório do trabalho
├── assets/
│   └── custom.css       # Estilos customizados para o Dash
└── README.md            # Este arquivo
```

## Como Executar

1. **Pré-requisitos:**
   - Python 3.10+
   - Instale as dependências:
     ```sh
     pip install dash dash-leaflet numpy pyproj
     ```

2. **Arquivos de Dados:**
   - Certifique-se de que `dados.csv` e `bares.csv` estejam na raiz do projeto.

3. **Executando a aplicação:**
   ```sh
   python map.py

Acesse http://127.0.0.1:8050 no navegador.

## Explicação dos Principais Arquivos
- map.py: Inicializa o Dash, carrega os dados, define o layout do mapa, tabela e callbacks para filtragem.
- tp.py: Contém as classes Point, Rectangle, KdTree para busca espacial, além de funções para parsing dos CSVs.
- dados.csv: Lista de estabelecimentos com localização (projetada e convertida para latitude/longitude), nome, endereço, licença, etc.
- bares.csv: Informações detalhadas dos bares participantes do Comida di Buteco, incluindo prato, descrição, imagem e link.

## Como funciona a busca espacial?
A busca dos estabelecimentos dentro de uma área selecionada no mapa é feita usando uma árvore KD (KdTree), implementada em tp.py. Isso permite filtrar rapidamente apenas os pontos dentro do retângulo desenhado pelo usuário.

## Customização
Para alterar o estilo visual, edite custom.css.
Para adicionar novos dados, atualize os arquivos CSV conforme o formato existente.

## Créditos
- Dados do concurso: Comida di Buteco
- Projeto acadêmico para Algoritmos II - UFMG
- Autores: Bruno Buti Ferreira Guilherme e Ricardo Shen
