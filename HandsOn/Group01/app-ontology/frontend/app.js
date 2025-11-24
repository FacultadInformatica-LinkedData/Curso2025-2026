// frontend/app.js
const runBtn = document.getElementById('run');
const qEl = document.getElementById('query');
const resultsEl = document.getElementById('results');
const examples = document.getElementById('examples');
const healthBtn = document.getElementById('health-check');

// Cargar ejemplos desde el backend
let exampleQueries = [];

async function loadExamples() {
  try {
    const resp = await fetch('/api/examples');
    if (resp.ok) {
      exampleQueries = await resp.json();
      populateExamples();
    } else {
      useFallbackExamples();
    }
  } catch (err) {
    console.warn('No se pudieron cargar ejemplos del servidor, usando fallback');
    useFallbackExamples();
  }
}

function useFallbackExamples() {
  exampleQueries = [
    {name: "10 sujetos y labels", query: `PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nSELECT ?s ?label WHERE { ?s a ?type . OPTIONAL { ?s rdfs:label ?label } } LIMIT 10`},
    {name: "Contar instancias por clase", query: `SELECT ?class (COUNT(?s) AS ?count) WHERE { ?s a ?class } GROUP BY ?class ORDER BY DESC(?count) LIMIT 20`}
  ];
  populateExamples();
}

function populateExamples() {
  examples.innerHTML = '<option value="">— Consultas de ejemplo —</option>';
  exampleQueries.forEach(e => {
    const opt = document.createElement('option');
    opt.value = e.query;
    opt.textContent = e.name;
    if (e.description) {
      opt.title = e.description;
    }
    examples.appendChild(opt);
  });
}

examples.addEventListener('change', () => {
  if (examples.value) {
    qEl.value = examples.value;
  }
});

runBtn.addEventListener('click', async () => {
  resultsEl.innerHTML = '<div class="loading">🔄 Ejecutando consulta...</div>';
  const query = qEl.value;
  try {
    const resp = await fetch('/api/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ query, format: 'application/sparql-results+json' })
    });
    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(`HTTP ${resp.status}: ${errorText}`);
    }
    const data = await resp.json();
    renderResults(data);
  } catch (err) {
    resultsEl.innerHTML = `<pre class="error">❌ Error: ${escapeHtml(err.message)}</pre>`;
  }
});

if (healthBtn) {
  healthBtn.addEventListener('click', async () => {
    try {
      const resp = await fetch('/api/health');
      const data = await resp.json();
      alert(`Backend: ${data.backend}\nSPARQL: ${data.sparql_status}\nEndpoint: ${data.sparql_endpoint}`);
    } catch (err) {
      alert('❌ No se pudo conectar con el backend');
    }
  });
}

function renderResults(data) {
  if (!data?.head || !data?.results) {
    resultsEl.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    return;
  }
  const vars = data.head.vars;
  const rows = data.results.bindings;
  if (!rows.length) {
    resultsEl.innerHTML = '<p class="no-results">ℹ️ No hay resultados para esta consulta.</p>';
    return;
  }
  
  const resultInfo = document.createElement('div');
  resultInfo.className = 'result-info';
  resultInfo.textContent = `✓ ${rows.length} resultado${rows.length !== 1 ? 's' : ''} encontrado${rows.length !== 1 ? 's' : ''}`;
  
  const table = document.createElement('table');
  const thead = document.createElement('thead');
  thead.innerHTML = '<tr>' + vars.map(v => `<th>${escapeHtml(v)}</th>`).join('') + '</tr>';
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  rows.forEach(r => {
    const tr = document.createElement('tr');
    vars.forEach(v => {
      const td = document.createElement('td');
      if (r[v]) {
        const value = r[v].value;
        const type = r[v].type;
        
        if (type === 'uri') {
          const link = document.createElement('a');
          link.href = value;
          link.textContent = shortenUri(value);
          link.target = '_blank';
          link.className = 'uri-link';
          td.appendChild(link);
        } else {
          td.textContent = value;
        }
      } else {
        td.className = 'null-value';
        td.textContent = '—';
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  
  resultsEl.innerHTML = '';
  resultsEl.appendChild(resultInfo);
  resultsEl.appendChild(table);
}

function shortenUri(uri) {
  const match = uri.match(/[#\/]([^#\/]+)$/);
  if (match) {
    return match[1];
  }
  return uri.length > 50 ? uri.substring(0, 47) + '...' : uri;
}

function escapeHtml(s) {
  if (!s) return '';
  const text = String(s);
  return text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

loadExamples();
