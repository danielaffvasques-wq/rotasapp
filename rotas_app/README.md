# Aplicação de Otimização de Rotas para Entregas

App web para calcular e recomendar o percurso mais eficiente (em termos de tempo e custo) para motoristas ou entregas, com interface moderna e suporte para dark mode.

---

## 🚚 Funcionalidades
- Introduz vários endereços (2 ou mais, sem limite)
- Calcula todas as combinações possíveis para encontrar a ordem de entrega mais eficiente
- Mostra o resultado visualmente num mapa (Leaflet/OpenStreetMap)
- Permite alternar entre modo claro e escuro
- **Suporte a múltiplos idiomas: Português (PT) e Inglês (EN)** - selecionável no header
- Usa o Google Maps para geocodificação (com .env)
- Distância e tempo apresentados em km e minutos respetivamente

---

## ⚡ Instruções Rápidas

### 1. Instalar dependências
No terminal dentro da pasta `rotas_app`:
```bash
pip install -r requirements.txt
```

### 2. API Key do Google Maps
- Crie um ficheiro chamado `.env` nesta pasta (se não existir)
- Cole a sua chave:
```
GOOGLE_MAPS_API_KEY=coloque_aqui_a_sua_chave_google
```

> Para obter uma chave: aceda ao [Google Cloud Console](https://console.cloud.google.com/), ative a "Geocoding API" e crie uma API Key.

### 3. Iniciar a app
```bash
python app.py
```

### 4. Aceder via browser
Abra o endereço:
```
http://localhost:5000
```

### 5. Selecionar Idioma
- No header da aplicação, encontra-se um seletor de idioma (🇵🇹 PT / 🇬🇧 EN)
- A preferência de idioma é guardada automaticamente no browser
- Podes alternar entre Português e Inglês a qualquer momento

---

## 🛠️ Tecnologias Usadas
- **Python 3**
- **Flask** (backend web/API)
- **geopy & Google Maps** (para converter moradas em coordenadas)
- **Leaflet.js** (para o mapa interativo)
- HTML/CSS moderno

---

## ℹ️ Notas
- Se não tiver key da Google, a app usa OpenStreetMap (mas é menos preciso para moradas nacionais)
- O cálculo é feito para rotas com ida-e-volta por omissão (pode desligar "Voltar ao local de partida" na interface)
- Use sempre nomes de ruas e localidades correctos
- A app apenas mostra distâncias em km
- **Idiomas suportados:** Português (PT) e Inglês (EN) - a preferência é guardada no browser

---

## 💡 Usos Pessoais

Esta aplicação não é apenas para entregas profissionais. Pode ser usada pessoalmente para:

- Otimizar o percurso de várias tarefas num mesmo dia
- Planeamento de viagens ou passeios com múltiplos destinos
- Reduzir tempo e custos em deslocações diárias

Basta introduzir os endereços e a app calcula a sequência mais eficiente!

---

## 🚀 Próximas Funcionalidades

Na próxima release, planeio adicionar:

- Consideração de trânsito em tempo real para otimizar tempo de percurso
- Rotas com prioridades ou janelas de horário
- Exportação de rotas em PDF ou link direto para Google Maps
- Histórico e estatísticas pessoais de rotas
- Sugestão de paragens automáticas (cafés, postos de combustível, etc.)
- Integração com calendário pessoal para otimizar percursos diários
- Expansão do suporte a mais idiomas

---

## 📧 Contacto

Se tiveres dúvidas, sugestões ou encontrares algum bug, podes entrar em contacto:

**Email:** danielaffvasques@gmail.com

---

## 📄 Licença

Esta aplicação está licenciada sob a MIT License – ou seja, podes usar, modificar e distribuir livremente, desde que mantenhas os créditos ao autor.





