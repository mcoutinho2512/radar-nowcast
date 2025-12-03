# 🌧️ Radar Nowcast - COR Rio

Sistema de visualização de radar meteorológico com detecção de tendência de deslocamento dos núcleos de chuva.

## Funcionalidades

- 📡 **Multi-radar**: Suporte para Sumaré, Mendanha e INEA
- 🗺️ **Mapa interativo**: Leaflet com limites do município do Rio de Janeiro
- ➤ **Setas de tendência**: Mostra direção de deslocamento dos núcleos
- 📊 **Análise em tempo real**: Detecção automática de núcleos e cálculo de velocidade
- 🔄 **Conexão FTP**: Sincronização automática com servidor de imagens

## Estrutura

```
radar-nowcast-v2/
├── index.html      # Frontend (Leaflet + JavaScript)
├── server.py       # Backend Python (Flask + FTP)
├── requirements.txt
├── cache/          # Cache de imagens (criado automaticamente)
│   ├── sumare/
│   ├── mendanha/
│   └── inea/
└── README.md
```

## Instalação

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor backend

```bash
python server.py
```

O servidor estará disponível em `http://localhost:5000`

### 3. Abrir o frontend

Abra `index.html` em um navegador ou sirva via servidor web:

```bash
# Opção 1: Python
python -m http.server 8080

# Opção 2: Node.js
npx serve .
```

Acesse `http://localhost:8080`

## Configuração do FTP

### Dados necessários

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| Servidor | Host do FTP | `ftp.alertario.rio.rj.gov.br` |
| Usuário | Login | `usuario_cor` |
| Senha | Password | `********` |
| Diretório | Caminho das imagens | `/radar/sumare/` |

### Estrutura esperada das imagens

O sistema espera imagens PNG com nomenclatura baseada em timestamp:

```
radar_sumare_202412031000.png
radar_sumare_202412031002.png
radar_sumare_202412031004.png
...
```

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/radars` | Lista radares disponíveis |
| GET | `/api/frames/<radar>` | Lista frames em cache |
| GET | `/api/frame/<radar>/<file>` | Retorna imagem |
| POST | `/api/ftp/connect` | Conecta ao FTP |
| GET | `/api/ftp/sync/<radar>` | Sincroniza imagens |
| GET | `/api/status` | Status do servidor |

### Exemplo de conexão FTP via API

```javascript
fetch('http://localhost:5000/api/ftp/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        host: 'ftp.alertario.rio.rj.gov.br',
        user: 'usuario',
        password: 'senha'
    })
});
```

## Configuração dos Radares

Edite o dicionário `RADARS` em `server.py` para ajustar:

```python
RADARS = {
    'sumare': {
        'name': 'Sumaré',
        'lat': -22.9519,
        'lng': -43.1731,
        'range': 250,  # km
        'ftp_path': '/radar/sumare/',
        'file_pattern': 'radar_sumare_%Y%m%d%H%M.png'
    },
    # ... outros radares
}
```

## Ajuste dos Bounds da Imagem

Para sobrepor corretamente a imagem do radar no mapa, ajuste os bounds no frontend:

```javascript
const RADARS = {
    sumare: {
        // ...
        bounds: [
            [-24.5, -45.0],  // Canto SW [lat, lng]
            [-21.4, -41.3]   // Canto NE [lat, lng]
        ]
    }
};
```

## Integração com GeoJSON do Município

Para usar os limites oficiais do Rio de Janeiro:

1. Baixe o GeoJSON do IBGE: https://geoftp.ibge.gov.br/
2. Coloque em `geojson/rio_de_janeiro.geojson`
3. Atualize a função `loadMunicipalBoundary()` no `index.html`

## Algoritmo de Detecção de Núcleos

1. **Análise de cores**: Identifica pixels com cores do radar (verde → magenta)
2. **Clusterização**: Agrupa pixels adjacentes (flood fill)
3. **Centróide**: Calcula centro de massa de cada cluster
4. **Rastreamento**: Compara posições entre frames consecutivos
5. **Vetor de movimento**: Calcula direção e velocidade
6. **Projeção**: Estima posição futura (próximos 30 min)

## Próximos Passos

- [ ] Integrar com API real do Alerta Rio
- [ ] Adicionar WebSocket para atualizações em tempo real
- [ ] Implementar alertas por bairro
- [ ] Histórico de deslocamentos
- [ ] Machine learning para melhorar previsões

## Suporte

Centro de Operações Rio (COR)
Desenvolvido para monitoramento meteorológico municipal.

---

**Versão**: 2.0.0  
**Última atualização**: Dezembro 2024
