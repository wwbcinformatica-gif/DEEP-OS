/* ============================================
   GeoShield - Monitor Global de Desastres
   JavaScript - APIs, Mapa, Dados em Tempo Real
   ============================================ */

// ==================== CONFIG ====================
const CONFIG = {
    apis: {
        usgs: 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson',
        usgsSignificant: 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson',
        eonet: 'https://eonet.gsfc.nasa.gov/api/v3/events?limit=100&days=3',
        reliefweb: 'https://api.reliefweb.int/v1/disasters?limit=50&sort=date:desc',
        gdacs: 'https://www.gdacs.org/gdacsapi/api/events/getevent?eventcategories=&alertlevel=&country=&radius=&poly=&from=&to='
    },
    refreshInterval: 60000,
    mapCenter: [20, 0],
    mapZoom: 2.5,
    maxAlerts: 50
};

// ==================== STATE ====================
let map = null;
let markers = [];
let allEvents = [];
let allAlerts = [];
let charts = {};
let currentFilter = 'all';
let currentSearchTerm = '';
let currentMapTypeFilter = 'all';
let currentMapMagnitudeFilter = 'all';

// Expose for external access (search integration)
window.geoShieldUtils = window.geoShieldUtils || {};
window.geoShieldUtils.applyMapFilters = applyAllMapFilters;
window.geoShieldUtils.applyAlertFilters = renderAlerts;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initParticles();
    initNavbar();
    initMap();
    initFilters();
    initBackToTop();
    initScrollAnimations();
    loadAllData();
    setInterval(loadAllData, CONFIG.refreshInterval);
});

// ==================== PRELOADER ====================
function initPreloader() {
    window.addEventListener('load', () => {
        setTimeout(() => {
            document.getElementById('preloader').classList.add('hidden');
        }, 1500);
    });
    // Fallback
    setTimeout(() => {
        document.getElementById('preloader').classList.add('hidden');
    }, 4000);
}

// ==================== PARTICLES ====================
function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    const count = 60;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    class Particle {
        constructor() {
            this.reset();
        }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3;
            this.opacity = Math.random() * 0.4 + 0.1;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
                this.reset();
            }
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 204, 255, ${this.opacity})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 204, 255, ${0.05 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
}

// ==================== NAVBAR ====================
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const toggle = document.getElementById('nav-toggle');
    const links = document.querySelector('.nav-links');

    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
    });

    // Close menu on link click
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            links.classList.remove('open');
        });
    });

    // Active nav link on scroll
    const sections = document.querySelectorAll('.section, .hero');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const top = section.offsetTop - 200;
            if (window.scrollY >= top) {
                current = section.getAttribute('id');
            }
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// ==================== MAP ====================
function initMap() {
    map = L.map('main-map', {
        center: CONFIG.mapCenter,
        zoom: CONFIG.mapZoom,
        zoomControl: true,
        attributionControl: false,
        maxBoundsViscosity: 1.0
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 18,
    }).addTo(map);

    // Attribution
    L.control.attribution({ position: 'topright' })
        .addAttribution('GeoShield | <a href="https://carto.com/" style="color:#4466ff">CARTO</a>')
        .addTo(map);

    // Track mouse position
    map.on('mousemove', (e) => {
        document.getElementById('map-coords').textContent = 
            `Lat: ${e.latlng.lat.toFixed(4)} | Lng: ${e.latlng.lng.toFixed(4)}`;
    });
}

