// map.js - Interactive Metro Map
let map;
let stationsData = [];
let linesData = [];
let markers = [];
let polylines = [];
let routeLayer = null;

const lineColors = {
  'L1': '#E2001A',
  'L2': '#A93DB9',
  'L3': '#00843D',
  'L4': '#F9B000',
  'L5': '#005BA9',
  'L6': '#683F99',
  'L7': '#C1A961',
  'L8': '#E85C98',
  'L9': '#F36F21',
  'L10': '#009CDD',
  'L11': '#A5CE39',
  'L12': '#9CA299'
};

function initMap() {
  map = L.map('map').setView([41.3851, 2.1734], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18,
    minZoom: 10
  }).addTo(map);

  loadMapData();
}

async function loadMapData() {
  try {
    const [stationsResp, linesResp] = await Promise.all([
      fetch('/api/stations'),
      fetch('/api/lines')
    ]);

    if (!stationsResp.ok || !linesResp.ok) {
      throw new Error('Error al cargar datos');
    }

    stationsData = await stationsResp.json();
    linesData = await linesResp.json();

    populateStationSelects();
    await renderLines();
    renderStations();

    document.getElementById('loading').style.display = 'none';

    if (markers.length > 0) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

    addLegend();
  } catch (error) {
    console.error('Error loading map data:', error);
    showError(error.message);
  }
}

function formatLineCode(lineCode) {
  const numCode = parseInt(lineCode);
  if (numCode >= 1 && numCode <= 11) {
    return `L${lineCode}`;
  } else if (lineCode === '91') {
    return 'L9 S';
  } else if (lineCode === '94') {
    return 'L9 N';
  } else if (lineCode === '101') {
    return 'L10 S';
  } else if (lineCode === '104') {
    return 'L10 N';
  } else if (lineCode === '99') {
    return 'FM';
  } else {
    return lineCode;
  }
}

function renderStations() {
  stationsData.forEach(station => {
    if (!station.latitude || !station.longitude) return;

    const isInterchange = station.lines && station.lines.length > 1;
    
    const icon = L.divIcon({
      className: 'station-marker' + (isInterchange ? ' interchange' : ''),
      iconSize: isInterchange ? [16, 16] : [12, 12],
      iconAnchor: isInterchange ? [8, 8] : [6, 6]
    });

    const marker = L.marker([station.latitude, station.longitude], { icon })
      .addTo(map);

    marker.on('click', () => showStationDetails(station));
    markers.push(marker);
  });
}

async function renderLines() {
  try {
    const resp = await fetch('/api/line-geometries');
    const lineGeometries = await resp.json();

    lineGeometries.forEach(lineData => {
      if (!lineData.coordinates || lineData.coordinates.length < 2) return;

      const coords = lineData.coordinates.map(coord => [coord.lat, coord.lng]);

      const polyline = L.polyline(coords, {
        color: lineData.color,
        weight: 4,
        opacity: 0.7,
        smoothFactor: 1
      }).addTo(map);

      polyline.on('click', () => showLineDetails(lineData.code));
      polylines.push(polyline);
    });
    
    console.log(`✅ ${lineGeometries.length} líneas renderizadas`);
  } catch (error) {
    console.error('Error renderizando líneas:', error);
  }
}

async function showStationDetails(station) {
  try {
    const stationId = encodeURIComponent(station.id);
    const resp = await fetch(`/api/station/${stationId}`);
    const details = await resp.json();

    const linesHTML = details.lines.map(lineCode => {
      const lineInfo = linesData.find(l => l.code === lineCode);
      const color = lineInfo?.color || lineColors[lineCode] || '#999';
      const displayCode = formatLineCode(lineCode);
      return `<span class="line-badge" style="background-color: ${color}">${displayCode}</span>`;
    }).join('');

    const popupContent = `
      <div class="station-popup">
        <h3>🚉 ${details.name}</h3>
        <div class="station-lines">
          <strong>Líneas:</strong><br>
          ${linesHTML}
        </div>
        <div class="station-info">
          ${details.inaugurated ? `<p><strong>Inauguración:</strong> ${formatDate(details.inaugurated)}</p>` : ''}
          <p><strong>Coordenadas:</strong> ${details.latitude.toFixed(4)}, ${details.longitude.toFixed(4)}</p>
          <p><strong>Tipo:</strong> ${details.lines.length > 1 ? 'Estación de intercambio' : 'Estación regular'}</p>
        </div>
      </div>
    `;

    L.popup()
      .setLatLng([details.latitude, details.longitude])
      .setContent(popupContent)
      .openOn(map);
  } catch (error) {
    console.error('Error loading station details:', error);
    alert('Error al cargar detalles de la estación');
  }
}

