const API_BASE = 'http://127.0.0.1:8080';
let token = null;
let serverTimeDiff = 0;

// Sincronizar hora con el servidor
async function syncServerTime() {
  try {
    const start = Date.now();
    const res = await fetch(`${API_BASE}/server-time`);
    const data = await res.json();
    const end = Date.now();
    const latency = (end - start) / 2; // Aproximar latencia de red
    const serverTime = new Date(data.utc).getTime();
    const localTime = Date.now();
    serverTimeDiff = serverTime - (localTime + latency);
    log(`Hora sincronizada. Diferencia con servidor: ${serverTimeDiff}ms`);
  } catch (err) {
    log('Error al sincronizar hora: ' + err.message);
  }
}

// Obtener hora actual ajustada al servidor
function getAdjustedNow() {
  return new Date(Date.now() + serverTimeDiff);
}

const el = id => document.getElementById(id);
const log = (msg) => {
  const node = el('debug-log');
  node.innerText = `${new Date().toLocaleTimeString()} - ${msg}\n` + node.innerText;
};

function showResult(elementId, message, isError = false) {
  const element = el(elementId);
  element.innerText = message;
  element.className = 'result ' + (isError ? 'error' : 'success');
  setTimeout(() => element.className = 'result', 5000); // Reset class after 5s
}

// Helpers
function authHeaders() {
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// Register
el('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    username: el('reg-username').value,
    email: el('reg-email').value,
    password: el('reg-password').value,
  };
  try {
    const res = await fetch(`${API_BASE}/users/register`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const data = await res.json();
    showResult('register-result', res.ok ? 'Registrado correctamente. ID: ' + data.id : (data.detail || 'Error al registrar'), !res.ok);
    log('Register -> ' + res.status);
  } catch (err) {
    el('register-result').innerText = 'Error: ' + err.message;
    log('Register error: ' + err.message);
  }
});

// Login
el('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = { email: el('login-email').value, password: el('login-password').value };
  try {
    const res = await fetch(`${API_BASE}/users/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const data = await res.json();
    if (res.ok && data.access_token) {
      token = data.access_token;
      showResult('login-result', 'Autenticado correctamente');
      el('token-display').innerText = token.slice(0,40) + '...';
      log('Login OK');
    } else {
      el('login-result').innerText = JSON.stringify(data);
      log('Login failed: ' + res.status);
    }
  } catch (err) {
    el('login-result').innerText = 'Error: ' + err.message;
    log('Login error: ' + err.message);
  }
});

// Create giveaway
el('create-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const endDateValue = el('g-enddate').value; // datetime-local value
  const body = {
    title: el('g-title').value,
    description: el('g-description').value,
    prize: el('g-prize').value,
    image_url: el('g-image').value || null,
    end_date: new Date(endDateValue).toISOString()
  };
  try {
    const headers = { 'Content-Type': 'application/json', ...authHeaders() };
    const res = await fetch(`${API_BASE}/giveaways/`, {
      method: 'POST', headers, body: JSON.stringify(body)
    });
    const data = await res.json();
    showResult('create-result', res.ok ? `Giveaway creado correctamente (id ${data.id})` : (data.detail || 'Error al crear el giveaway'), !res.ok);
    log('Create giveaway -> ' + res.status);
    if (res.ok) loadGiveaways();
  } catch (err) {
    el('create-result').innerText = 'Error: ' + err.message;
    log('Create error: ' + err.message);
  }
});

// List giveaways
async function participateInGiveaway(giveawayId) {
  if (!token) {
    alert('Debes iniciar sesión para participar');
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/giveaways/${giveawayId}/participate`, {
      method: 'POST',
      headers: authHeaders()
    });
    const data = await res.json();
    if (res.ok) {
      showResult(`giveaway-${giveawayId}-result`, 'Te has registrado en el sorteo correctamente');
      loadGiveaways(); // Refresh list
    } else {
      showResult(`giveaway-${giveawayId}-result`, data.detail || 'Error al participar', true);
    }
    log(`Participate in giveaway ${giveawayId} -> ${res.status}`);
  } catch (err) {
    showResult(`giveaway-${giveawayId}-result`, 'Error: ' + err.message, true);
    log('Participate error: ' + err.message);
  }
}