function addMarker(lat, lng, type, data) {
    const colors = {
        earthquake: '#ff4444',
        volcano: '#ff8800',
        storm: '#aa44ff',
        flood: '#4488ff',
        wildfire: '#ffcc00',
        sealake: '#00ccff'
    };

    const sizes = {
        earthquake: Math.max(8, (data.magnitude || 2) * 4),
        volcano: 14,
        storm: 16,
        flood: 12,
        wildfire: 12,
        sealake: 10
    };

    const size = sizes[type] || 10;
    const color = colors[type] || '#ffffff';

    const icon = L.divIcon({
        className: '',
        html: `<div style="
            width:${size}px; height:${size}px;
            background:${color};
            border-radius:50%;
            border:2px solid rgba(255,255,255,0.8);
            box-shadow: 0 0 ${size}px ${color}, 0 0 ${size * 2}px ${color}44;
            animation: markerPulse 2s infinite;
        "></div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2]
    });

    const marker = L.marker([lat, lng], { icon }).addTo(map);

    // Store event type and searchable location on the marker object
    // Improved location name extraction for better searchability by country/state
    let locationName = '';
    if (data.place) {
        locationName = data.place;
    } else if (data.title) {
        // Attempt to extract country/state from a general title
        const titleParts = data.title.split(',');
        locationName = titleParts[titleParts.length - 1]?.trim() || data.title; // Last part often country/state
    }
    marker.locationName = locationName.toLowerCase();
    marker.eventType = type;
    marker.options.magnitude = data.magnitude || 0;
    marker.options.time = data.time || data.date || 0;

    let popupContent = '';
    if (type === 'earthquake') {
        const mag = data.magnitude || 0;
        let magClass = 'mag-low';
        if (mag >= 7) magClass = 'mag-extreme';
        else if (mag >= 5) magClass = 'mag-high';
        else if (mag >= 3) magClass = 'mag-mid';

        popupContent = `
            <div class="popup-title">${data.title || 'Terremoto'}</div>
            <div class="popup-magnitude ${magClass}">M ${mag.toFixed(1)}</div>
            <div class="popup-info">
                <div>📍 ${data.place || 'Localização desconhecida'}</div>
                <div>🕐 ${formatTime(data.time)}</div>
                <div>📏 Profundidade: ${data.depth ? data.depth.toFixed(1) : '?'} km</div>
                ${data.tsunami ? '<div style="color:#00ccff">🌊 Possível tsunami</div>' : ''}
            </div>
        `;
    } else if (type === 'volcano') {
        popupContent = `
            <div class="popup-title">${data.title || 'Vulcão'}</div>
            <div class="popup-info">
                <div>🔥 ${data.categories ? data.categories.map(c => c.title).join(', ') : 'Atividade vulcânica'}</div>
                <div>🕐 ${formatTime(data.date)}</div>
                ${data.description ? `<div style="margin-top:6px;font-size:12px">${data.description.substring(0, 150)}...</div>` : ''}
            </div>
        `;
    } else {
        popupContent = `
            <div class="popup-title">${data.title || type}</div>
            <div class="popup-info">
                <div>📍 ${data.place || data.title || ''}</div>
                <div>🕐 ${formatTime(data.time || data.date)}</div>
            </div>
        `;
    }

    marker.bindPopup(popupContent, { maxWidth: 300 });
    markers.push(marker);
    return marker;
}

function applyAllMapFilters() {
    const searchTerm = currentSearchTerm.toLowerCase().trim();
    const magMin = currentMapMagnitudeFilter === 'all' ? 0 : parseFloat(currentMapMagnitudeFilter);

    markers.forEach(m => {
        const matchesType = (currentFilter === 'all' || m.eventType === currentFilter)
                         && (currentMapTypeFilter === 'all' || m.eventType === currentMapTypeFilter);
        
        const markerMag = m.options.magnitude || 0;
        const matchesMag = magMin === 0 || markerMag >= magMin;

        const matchesSearch = !searchTerm || (m.locationName && m.locationName.includes(searchTerm));

        if (matchesType && matchesMag && matchesSearch) {
            m.setOpacity(1);
            m.setZIndexOffset(0);
        } else {
            m.setOpacity(0.15);
            m.setZIndexOffset(-1000);
        }
    });
}

// Add CSS animation for markers
const markerStyle = document.createElement('style');
markerStyle.textContent = `
    @keyframes markerPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.15); opacity: 0.85; }
    }
