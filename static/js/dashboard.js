document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('org-events-container')) {
        initDashboard();
    }
});

function initDashboard() {
    fetchAnalytics();
    fetchOrganizerEvents();
    setupModal();
    setupSeatsPreview();
}

// Fetch and display analytics
// Fetch and display analytics
async function fetchAnalytics() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        const res = await authenticatedFetch('/api/events/analytics/');

        if (!res.ok) return;

        const data = await res.json();

        document.getElementById('total-revenue').textContent = `$${data.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        document.getElementById('tickets-sold').textContent = data.total_tickets_sold;
        document.getElementById('total-events').textContent = data.total_events;

    } catch (err) {
        console.error('Analytics error:', err);
    }
}

// Fetch organizer's events
async function fetchOrganizerEvents() {
    const token = localStorage.getItem('access_token');
    const container = document.getElementById('org-events-container');
    const loader = document.getElementById('loading-indicator');

    if (!token) return;

    try {
        const res = await authenticatedFetch('/api/events/');

        if (!res.ok) throw new Error('Failed to fetch events');

        const events = await res.json();

        container.innerHTML = '';
        if (loader) loader.classList.add('hidden');

        if (events.length === 0) {
            container.innerHTML = `<div class="no-events">
                <p>You haven't created any events yet.</p>
                <p>Click "Create New Event" to get started!</p>
            </div>`;
            return;
        }

        events.forEach(event => {
            const date = new Date(event.date_time).toLocaleDateString('en-US', {
                weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            // Build image HTML
            const imageHtml = event.venue_image
                ? `<div class="event-image" style="background-image: url('${event.venue_image}')"></div>`
                : `<div class="event-image-placeholder"></div>`;

            const card = document.createElement('div');
            card.className = 'event-card';
            card.innerHTML = `
                ${imageHtml}
                <div class="event-card-content">
                    <h3 class="event-title">${event.title}</h3>
                    <div class="event-meta">📅 ${date}</div>
                    <div class="event-meta">📍 ${event.location}</div>
                    <div class="event-actions">
                        <a href="/event/${event.id}/" class="icon-btn">View Details</a>
                        <a href="/book-event/${event.id}/" class="icon-btn">Manage Seats 🎟️</a>
                        <button onclick="deleteEvent(${event.id})" class="icon-btn delete-btn" style="background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2);">Delete 🗑️</button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        if (loader) loader.textContent = 'Error loading events.';
    }
}

// Modal handling
function setupModal() {
    const modal = document.getElementById('create-event-modal');
    const openBtn = document.getElementById('create-event-btn');
    const closeBtn = document.querySelector('.close-modal');
    const form = document.getElementById('create-event-form');

    if (openBtn) openBtn.onclick = () => modal.classList.remove('hidden');
    if (closeBtn) closeBtn.onclick = () => modal.classList.add('hidden');

    window.onclick = (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    };

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem('access_token');
            const submitBtn = form.querySelector('button[type="submit"]');

            const title = document.getElementById('evt-title').value;
            const description = document.getElementById('evt-desc').value;
            const location = document.getElementById('evt-location').value;
            const dateTime = document.getElementById('evt-date').value;
            const rows = parseInt(document.getElementById('evt-rows').value);
            const cols = parseInt(document.getElementById('evt-cols').value);
            const priceVip = document.getElementById('evt-price-vip').value;
            const priceStandard = document.getElementById('evt-price-standard').value;
            const priceEconomy = document.getElementById('evt-price-economy').value;

            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating Event...';
            submitBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('title', title);
                formData.append('description', description);
                formData.append('location', location);
                formData.append('date_time', dateTime);
                formData.append('seat_rows', rows);
                formData.append('seat_cols', cols);
                formData.append('seat_price_vip', priceVip);
                formData.append('seat_price_standard', priceStandard);
                formData.append('seat_price_economy', priceEconomy);

                // Add venue image if selected
                const imageInput = document.getElementById('evt-image');
                if (imageInput && imageInput.files[0]) {
                    formData.append('venue_image', imageInput.files[0]);
                }

                const eventRes = await authenticatedFetch('/api/events/', {
                    method: 'POST',
                    body: formData
                });

                if (!eventRes.ok) {
                    const data = await eventRes.json();
                    throw new Error(JSON.stringify(data));
                }

                const event = await eventRes.json();
                alert(`Event created with ${event.seats_created || rows * cols} seats!`);
                modal.classList.add('hidden');
                form.reset();
                resetFormDefaults();
                fetchOrganizerEvents();
                fetchAnalytics();

            } catch (err) {
                alert('Error: ' + err.message);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

function resetFormDefaults() {
    document.getElementById('evt-rows').value = 6;
    document.getElementById('evt-cols').value = 10;
    document.getElementById('evt-price-vip').value = 150;
    document.getElementById('evt-price-standard').value = 100;
    document.getElementById('evt-price-economy').value = 50;
    updateSeatsPreview();
}

// Seats preview
function setupSeatsPreview() {
    const inputs = ['evt-rows', 'evt-cols', 'evt-price-vip', 'evt-price-standard', 'evt-price-economy'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', updateSeatsPreview);
    });
    updateSeatsPreview();
}

