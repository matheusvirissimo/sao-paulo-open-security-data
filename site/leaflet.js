// Variáveis globais
let dadosCriminais = [];
let estatisticas = null;
let map;
let markersLayer;
let allMarkers = [];

// Cores por categoria
const crimeColors = {
    'Crimes Violentos': '#d63031',
    'Crimes Patrimoniais': '#e17055',
    'Crimes de Trânsito': '#0984e3',
    'Crimes Diversos': '#6c5ce7',
    'default': '#2d3436'
};

// INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Iniciando aplicação de Criminalidade SP...');
    console.log('URL atual:', window.location.href);
    
    const success = await loadData();
    
    if (success && dadosCriminais && dadosCriminais.length > 0) {
        console.log('Dados carregados com sucesso');
        initMap();
        setupEventListeners();
        hideLoading();
    } else {
        console.error('Falha ao carregar dados');
        hideLoading();
    }
});

// CARREGAR DADOS
async function loadData() {
    try {
        console.log('Carregando dados criminais...');
        
        // Carregar dados principais (sample por padrão para melhor performance)
        const dataResponse = await fetch('dados_criminais_sample.json');
        console.log('Response status:', dataResponse.status);
        
        if (!dataResponse.ok) {
            throw new Error(`HTTP error! status: ${dataResponse.status}`);
        }
        
        const dataText = await dataResponse.text();
        console.log('Dados recebidos, tamanho:', dataText.length);
        
        dadosCriminais = JSON.parse(dataText);
        console.log(`${dadosCriminais.length} crimes carregados`);
        
        if (!Array.isArray(dadosCriminais) || dadosCriminais.length === 0) {
            throw new Error('Dados inválidos ou vazios');
        }
        
        // Carregar estatísticas
        try {
            const statsResponse = await fetch('estatisticas.json');
            if (statsResponse.ok) {
                estatisticas = await statsResponse.json();
                console.log('Estatísticas carregadas');
            }
        } catch (e) {
            console.warn('Estatísticas não disponíveis:', e);
        }
        
        return true;
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        showError(error.message);
        return false;
    }
}


// INICIALIZAR MAPA - LEAFLET 
function initMap() {
    if (!dadosCriminais || dadosCriminais.length === 0) {
        console.error('Nenhum dado para exibir');
        return;
    }
    
    console.log('Inicializando mapa...');
    
    // Criar mapa centrado em São Paulo
    map = L.map('map').setView([-23.5505, -46.6333], 11);
    
    // Adicionar tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Criar camada de clusters
    markersLayer = L.markerClusterGroup({
        chunkedLoading: true,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        maxClusterRadius: 60
    });
    
    // Renderizar marcadores
    renderMarkers(dadosCriminais);
    
    // Atualizar interface
    updateStats(dadosCriminais);
    populateFilters();
    updateRankings(dadosCriminais);
    
    // Ajustar zoom para mostrar todos os pontos
    if (dadosCriminais.length > 0) {
        const bounds = L.latLngBounds(dadosCriminais.map(d => [d.lat, d.lng]));
        map.fitBounds(bounds, { padding: [50, 50] });
    }
    
    console.log('✓ Mapa inicializado');
}

// RENDERIZAR MARCADORES
function renderMarkers(dados) {
    markersLayer.clearLayers();
    allMarkers = [];
    
    dados.forEach(crime => {
        const marker = L.marker([crime.lat, crime.lng], {
            icon: createMarkerIcon(crime.categoria_crime)
        });
        
        marker.bindPopup(createPopupContent(crime), {
            maxWidth: 350,
            className: 'crime-popup'
        });
        
        marker.crimeData = crime;
        allMarkers.push(marker);
        markersLayer.addLayer(marker);
    });
    
    map.addLayer(markersLayer);
}

// CRIAR ÍCONE DO MARCADOR
function createMarkerIcon(categoria) {
    const color = crimeColors[categoria] || crimeColors['default'];
    
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${color};
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 4px rgba(0,0,0,0.5);
        "></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
    });
}