`;
document.head.appendChild(markerStyle);

// ==================== DATA LOADING ====================
async function loadAllData() {
    updateLastTime();
    // Clear existing markers and alerts before loading new data
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    allAlerts = [];

    await Promise.allSettled([
        loadUSGSEarthquakes(),
        loadNASAEvents(),
        loadReliefWebDisasters()
    ]);
    applyAllMapFilters();
    updateHeroStats();
    updateCharts();

    // Expose markers for external search integration
    window.allMarkers = markers;
}

function updateLastTime() {
    const el = document.getElementById('last-update');
    if (el) el.textContent = new Date().toLocaleString('pt-BR');
}

// --- USGS Earthquakes ---
async function loadUSGSEarthquakes() {
    try {
        const response = await fetch(CONFIG.apis.usgs);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const earthquakes = data.features || [];
        const count = earthquakes.length;

        // Update card
        document.getElementById('count-earthquake').textContent = count;
        document.getElementById('bar-earthquake').style.width = `${Math.min(count / 3, 100)}%`;
        updateCardStatus('earthquake', true);

        // Add markers
        earthquakes.forEach(eq => {
            const [lng, lat] = eq.geometry.coordinates;
            const mag = eq.properties.mag;
            const depth = eq.geometry.coordinates[2];
            addMarker(lat, lng, 'earthquake', {
                title: eq.properties.place,
                place: eq.properties.place,
                magnitude: mag,
                depth: depth,
                time: eq.properties.time,
                tsunami: eq.properties.tsunami
            });
        });

        // Build alerts
        earthquakes.slice(0, CONFIG.maxAlerts).forEach(eq => {
            allAlerts.push({
                type: 'earthquake',
                icon: 'fa-house-crack',
                title: eq.properties.place || 'Terremoto',
                magnitude: eq.properties.mag,
                time: eq.properties.time,
                lat: eq.geometry.coordinates[1],
                lng: eq.geometry.coordinates[0]
            });
        });

        // Build ticker
        updateTicker(earthquakes.slice(0, 15));
        return earthquakes;
    } catch (err) {
        console.error('USGS Error:', err);
        updateCardStatus('earthquake', false, 'Erro ao carregar');
        return [];
    }
}

// --- NASA EONET ---
async function loadNASAEvents() {
    try {
        const response = await fetch(CONFIG.apis.eonet);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const events = data.events || [];
        let volcanoCount = 0, stormCount = 0, floodCount = 0, wildfireCount = 0, sealakeCount = 0;

        events.forEach(event => {
            const categories = event.categories || [];
            const catTitles = categories.map(c => c.title.toLowerCase());

            let type = 'storm'; // default
            if (catTitles.some(c => c.includes('volcano'))) { type = 'volcano'; volcanoCount++; }
            else if (catTitles.some(c => c.includes('storm') || c.includes('hurricane') || c.includes('cyclone') || c.includes('tornado'))) { type = 'storm'; stormCount++; }
            else if (catTitles.some(c => c.includes('flood'))) { type = 'flood'; floodCount++; }
            else if (catTitles.some(c => c.includes('fire'))) { type = 'wildfire'; wildfireCount++; }
            else if (catTitles.some(c => c.includes('sea') || c.includes('lake') || c.includes('ice'))) { type = 'sealake'; sealakeCount++; }
            else { stormCount++; }

            // Add marker for each geometry
            if (event.geometry && event.geometry.length > 0) {
                const geo = event.geometry[0];
                addMarker(geo.coordinates[1], geo.coordinates[0], type, {
                    title: event.title,
                    date: event.geometry[0].date,
                    categories: categories,
                    description: event.description || ''
                });
            }

            // Add to alerts
            allAlerts.push({
                type: type,
                icon: getTypeIcon(type),
                title: event.title,
                magnitude: null,
                time: event.geometry && event.geometry[0] ? event.geometry[0].date : null,
                lat: event.geometry && event.geometry[0] ? event.geometry[0].coordinates[1] : null,
                lng: event.geometry && event.geometry[0] ? event.geometry[0].coordinates[0] : null
            });
        });

        // Update cards
        document.getElementById('count-volcano').textContent = volcanoCount;
        document.getElementById('count-storm').textContent = stormCount;
        document.getElementById('count-flood').textContent = floodCount;
        document.getElementById('count-wildfire').textContent = wildfireCount;
        document.getElementById('count-tsunami').textContent = sealakeCount;

        document.getElementById('bar-volcano').style.width = `${Math.min(volcanoCount * 8, 100)}%`;
        document.getElementById('bar-storm').style.width = `${Math.min(stormCount * 4, 100)}%`;
        document.getElementById('bar-flood').style.width = `${Math.min(floodCount * 6, 100)}%`;
        document.getElementById('bar-wildfire').style.width = `${Math.min(wildfireCount * 5, 100)}%`;
        document.getElementById('bar-tsunami').style.width = `${Math.min(sealakeCount * 10, 100)}%`;

        ['volcano', 'storm', 'flood', 'wildfire', 'tsunami'].forEach(t => updateCardStatus(t, true));
        return events;
    } catch (err) {
        console.error('NASA EONET Error:', err);
        ['volcano', 'storm', 'flood', 'wildfire', 'tsunami'].forEach(t => updateCardStatus(t, false, 'Erro ao carregar'));
        return [];
    }
}

// --- ReliefWeb ---
async function loadReliefWebDisasters() {
    try {
        const response = await fetch(CONFIG.apis.reliefweb);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        const disasters = data.data || [];
        disasters.forEach(d => {
            const fields = d.fields || {};
            const type = mapReliefWebType(fields.type);
            allAlerts.push({
                type: type,
                icon: getTypeIcon(type),
                title: fields.name || fields.title || 'Desastre',
                magnitude: null,
                time: fields.date ? fields.date.created : null,
                lat: fields.country && fields.country[0] ? fields.country[0].location.lat : null,
                lng: fields.country && fields.country[0] ? fields.country[0].location.lon : null
            });
        });

        return disasters;
    } catch (err) {
        console.error('ReliefWeb Error:', err);
        return [];
    }
}

// ==================== UI UPDATES ====================
function updateCardStatus(type, online, errorMsg) {
    const card = document.getElementById(`card-${type}`);
    if (!card) return;
    const statusEl = card.querySelector('.card-status');
    if (online) {
        statusEl.className = 'card-status status-online';
        statusEl.textContent = 'Online';
    } else {
        statusEl.className = 'card-status';
        statusEl.style.color = 'var(--accent-red)';
        statusEl.textContent = errorMsg || 'Offline';
    }
}

function updateHeroStats() {
    const eqCount = allAlerts.filter(a => a.type === 'earthquake').length;
    const volcanoCount = allAlerts.filter(a => a.type === 'volcano').length;
    const activeAlerts = allAlerts.length;
    const countries = new Set(allAlerts.filter(a => a.title).map(a => {
        const parts = a.title.split(',');
        return parts[parts.length - 1]?.trim();
    })).size;

    animateCounter('stat-earthquakes', eqCount);
    animateCounter('stat-active-volcanoes', volcanoCount);
    animateCounter('stat-active-alerts', activeAlerts);
    animateCounter('stat-countries', countries || 45);

    renderAlerts();
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    const diff = target - start;
    const duration = 1000;
    const startTime = performance.now();

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + diff * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

function updateTicker(earthquakes) {
    const ticker = document.getElementById('live-ticker');
    if (!ticker || !earthquakes.length) return;

    let html = '';
    earthquakes.forEach(eq => {
        const mag = eq.properties.mag;
        const place = eq.properties.place || 'Local desconhecido';
        html += `<span class="ticker-item">
            <span class="mag">M ${mag.toFixed(1)}</span>
            <strong>${place}</strong> - ${formatTime(eq.properties.time)}
        </span>`;
    });
    // Duplicate for seamless loop
    ticker.innerHTML = html + html;
}

function renderAlerts() {
    const container = document.getElementById('alerts-list');
    if (!container) return;

    // Sort by time (newest first)
    allAlerts.sort((a, b) => {
        const timeA = a.time || 0;
        const timeB = b.time || 0;
        return new Date(timeB) - new Date(timeA);
    });

    let html = '';
    const filtered = getFilteredAlerts();
    const displayed = filtered.slice(0, CONFIG.maxAlerts);

    if (displayed.length === 0) {
        html = `<div class="no-data"><i class="fas fa-satellite-dish"></i><p>Nenhum alerta encontrado</p></div>`;
    } else {
        displayed.forEach(alert => {
            const magText = alert.magnitude != null ? `M ${alert.magnitude.toFixed(1)}` : '';
            const magClass = getMagnitudeClass(alert.magnitude);
            html += `
                <div class="alert-item" 
                     data-event-type="${alert.type}" 
                     data-magnitude="${alert.magnitude || ''}"
                     onclick="focusMap(${alert.lat || 0}, ${alert.lng || 0})">
                    <div class="alert-icon ${alert.type}">
                        <i class="fas ${alert.icon}"></i>
                    </div>
                    <div class="alert-content">
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-meta">
                            <span><i class="fas fa-tag"></i> ${getTypeLabel(alert.type)}</span>
                            <span><i class="fas fa-clock"></i> ${alert.time ? formatTime(alert.time) : 'N/A'}</span>
                        </div>
                    </div>
                    <div class="alert-mag ${magClass}">${magText}</div>
                </div>
            `;
        });
    }

    container.innerHTML = html;
}

function getFilteredAlerts() {
    const search = document.getElementById('alert-search')?.value.toLowerCase() || '';
    const typeFilter = document.getElementById('alert-type-filter')?.value || 'all';
    const magFilter = document.getElementById('alert-magnitude-filter')?.value || 'all';

    return allAlerts.filter(alert => {
        const matchSearch = !search || (alert.title && alert.title.toLowerCase().includes(search));
        const matchType = typeFilter === 'all' || alert.type === typeFilter;
        const matchMag = magFilter === 'all' || (alert.magnitude && alert.magnitude >= parseFloat(magFilter));
        return matchSearch && matchType && matchMag;
    });
}

function focusMap(lat, lng) {
    if (lat && lng && map) {
        map.flyTo([lat, lng], 6, { duration: 1.5 });
        document.getElementById('map')?.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==================== CHARTS ====================
function updateCharts() {
    updateMagnitudeChart();
    updateRegionChart();
    updateTimelineChart();
}

function updateMagnitudeChart() {
    const ctx = document.getElementById('chart-magnitude');
    if (!ctx) return;

    const eqAlerts = allAlerts.filter(a => a.type === 'earthquake' && a.magnitude != null);
    const bins = { '0-2': 0, '2-3': 0, '3-4': 0, '4-5': 0, '5-6': 0, '6-7': 0, '7+': 0 };
    
    eqAlerts.forEach(a => {
        const m = a.magnitude;
        if (m < 2) bins['0-2']++;
        else if (m < 3) bins['2-3']++;
        else if (m < 4) bins['3-4']++;
        else if (m < 5) bins['4-5']++;
        else if (m < 6) bins['5-6']++;
        else if (m < 7) bins['6-7']++;
        else bins['7+']++;
    });

    if (charts.magnitude) charts.magnitude.destroy();
    charts.magnitude = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(bins),
            datasets: [{
                label: 'Terremotos',
                data: Object.values(bins),
                backgroundColor: [
                    'rgba(0, 255, 136, 0.6)',
                    'rgba(0, 204, 255, 0.6)',
                    'rgba(68, 102, 255, 0.6)',
                    'rgba(255, 204, 0, 0.6)',
                    'rgba(255, 136, 0, 0.6)',
                    'rgba(255, 68, 68, 0.6)',
                    'rgba(255, 0, 0, 0.8)'
                ],
                borderColor: [
                    '#00ff88', '#00ccff', '#4466ff', '#ffcc00', '#ff8800', '#ff4444', '#ff0000'
                ],
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b92c4', font: { family: 'Rajdhani' } }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b92c4', font: { family: 'Rajdhani' } }
                }
            }
        }
    });
}

function updateRegionChart() {
    const ctx = document.getElementById('chart-region');
    if (!ctx) return;

    // Count events by region from all alerts
    const regions = {};
    allAlerts.forEach(a => {
        if (a.title) {
            const parts = a.title.split(',');
            const region = parts[parts.length - 1]?.trim() || 'Desconhecido';
            regions[region] = (regions[region] || 0) + 1;
        }
    });

    // Get top 8 regions
    const sorted = Object.entries(regions)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    if (charts.region) charts.region.destroy();
    charts.region = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sorted.map(s => s[0]),
            datasets: [{
                data: sorted.map(s => s[1]),
                backgroundColor: [
                    'rgba(68, 102, 255, 0.7)',
                    'rgba(0, 204, 255, 0.7)',
                    'rgba(170, 68, 255, 0.7)',
                    'rgba(255, 136, 0, 0.7)',
                    'rgba(0, 255, 136, 0.7)',
                    'rgba(255, 68, 68, 0.7)',
                    'rgba(255, 204, 0, 0.7)',
                    'rgba(255, 68, 170, 0.7)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#8b92c4',
                        font: { family: 'Space Grotesk', size: 12 },
                        padding: 12,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                }
            }
        }
    });
}

function updateTimelineChart() {
    const ctx = document.getElementById('chart-timeline');
    if (!ctx) return;

    // Group alerts by hour
    const hours = {};
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
        const h = new Date(now - i * 3600000);
        const key = h.getHours().toString().padStart(2, '0') + ':00';
        hours[key] = { earthquake: 0, volcano: 0, storm: 0, flood: 0, wildfire: 0 };
    }

    allAlerts.forEach(a => {
        if (!a.time) return;
        const d = new Date(a.time);
        const key = d.getHours().toString().padStart(2, '0') + ':00';
        if (hours[key] && hours[key][a.type] !== undefined) {
            hours[key][a.type]++;
        }
    });

    const labels = Object.keys(hours);
    const types = ['earthquake', 'volcano', 'storm', 'flood', 'wildfire'];
    const colors = ['#ff4444', '#ff8800', '#aa44ff', '#4488ff', '#ffcc00'];

    if (charts.timeline) charts.timeline.destroy();
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: types.map((t, i) => ({
                label: getTypeLabel(t),
                data: labels.map(h => hours[h][t]),
                borderColor: colors[i],
                backgroundColor: colors[i] + '22',
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 5
            }))
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    labels: {
                        color: '#8b92c4',
                        font: { family: 'Space Grotesk', size: 12 },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b92c4', font: { family: 'Rajdhani' }, maxTicksLimit: 12 }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#8b92c4', font: { family: 'Rajdhani' }, stepSize: 1 }
                }
            }
        }
    });
}

// ==================== FILTERS ====================
function initFilters() {
    // Map type filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            // Sincroniza o select de tipo com os botões
            const typeSelect = document.getElementById('map-type-filter');
            if (typeSelect) typeSelect.value = currentFilter;
            applyAllMapFilters();
        });
    });

    // Map type filter dropdown
    const mapTypeFilter = document.getElementById('map-type-filter');
    if (mapTypeFilter) {
        mapTypeFilter.addEventListener('change', (e) => {
            currentMapTypeFilter = e.target.value;
            currentFilter = e.target.value;
            // Sincroniza os botões com o select
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.filter === currentFilter);
            });
            applyAllMapFilters();
        });
    }

    // Map magnitude filter dropdown
    const mapMagFilter = document.getElementById('map-magnitude-filter');
    if (mapMagFilter) {
        mapMagFilter.addEventListener('change', (e) => {
            currentMapMagnitudeFilter = e.target.value;
            applyAllMapFilters();
        });
    }

    // Map search input
    const mapSearchInput = document.getElementById('searchInput');
    if (mapSearchInput) {
        mapSearchInput.addEventListener('input', (e) => {
            currentSearchTerm = e.target.value;
            applyAllMapFilters();
        });
        mapSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyAllMapFilters();

                // Encontra o resultado mais grave que corresponde à busca
                const term = currentSearchTerm.toLowerCase().trim();
                if (term && markers.length > 0) {
                    const magMin = currentMapMagnitudeFilter === 'all' ? 0 : parseFloat(currentMapMagnitudeFilter);

                    const matches = markers.filter(m => {
                        const matchesType = (currentFilter === 'all' || m.eventType === currentFilter);
                        const matchesSearch = m.locationName && m.locationName.includes(term);
                        const matchesMag = magMin === 0 || (m.options.magnitude || 0) >= magMin;
                        return matchesType && matchesSearch && matchesMag;
                    });

                    if (matches.length > 0) {
                        // Ordena por gravidade: magnitude (maior primeiro) e depois por mais recente
                        matches.sort((a, b) => {
                            const magA = a.options.magnitude || 0;
                            const magB = b.options.magnitude || 0;
                            if (magB !== magA) return magB - magA;
                            const timeA = a.options.time || 0;
                            const timeB = b.options.time || 0;
                            return timeB - timeA;
                        });

                        const best = matches[0];
                        const latlng = best.getLatLng();
                        map.flyTo(latlng, 6, { duration: 1.5 });
                        best.openPopup();
                    }
                }
            }
        });
    }

    // Alert search and filters
    const alertSearchInput = document.getElementById('alert-search');
    const typeFilter = document.getElementById('alert-type-filter');
    const magFilter = document.getElementById('alert-magnitude-filter');

    if (alertSearchInput) {
        alertSearchInput.addEventListener('input', renderAlerts);
        alertSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                renderAlerts();
            }
        });
    }
    if (typeFilter) typeFilter.addEventListener('change', renderAlerts);
    if (magFilter) magFilter.addEventListener('change', renderAlerts);

    // Load more alerts button
    const loadMoreBtn = document.getElementById('load-more-alerts');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            setTimeout(renderAlerts, 300);
        });
    }
}

// ==================== BACK TO TOP ====================
function initBackToTop() {
    const btn = document.getElementById('back-to-top');
    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 500);
    });
    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ==================== SCROLL ANIMATIONS ====================
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.category-card, .stat-card, .source-card, .api-card').forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// ==================== HELPERS ====================
function formatTime(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Agora';
    if (diff < 3600000) return `Há ${Math.floor(diff / 60000)} min`;
    if (diff < 86400000) return `Há ${Math.floor(diff / 3600000)}h`;
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function getMagnitudeClass(mag) {
    if (mag == null) return '';
    if (mag >= 7) return 'mag-extreme';
    if (mag >= 5) return 'mag-high';
    if (mag >= 3) return 'mag-mid';
    return 'mag-low';
}

function getTypeIcon(type) {
    const icons = {
        earthquake: 'fa-house-crack',
        volcano: 'fa-fire',
        storm: 'fa-wind',
        flood: 'fa-water',
        wildfire: 'fa-fire-flame-curved',
        sealake: 'fa-snowflake'
    };
    return icons[type] || 'fa-circle-exclamation';
}

function getTypeLabel(type) {
    const labels = {
        earthquake: 'Terremoto',
        volcano: 'Vulcão',
        storm: 'Tempestade',
        flood: 'Enchente',
        wildfire: 'Incêndio',
        sealake: 'Gelo/Neve'
    };
    return labels[type] || type;
}

function mapReliefWebType(typeObj) {
    if (!typeObj) return 'storm';
    const name = (typeObj.name || '').toLowerCase();
    if (name.includes('earthquake')) return 'earthquake';
    if (name.includes('volcano')) return 'volcano';
    if (name.includes('flood')) return 'flood';
    if (name.includes('cyclone') || name.includes('hurricane') || name.includes('typhoon') || name.includes('storm')) return 'storm';
    if (name.includes('wildfire') || name.includes('fire')) return 'wildfire';
    if (name.includes('tsunami')) return 'tsunami';
    return 'storm';
}