async function showLineDetails(lineCode) {
  try {
    const resp = await fetch(`/api/line/${lineCode}`);
    const details = await resp.json();

    const color = details.color || lineColors[lineCode] || '#999';

    const stationsListHTML = details.stations
      .sort((a, b) => a.order - b.order)
      .map(s => `<li>${s.name}</li>`)
      .join('');

    const displayCode = formatLineCode(lineCode);
    
    const popupContent = `
      <div class="line-popup">
        <h3>
          <span class="line-badge" style="background-color: ${color}">${displayCode}</span>
          ${details.origin && details.destination ? 
            `${details.origin} ↔ ${details.destination}` : 
            'Línea de Metro'}
        </h3>
        <div class="line-stats">
          <p><strong>🚉 Número de paradas:</strong> ${details.numStations}</p>
          ${details.origin ? `<p><strong>📍 Origen:</strong> ${details.origin}</p>` : ''}
          ${details.destination ? `<p><strong>🎯 Destino:</strong> ${details.destination}</p>` : ''}
        </div>
        ${details.stations.length > 0 ? `
          <details>
            <summary><strong>Ver todas las paradas</strong></summary>
            <div class="stations-list">
              <ol>${stationsListHTML}</ol>
            </div>
          </details>
        ` : ''}
      </div>
    `;

    const lineStations = stationsData.filter(s => 
      s.lines && s.lines.includes(lineCode) && s.latitude && s.longitude
    );
    
    if (lineStations.length > 0) {
      const centerLat = lineStations.reduce((sum, s) => sum + s.latitude, 0) / lineStations.length;
      const centerLng = lineStations.reduce((sum, s) => sum + s.longitude, 0) / lineStations.length;

      L.popup()
        .setLatLng([centerLat, centerLng])
        .setContent(popupContent)
        .openOn(map);
    }
  } catch (error) {
    console.error('Error loading line details:', error);
    alert('Error al cargar detalles de la línea');
  }
}

function addLegend() {
  const legendDiv = document.createElement('div');
  legendDiv.className = 'legend';
  
  let legendHTML = '<h4>📍 Leyenda</h4>';
  
  legendHTML += `
    <div class="legend-item">
      <div class="legend-marker" style="background: white; border-color: #667eea;"></div>
      <span>Estación regular</span>
    </div>
    <div class="legend-item">
      <div class="legend-marker" style="background: white; border-color: #ff5722; width: 14px; height: 14px;"></div>
      <span>Estación de intercambio</span>
    </div>
  `;

  if (linesData.length > 0) {
    legendHTML += '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;"></div>';
    linesData.forEach(line => {
      const color = line.color || lineColors[line.code] || '#999';
      const displayCode = formatLineCode(line.code);
      legendHTML += `
        <div class="legend-item">
          <div class="legend-color" style="background-color: ${color}"></div>
          <span>${displayCode}</span>
        </div>
      `;
    });
  }

  legendDiv.innerHTML = legendHTML;
  document.getElementById('map-container').appendChild(legendDiv);
}

function showError(message) {
  document.getElementById('loading').style.display = 'none';
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.innerHTML = `
    <h3>❌ Error</h3>
    <p>${message}</p>
    <p>Asegúrate de que:</p>
    <ul style="text-align: left; margin: 10px 0;">
      <li>Apache Jena Fuseki esté corriendo</li>
      <li>Los datos estén cargados</li>
      <li>El backend esté funcionando</li>
    </ul>
    <button class="btn btn-light" onclick="location.reload()">🔄 Reintentar</button>
  `;
  
  document.getElementById('map-container').appendChild(errorDiv);
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch {
    return dateString;
  }
}