async function loadGiveaways(){
  try{
    const res = await fetch(`${API_BASE}/giveaways/`);
    const data = await res.json();
    const list = el('giveaway-list');
    list.innerHTML = '';
    if (!Array.isArray(data)) {
      list.innerHTML = '<li>Error: ' + JSON.stringify(data) + '</li>';
      log('List giveaways: unexpected response');
      return;
    }
    data.forEach(g => {
      const li = document.createElement('li');
      // Usar hora sincronizada con el servidor
      const now = getAdjustedNow();
      const endDate = new Date(g.end_date);
      const isActive = endDate > now;
      const isOwner = g.is_owner;
      const canDraw = !g.winner && !isActive && isOwner;
      
      console.log(`Giveaway ${g.id}:`, {
        endDate: endDate.toLocaleString(),
        now: now.toLocaleString(),
        isActive,
        isOwner,
        canDraw,
        hasParticipated: g.has_participated,
        winner: g.winner,
        canParticipate: g.can_participate,
        timeUntilEnd: (endDate - now) / 1000 / 60, // minutos hasta el final
      });
      li.innerHTML = `
        <strong>${escapeHtml(g.title)}</strong> — Premio: ${escapeHtml(g.prize)}
        <br/><small>Finaliza: ${new Date(g.end_date).toLocaleString()}</small>
        <p>${escapeHtml(g.description)}</p>
        <small>Creator: ${g.creator ? g.creator.username : g.creator_id}</small>
        <div class="giveaway-info">
          <small>Participantes: ${g.participants_count}</small>
          <div class="status-container">
            ${endDate <= now 
              ? '<small class="status-ended">🕒 Sorteo finalizado</small>'
              : '<small class="status-info">🕒 Sorteo en curso</small>'
            }
          </div>
        </div>
        <div class="giveaway-actions">
          ${g.winner 
            ? `<div class="winner-info">
                <span class="winner-label">🎉 Ganador:</span>
                <strong>${g.winner.username}</strong>
                <small>(${new Date(g.drawn_at).toLocaleString()})</small>
              </div>`
            : endDate <= now 
              ? (isOwner 
                ? `<button onclick="drawWinner(${g.id})" class="draw-btn">Realizar Sorteo</button>`
                : `<small class="status-ended">Esperando al sorteo</small>`)
              : (isOwner
                ? `<small class="status-info">Esperando a que finalice el sorteo</small>`
                : g.has_participated 
                  ? `<small class="status-info">✓ Ya estás participando</small>`
                  : `<button onclick="participateInGiveaway(${g.id})" class="participate-btn">Participar</button>`)
          }
          ${g.participants_count > 0 
            ? `<small class="participants-info">👥 ${g.participants_count} participante${g.participants_count !== 1 ? 's' : ''}</small>` 
            : ''
          }
          <div id="giveaway-${g.id}-result" class="result"></div>
        </div>
      `;
      list.appendChild(li);
    });
    log('Loaded giveaways: ' + data.length);
  } catch(err){
    el('giveaway-list').innerHTML = '<li>Error: ' + err.message + '</li>';
    log('Load giveaways error: ' + err.message);
  }
}

el('refresh-list').addEventListener('click', loadGiveaways);

async function drawWinner(giveawayId) {
  if (!token) {
    alert('Debes iniciar sesión para realizar el sorteo');
    return;
  }
  if (!confirm('¿Estás seguro de que quieres realizar el sorteo? Esta acción no se puede deshacer.')) {
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/giveaways/${giveawayId}/draw`, {
      method: 'POST',
      headers: authHeaders()
    });
    const data = await res.json();
    if (res.ok) {
      showResult(`giveaway-${giveawayId}-result`, `¡El ganador es ${data.winner.username}!`);
      loadGiveaways(); // Refresh list
    } else {
      showResult(`giveaway-${giveawayId}-result`, data.detail || 'Error al realizar el sorteo', true);
    }
    log(`Draw winner for giveaway ${giveawayId} -> ${res.status}`);
  } catch (err) {
    showResult(`giveaway-${giveawayId}-result`, 'Error: ' + err.message, true);
    log('Draw winner error: ' + err.message);
  }
}

function escapeHtml(text){
  if (!text) return '';
  return text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
}

// Init
el('api-base').innerText = API_BASE;
syncServerTime().then(() => loadGiveaways());