function updateSeatsPreview() {
    const rows = parseInt(document.getElementById('evt-rows').value) || 0;
    const cols = parseInt(document.getElementById('evt-cols').value) || 0;
    const priceVip = parseFloat(document.getElementById('evt-price-vip').value) || 0;
    const priceStandard = parseFloat(document.getElementById('evt-price-standard').value) || 0;
    const priceEconomy = parseFloat(document.getElementById('evt-price-economy').value) || 0;

    // Calculate seats per tier
    const vipRows = Math.min(2, rows);
    const standardRows = Math.min(3, Math.max(0, rows - 2));
    const economyRows = Math.max(0, rows - 5);

    const vipSeats = vipRows * cols;
    const standardSeats = standardRows * cols;
    const economySeats = economyRows * cols;

    const totalValue = (vipSeats * priceVip) + (standardSeats * priceStandard) + (economySeats * priceEconomy);

    const preview = document.getElementById('seats-preview');
    if (preview) {
        preview.innerHTML = `
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 0.5rem;">
                <span>💎 VIP: <strong style="color: #fbbf24;">${vipSeats}</strong></span>
                <span>⭐ Standard: <strong style="color: #22d3ee;">${standardSeats}</strong></span>
                <span>🎫 Economy: <strong style="color: #22c55e;">${economySeats}</strong></span>
            </div>
            <div style="margin-top: 0.5rem;">
                Total: <strong>${rows * cols}</strong> seats | Value: <strong style="color: #2dd4bf;">$${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</strong>
            </div>
        `;
    }
}


// Delete Event
window.deleteEvent = async function (eventId) {
    if (!confirm('Are you sure you want to delete this event? This action cannot be undone.')) return;

    const originalBtn = document.querySelector(`button[onclick="deleteEvent(${eventId})"]`);
    if (originalBtn) {
        originalBtn.textContent = 'Deleting...';
        originalBtn.disabled = true;
    }

    try {
        const res = await authenticatedFetch(`/api/events/${eventId}/`, {
            method: 'DELETE'
        });

        if (res.ok) {
            // Refresh events
            fetchOrganizerEvents();
            fetchAnalytics();
        } else {
            const data = await res.json().catch(() => ({}));
            alert('Failed to delete event: ' + (data.detail || 'Unknown error'));
            if (originalBtn) {
                originalBtn.textContent = 'Delete 🗑️';
                originalBtn.disabled = false;
            }
        }
    } catch (err) {
        console.error("Error deleting event:", err);
        alert('Error deleting event.');
        if (originalBtn) {
            originalBtn.textContent = 'Delete 🗑️';
            originalBtn.disabled = false;
        }
    }
};