function populateStationSelects() {
  const originSelect = document.getElementById('origin-select');
  const destSelect = document.getElementById('destination-select');
  
  const uniqueStations = new Map();
  stationsData.forEach(station => {
    if (!uniqueStations.has(station.name)) {
      uniqueStations.set(station.name, station);
    }
  });
  
  const sortedStations = Array.from(uniqueStations.values()).sort((a, b) => 
    a.name.localeCompare(b.name)
  );
  
  sortedStations.forEach(station => {
    const option1 = document.createElement('option');
    option1.value = station.name;
    option1.textContent = station.name;
    originSelect.appendChild(option1);
    
    const option2 = document.createElement('option');
    option2.value = station.name;
    option2.textContent = station.name;
    destSelect.appendChild(option2);
  });
}

function checkRouteInputs() {
  const origin = document.getElementById('origin-select').value;
  const dest = document.getElementById('destination-select').value;
  const btn = document.getElementById('find-route-btn');
  
  btn.disabled = !origin || !dest || origin === dest;
}

async function findRoute() {
  const originName = document.getElementById('origin-select').value;
  const destName = document.getElementById('destination-select').value;
  const resultDiv = document.getElementById('route-result');
  
  if (!originName || !destName) {
    resultDiv.innerHTML = '<p style="color: #c62828;">Selecciona origen y destino</p>';
    return;
  }
  
  if (originName === destName) {
    resultDiv.innerHTML = '<p style="color: #c62828;">El origen y destino son la misma estación</p>';
    return;
  }
  
  resultDiv.innerHTML = '<p>🔍 Buscando ruta...</p>';
  
  try {
    const resp = await fetch(`/api/route?origin=${encodeURIComponent(originName)}&destination=${encodeURIComponent(destName)}`);
    const data = await resp.json();
    
    if (!data.found) {
      resultDiv.innerHTML = `<p style="color: #c62828;">${data.error || 'No se encontró ruta entre estas estaciones'}</p>`;
      return;
    }
    
    displayRoute(data);
    drawRouteOnMap(data);
  } catch (error) {
    console.error('Error finding route:', error);
    resultDiv.innerHTML = '<p style="color: #c62828;">Error al buscar ruta</p>';
  }
}

function displayRoute(routeData) {
  const resultDiv = document.getElementById('route-result');
  
  const uniqueLines = [...new Set(routeData.lines)];
  const duration = calculateEstimatedDuration(routeData);
  
  let html = '<h4 style="color: #333; margin: 0 0 10px; font-size: 14px;">✅ Ruta Encontrada</h4>';
  
  html += '<div class="route-summary">';
  html += `<p><strong>🚉 Total estaciones:</strong> ${routeData.num_stations}</p>`;
  html += `<p><strong>🚇 Líneas utilizadas:</strong> ${uniqueLines.map(c => formatLineCode(c)).join(', ')}</p>`;
  html += `<p><strong>🔄 Transbordos:</strong> ${routeData.num_transfers}</p>`;
  html += `<p><strong>⏱️ Tiempo estimado:</strong> ${duration} min</p>`;
  html += '</div>';
  
  html += '<div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #eee;">';
  html += '<h4 style="font-size: 13px; margin-bottom: 10px; color: #333;">📋 Instrucciones:</h4>';
  html += '<ol style="padding-left: 20px; margin: 0; list-style: decimal;">';
  
  for (let i = 0; i < routeData.stations.length; i++) {
    const station = routeData.stations[i];
    const lineCode = routeData.lines[i - 1];
    
    if (i === 0) {
      const firstLineCode = formatLineCode(routeData.lines[0]);
      html += `<li style="margin-bottom: 8px; padding: 8px; background: #f9f9f9; border-radius: 4px;">`;
      html += `<strong>Origen en ${station.name}</strong><br>`;
      html += `<small>Toma la línea ${firstLineCode}</small>`;
      html += `</li>`;
    } else if (i === routeData.stations.length - 1) {
      html += `<li style="margin-bottom: 8px; padding: 8px; background: #f9f9f9; border-radius: 4px;">`;
      html += `<strong>Destino: ${station.name}</strong>`;
      html += `</li>`;
    } else {
      const nextLineCode = routeData.lines[i];
      const isTransfer = lineCode !== nextLineCode;
      
      if (isTransfer) {
        const fromLine = formatLineCode(lineCode);
        const toLine = formatLineCode(nextLineCode);
        html += `<li style="margin-bottom: 8px; padding: 8px; background: #fff3e0; border-radius: 4px;">`;
        html += `<strong>🔄 Transbordo en ${station.name}</strong><br>`;
        html += `<small>Cambia de ${fromLine} a ${toLine}</small>`;
        html += `</li>`;
      } else {
        html += `<li style="margin-bottom: 8px; padding: 8px; background: #f9f9f9; border-radius: 4px;">`;
        html += `Pasa por ${station.name}`;
        html += `</li>`;
      }
    }
  }
  
  html += '</ol>';
  html += '</div>';
  
  if (routeData.transfers && routeData.transfers.length > 0) {
    html += '<div style="margin-top: 15px; padding: 10px; background: #fff3e0; border-radius: 6px;">';
    html += '<strong style="color: #f57c00;">⚠️ Transbordos necesarios:</strong>';
    html += '<ul style="margin: 5px 0 0 20px; font-size: 12px;">';
    routeData.transfers.forEach(transfer => {
      html += `<li>${transfer.station}: ${formatLineCode(transfer.from_line)} → ${formatLineCode(transfer.to_line)}</li>`;
    });
    html += '</ul>';
    html += '</div>';
  }
  
  html += '<button class="clear-route" onclick="clearRoute()" style="margin-top: 15px; width: 100%; padding: 8px; background: #f5f5f5; color: #666; border: 1px solid #ddd; border-radius: 6px; cursor: pointer;">🔄 Nueva Búsqueda</button>';
  
  resultDiv.innerHTML = html;
}