// CRIAR CONTEÚDO DO POPUP
function createPopupContent(crime) {
    let html = '<div class="popup-content">';
    
    // Título
    html += `<h4>${crime.tipo_crime || crime.rubrica || 'Ocorrência Criminal'}</h4>`;
    
    // Categoria
    if (crime.categoria_crime) {
        html += `<p><strong>Categoria:</strong> ${crime.categoria_crime}</p>`;
    }
    
    // Localização
    html += '<div>';
    if (crime.municipio) {
        html += `<p><strong>📍 Município:</strong> ${crime.municipio}</p>`;
    }
    if (crime.bairro && crime.bairro !== '') {
        html += `<p><strong>Bairro:</strong> ${crime.bairro}</p>`;
    }
    if (crime.logradouro && !crime.logradouro.includes('VEDAÇÃO')) {
        html += `<p><strong>Local:</strong> ${crime.logradouro}`;
        if (crime.numero_logradouro) html += `, ${crime.numero_logradouro}`;
        html += `</p>`;
    }
    if (crime.descr_subtipolocal && crime.descr_subtipolocal !== '') {
        html += `<p><strong>Tipo:</strong> ${crime.descr_subtipolocal}</p>`;
    }
    html += '</div>';
    
    // Data e Hora
    html += '<div>';
    if (crime.data_ocorrencia) {
        html += `<p><strong>🕐 Data:</strong> ${formatDate(crime.data_ocorrencia)}`;
        if (crime.dia_semana) html += ` (${crime.dia_semana})`;
        html += `</p>`;
    }
    if (crime.hora_ocorrencia && crime.hora_ocorrencia !== '') {
        html += `<p><strong>Hora:</strong> ${crime.hora_ocorrencia}`;
        if (crime.desc_periodo) html += ` - ${crime.desc_periodo}`;
        html += `</p>`;
    }
    html += '</div>';
    
    // Delegacia
    if (crime.delegacia || crime.num_bo) {
        html += '<div>';
        if (crime.delegacia) {
            html += `<p><strong>🏛️ Delegacia:</strong> ${crime.delegacia}</p>`;
        }
        if (crime.num_bo) {
            html += `<p><strong>BO:</strong> ${crime.num_bo}/${crime.ano || ''}</p>`;
        }
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

// ATUALIZAR ESTATÍSTICAS
function updateStats(dados) {
    const total = estatisticas ? estatisticas.total_crimes : dados.length;
    const filtered = dados.length;
    
    document.getElementById('totalCrimes').textContent = total.toLocaleString('pt-BR');
    document.getElementById('filteredCrimes').textContent = filtered.toLocaleString('pt-BR');
}


// POPULAR FILTROS
function populateFilters() {
    // Filtro de crimes
    const tiposCrime = [...new Set(dadosCriminais.map(c => c.tipo_crime || c.rubrica))].filter(Boolean).sort();
    const crimeSelect = document.getElementById('crimeFilter');
    
    tiposCrime.forEach(tipo => {
        const option = document.createElement('option');
        option.value = tipo;
        option.textContent = tipo;
        crimeSelect.appendChild(option);
    });
    
    // Filtro de municípios
    const municipios = [...new Set(dadosCriminais.map(c => c.municipio))].filter(Boolean).sort();
    const municipioSelect = document.getElementById('municipioFilter');
    
    municipios.forEach(mun => {
        const option = document.createElement('option');
        option.value = mun;
        option.textContent = mun;
        municipioSelect.appendChild(option);
    });
}


// ATUALIZAR RANKINGS
function updateRankings(dados) {
    // Top Crimes
    const crimeCounts = {};
    dados.forEach(d => {
        const crime = d.tipo_crime || d.rubrica;
        if (crime) {
            crimeCounts[crime] = (crimeCounts[crime] || 0) + 1;
        }
    });
    
    const topCrimes = Object.entries(crimeCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    const topCrimesHtml = topCrimes.map((item, index) => `
        <div class="ranking-item">
            <div class="ranking-position">${index + 1}º</div>
            <div class="ranking-label">${item[0]}</div>
            <div class="ranking-count">${item[1].toLocaleString('pt-BR')}</div>
        </div>
    `).join('');
    
    document.getElementById('topCrimes').innerHTML = topCrimesHtml || '<p class="loading-text">Sem dados</p>';
    
    // Top Municípios
    const municipioCounts = {};
    dados.forEach(d => {
        if (d.municipio) {
            municipioCounts[d.municipio] = (municipioCounts[d.municipio] || 0) + 1;
        }
    });
    
    const topMunicipios = Object.entries(municipioCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    const topMunicipiosHtml = topMunicipios.map((item, index) => `
        <div class="ranking-item">
            <div class="ranking-position">${index + 1}º</div>
            <div class="ranking-label">${item[0]}</div>
            <div class="ranking-count">${item[1].toLocaleString('pt-BR')}</div>
        </div>
    `).join('');
    
    document.getElementById('topMunicipios').innerHTML = topMunicipiosHtml || '<p class="loading-text">Sem dados</p>';
}


// FILTRAR DADOS
function filterData() {
    const crimeFilter = document.getElementById('crimeFilter').value;
    const municipioFilter = document.getElementById('municipioFilter').value;
    
    let filtered = dadosCriminais;
    
    if (crimeFilter !== 'todos') {
        filtered = filtered.filter(c => 
            (c.tipo_crime || c.rubrica) === crimeFilter
        );
    }
    
    if (municipioFilter !== 'todos') {
        filtered = filtered.filter(c => c.municipio === municipioFilter);
    }
    
    renderMarkers(filtered);
    updateStats(filtered);
    updateRankings(filtered);
}


// RESETAR FILTROS
function resetFilters() {
    document.getElementById('crimeFilter').value = 'todos';
    document.getElementById('municipioFilter').value = 'todos';
    
    renderMarkers(dadosCriminais);
    updateStats(dadosCriminais);
    updateRankings(dadosCriminais);
}


// SETUP EVENT LISTENERS
function setupEventListeners() {
    document.getElementById('crimeFilter').addEventListener('change', filterData);
    document.getElementById('municipioFilter').addEventListener('change', filterData);
    document.getElementById('resetBtn').addEventListener('click', resetFilters);
}


// UTILITÁRIOS
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function hideLoading() {
    const loading = document.getElementById('loading-screen');
    if (loading) {
        loading.classList.add('hidden');
        setTimeout(() => loading.remove(), 500);
    }
}

function showError(message = 'Os arquivos de dados não foram encontrados.') {
    hideLoading();
    const errorHtml = `
        <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
             background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
             text-align: center; max-width: 500px; z-index: 10000;">
            <h2 style="color: #d63031; margin-bottom: 20px;">⚠️ Erro ao Carregar Dados</h2>
            <p style="margin-bottom: 20px;">${message}</p>
            <p style="font-size: 14px; color: #636e72; margin-bottom: 10px;">
                Execute o notebook <strong>5_exportar_para_web.ipynb</strong> para gerar os dados.
            </p>
            <p style="font-size: 12px; color: #636e72;">
                Abra o Console do navegador (F12) para mais detalhes.
            </p>
            <button onclick="location.reload()" style="margin-top: 20px; padding: 12px 24px; 
                   background: #d63031; color: white; border: none; border-radius: 6px; 
                   cursor: pointer; font-weight: 600;">
                Tentar Novamente
            </button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', errorHtml);
}

// Log inicial
console.log('Aplicação de Criminalidade SP carregada');