function calculateEstimatedDuration(routeData) {
  const stationTime = (routeData.num_stations - 1) * 2;
  const transferTime = routeData.num_transfers * 3;
  return stationTime + transferTime;
}

function drawRouteOnMap(routeData) {
  clearRoute();
  
  routeLayer = L.featureGroup().addTo(map);
  
  if (routeData.segments && routeData.segments.length > 0) {
    routeData.segments.forEach(segment => {
      const lineCode = segment.line_code;
      const lineInfo = linesData.find(l => l.code === lineCode);
      const lineColor = lineInfo?.color || '#FF0000';
      
      const fromStation = stationsData.find(s => s.name === segment.from_station);
      const toStation = stationsData.find(s => s.name === segment.to_station);
      
      if (fromStation && toStation) {
        L.polyline(
          [[fromStation.latitude, fromStation.longitude],
           [toStation.latitude, toStation.longitude]], {
          color: lineColor,
          weight: 8,
          opacity: 0.9,
          className: 'route-segment'
        }).addTo(routeLayer);
      }
    });
  }
  
  const allRoutePoints = [];
  
  routeData.stations.forEach((station, index) => {
    const stationData = stationsData.find(s => s.name === station.name);
    
    if (stationData) {
      allRoutePoints.push([stationData.latitude, stationData.longitude]);
      
      const isStart = index === 0;
      const isEnd = index === routeData.stations.length - 1;
      
      const icon = L.divIcon({
        className: 'route-marker',
        html: `<div style="
          background: ${isStart ? '#00FF00' : isEnd ? '#FF0000' : '#FFA500'};
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 3px 8px rgba(0,0,0,0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 11px;
          z-index: 1000;
        ">${isStart ? '▶' : isEnd ? '■' : index}</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });
      
      const marker = L.marker([stationData.latitude, stationData.longitude], { icon })
        .bindPopup(`<strong>${station.name}</strong><br>${isStart ? '🚩 Origen' : isEnd ? '🏁 Destino' : '🚉 Parada ' + index}`)
        .addTo(routeLayer);
      
      if (isStart) {
        marker.openPopup();
      }
    }
  });
  
  if (allRoutePoints.length > 0) {
    const bounds = L.latLngBounds(allRoutePoints);
    map.fitBounds(bounds.pad(0.15));
  }
}

function clearRoute() {
  if (routeLayer) {
    map.removeLayer(routeLayer);
    routeLayer = null;
  }
  document.getElementById('route-result').innerHTML = '';
  document.getElementById('origin-select').value = '';
  document.getElementById('destination-select').value = '';
  document.getElementById('find-route-btn').disabled = true;
}

document.getElementById('refresh-btn').addEventListener('click', () => {
  location.reload();
});

document.getElementById('origin-select').addEventListener('change', checkRouteInputs);
document.getElementById('destination-select').addEventListener('change', checkRouteInputs);
document.getElementById('find-route-btn').addEventListener('click', findRoute);

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMap);
} else {
  initMap();
}
