document.addEventListener('DOMContentLoaded', () => {
    fetchEvents();
    checkAuth();

    // Load order history if on that page
    if (document.getElementById('orders-container')) {
        fetchOrders();
    }
});

// --- Global Authenticated Fetch ---
window.authenticatedFetch = async function (url, options = {}) {
    let token = localStorage.getItem('access_token');

    // Default headers
    const headers = {
        ...options.headers,
        'Authorization': `JWT ${token}`
    };

    // Auto-set Content-Type to JSON if body is present and not FormData, and not already set
    if (!headers['Content-Type'] && options.body && typeof options.body === 'string') {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, { ...options, headers });

    // Handle Token Expiration
    if (response.status === 401) {
        const data = await response.clone().json().catch(() => ({}));

        // Check specific error message if possible, or just assume 401 needs refresh
        if (data.detail === "Given token not valid for any token type" ||
            (data.messages && data.messages[0] && data.messages[0].message === "Token is expired")) {

            console.log("Token expired, attempting refresh...");
            const refreshToken = localStorage.getItem('refresh_token');

            if (!refreshToken) {
                logout();
                throw new Error("Session expired. Please login again.");
            }

            try {
                const refreshRes = await fetch('/auth/jwt/refresh/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: refreshToken })
                });

                if (refreshRes.ok) {
                    const refreshData = await refreshRes.json();
                    localStorage.setItem('access_token', refreshData.access);
                    console.log("Token refreshed successfully.");

                    // Retry original request with new token
                    headers['Authorization'] = `JWT ${refreshData.access}`;
                    return await fetch(url, { ...options, headers });
                } else {
                    console.error("Refresh failed");
                    logout();
                    throw new Error("Session expired. Please login again.");
                }
            } catch (err) {
                console.error("Error during token refresh:", err);
                logout();
                throw err;
            }
        }
    }

    return response;
};

// --- Auth & Navigation ---

function checkAuth() {
    const loginBtn = document.getElementById('login-btn');
    const navLinks = document.querySelector('.nav-links');
    const token = localStorage.getItem('access_token');

    if (token) {
        if (loginBtn) {
            loginBtn.textContent = 'Logout';
            loginBtn.onclick = (e) => {
                e.preventDefault();
                logout();
            };
        }

        const role = localStorage.getItem('user_role');
        const currentPath = window.location.pathname;

        // Add navigation links based on role
        if (navLinks) {
            // Add My Orders link for customers
            if (!document.getElementById('orders-link')) {
                const ordersLink = document.createElement('a');
                ordersLink.href = '/my-orders/';
                ordersLink.id = 'orders-link';
                ordersLink.textContent = 'My Orders';
                if (loginBtn) {
                    navLinks.insertBefore(ordersLink, loginBtn);
                } else {
                    navLinks.appendChild(ordersLink);
                }
            }

            // Add Admin Dashboard link for staff
            const isStaff = localStorage.getItem('is_staff') === 'true';
            if (isStaff) {
                if (!document.getElementById('admin-link')) {
                    const adminLink = document.createElement('a');
                    adminLink.href = '/admin-logs/';
                    adminLink.id = 'admin-link';
                    adminLink.textContent = 'Admin Dashboard';
                    // Insert before login button
                    if (loginBtn) {
                        navLinks.insertBefore(adminLink, loginBtn);
                    } else {
                        navLinks.appendChild(adminLink);
                    }
                }
            }

            // Add Dashboard link for organizers
            if (role === 'ORGANIZER') {
                if (!document.getElementById('dashboard-link')) {
                    const dashLink = document.createElement('a');
                    dashLink.href = '/organizer/';
                    dashLink.id = 'dashboard-link';
                    dashLink.textContent = 'Dashboard';
                    if (loginBtn) {
                        navLinks.insertBefore(dashLink, loginBtn);
                    } else {
                        navLinks.appendChild(dashLink);
                    }
                }
            }
        }

        // Protect organizer dashboard
        if (currentPath.includes('/organizer/')) {
            if (role !== 'ORGANIZER') {
                window.location.href = '/';
            }
        }
    } else {
        if (loginBtn) loginBtn.href = '/login/';

        // Redirect to login for protected pages
        if (window.location.pathname.includes('/organizer/') ||
            window.location.pathname.includes('/my-orders/')) {
            window.location.href = '/login/';
        }
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('is_staff');
    window.location.href = '/';
}

// --- Home Page ---
async function fetchEvents() {
    const container = document.getElementById('events-container');
    if (!container) return;

    try {
        const response = await fetch('/api/events/');
        if (!response.ok) throw new Error('Failed to fetch events');
        const events = await response.json();
        renderEvents(events, container);
    } catch (error) {
        console.error(error);
        container.innerHTML = '<div class="error">Unable to load events.</div>';
    }
}

function renderEvents(events, container) {
    container.innerHTML = '';
    if (events.length === 0) {
        container.innerHTML = '<div class="no-events">No upcoming events found.</div>';
        return;
    }
    events.forEach(event => {
        const date = new Date(event.date_time).toLocaleDateString('en-US', {
            weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
        });

        // Build image HTML if venue_image exists
        const imageHtml = event.venue_image
            ? `<div class="event-image" style="background-image: url('${event.venue_image}')"></div>`
            : `<div class="event-image-placeholder"></div>`;

        const card = document.createElement('div');
        card.className = 'event-card';
        card.innerHTML = `
            ${imageHtml}
            <div class="event-card-content">
                <h3 class="event-title">${event.title}</h3>
                <div class="event-date">📅 ${date}</div>
                <div class="event-location">📍 ${event.location}</div>
                <p>${event.description.substring(0, 80)}...</p>
                <button class="book-btn" onclick="window.location.href='/event/${event.id}/'">View Details</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// --- Login Form ---
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMsg = document.getElementById('error-message');

        try {
            const response = await fetch('/auth/jwt/create/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) throw new Error('Invalid credentials');

            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);

            // Get User Role
            const meRes = await fetch('/auth/users/me/', {
                headers: { 'Authorization': `JWT ${data.access}` }
            });
            const meData = await meRes.json();
            localStorage.setItem('user_role', meData.role);
            localStorage.setItem('is_staff', meData.is_staff);

            if (meData.role === 'ORGANIZER') {
                window.location.href = '/organizer/';
            } else {
                window.location.href = '/';
            }

        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        }
    });
}

// --- Register Form ---
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const re_password = document.getElementById('reg-re-password').value;
        const errorMsg = document.getElementById('reg-error-message');

        if (password !== re_password) {
            errorMsg.textContent = "Passwords do not match.";
            errorMsg.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch('/auth/users/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, re_password })
            });

            if (!response.ok) {
                const data = await response.json();
                let msg = 'Registration failed.';
                if (typeof data === 'object') msg = Object.values(data).flat().join(' ');
                throw new Error(msg);
            }

            alert('Registration successful! Please login.');
            window.location.href = '/login/';
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        }
    });
}

// --- Booking Page Logic ---
// Only run on booking page (has seat-map element)
if (typeof EVENT_ID !== 'undefined' && document.getElementById('seat-map')) {
    loadBookingEventDetails(EVENT_ID);
    loadBookingSeats(EVENT_ID);

    const token = localStorage.getItem('access_token');
    if (!token) {
        const loginPrompt = document.getElementById('login-prompt');
        if (loginPrompt) loginPrompt.classList.remove('hidden');
    }
}

async function loadBookingEventDetails(eventId) {
    const titleEl = document.getElementById('event-title');
    const detailsEl = document.getElementById('event-details');

    if (!titleEl || !detailsEl) return; // Not on booking page

    try {
        const response = await fetch(`/api/events/${eventId}/`);
        const event = await response.json();

        titleEl.textContent = event.title;

        const date = new Date(event.date_time).toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
        detailsEl.textContent = `📅 ${date} | 📍 ${event.location}`;
    } catch (error) {
        console.error("Error loading event:", error);
    }
}

async function loadBookingSeats(eventId) {
    const mapContainer = document.getElementById('seat-map');
    if (!mapContainer) return;

    try {
        const response = await fetch(`/api/events/${eventId}/seats/`);
        const seats = await response.json();

        if (seats.length === 0) {
            mapContainer.innerHTML = '<p style="color: #94a3b8; text-align: center;">No seats available for this event.</p>';
            return;
        }

        const rows = {};
        seats.forEach(seat => {
            if (!rows[seat.row_label]) {
                rows[seat.row_label] = [];
            }
            rows[seat.row_label].push(seat);
        });

        const sortedRowLabels = Object.keys(rows).sort();
        const maxCols = Math.max(...Object.values(rows).map(r => r.length));
        mapContainer.style.gridTemplateColumns = `repeat(${maxCols}, 40px)`;
        mapContainer.innerHTML = '';

        sortedRowLabels.forEach(rowLabel => {
            rows[rowLabel].sort((a, b) => parseInt(a.seat_number) - parseInt(b.seat_number));

            rows[rowLabel].forEach(seat => {
                const seatEl = document.createElement('div');
                const tierClass = seat.tier ? seat.tier.toLowerCase() : '';
                seatEl.className = `seat ${seat.status.toLowerCase()} ${tierClass}`;
                seatEl.textContent = `${seat.row_label}${seat.seat_number}`;
                seatEl.dataset.id = seat.id;
                seatEl.dataset.price = seat.price;
                seatEl.dataset.label = `${seat.row_label}${seat.seat_number}`;
                seatEl.title = `Seat ${seat.row_label}${seat.seat_number} - $${seat.price}`;

                if (seat.status === 'AVAILABLE') {
                    seatEl.onclick = () => toggleSeat(seatEl);
                }
                mapContainer.appendChild(seatEl);
            });
        });
    } catch (error) {
        console.error("Error loading seats:", error);
        mapContainer.innerHTML = '<p style="color: #ef4444;">Error loading seats.</p>';
    }
}

// Track multiple selected seats
let selectedSeats = [];

function toggleSeat(seatEl) {
    const seatId = seatEl.dataset.id;
    const existingIndex = selectedSeats.findIndex(s => s.id === seatId);

    if (existingIndex > -1) {
        selectedSeats.splice(existingIndex, 1);
        seatEl.classList.remove('selected');
    } else {
        selectedSeats.push({
            id: seatId,
            price: parseFloat(seatEl.dataset.price),
            label: seatEl.dataset.label
        });
        seatEl.classList.add('selected');
    }

    updateBookingSummary();
}

function updateBookingSummary() {
    const count = selectedSeats.length;
    const total = selectedSeats.reduce((sum, s) => sum + s.price, 0);
    const labels = selectedSeats.map(s => s.label).join(', ');

    document.getElementById('selected-seat-label').textContent = count > 0 ? labels : 'None';
    document.getElementById('total-price').textContent = `$${total.toFixed(2)}`;

    const btn = document.getElementById('confirm-booking-btn');
    if (btn) {
        if (count > 0) {
            btn.classList.remove('disabled');
            btn.textContent = `🎟️ Book ${count} Seat${count > 1 ? 's' : ''}`;
        } else {
            btn.classList.add('disabled');
            btn.textContent = '🎟️ Book Now';
        }
    }
}

const confirmBtn = document.getElementById('confirm-booking-btn');
if (confirmBtn) {
    confirmBtn.onclick = async () => {
        if (selectedSeats.length === 0) return;

        const token = localStorage.getItem('access_token');
        if (!token) {
            alert("Please login to book tickets.");
            window.location.href = '/login/';
            return;
        }

        confirmBtn.textContent = 'Processing...';
        confirmBtn.disabled = true;

        try {
            // Send all seat IDs in one request - backend handles bulk creation
            const seatIds = selectedSeats.map(s => parseInt(s.id));

            const response = await authenticatedFetch('/api/tickets/', {
                method: 'POST',
                body: JSON.stringify({
                    event_id: EVENT_ID,
                    seat_ids: seatIds
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(JSON.stringify(errData));
            }

            const result = await response.json();

            // Get ticket IDs from response
            const ticketIds = result.tickets.map(t => t.id).join(',');

            // Redirect to confirmation page with ticket IDs
            window.location.href = `/order-confirmation/?tickets=${ticketIds}`;

        } catch (error) {
            alert("Booking Failed: " + error.message);
            confirmBtn.textContent = `🎟️ Book ${selectedSeats.length} Seat${selectedSeats.length > 1 ? 's' : ''}`;
            confirmBtn.disabled = false;
        }
    };
}

// --- Order History Page ---
async function fetchOrders() {
    const container = document.getElementById('orders-container');
    const token = localStorage.getItem('access_token');

    if (!token || !container) return;

    try {
        const response = await authenticatedFetch('/api/tickets/');

        if (!response.ok) throw new Error('Failed to fetch orders');

        const tickets = await response.json();

        container.innerHTML = '';

        if (tickets.length === 0) {
            container.innerHTML = `
                <div class="no-orders">
                    <p>You haven't booked any tickets yet.</p>
                    <a href="/" class="cta-btn">Browse Events</a>
                </div>
            `;
            return;
        }

        tickets.forEach(ticket => {
            const date = new Date(ticket.purchase_date).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });

            const card = document.createElement('div');
            card.className = 'order-card';
            card.innerHTML = `
                <div class="order-header">
                    <span class="order-id">Ticket #${ticket.id}</span>
                    <span class="order-status ${ticket.payment_status.toLowerCase()}">${ticket.payment_status}</span>
                </div>
                <div class="order-details">
                    <h3>${ticket.event_title || 'Event'}</h3>
                    <p>Seat: <strong>${ticket.seat_label || 'N/A'}</strong></p>
                    <p>Booked: ${date}</p>
                </div>
                ${ticket.qr_code ? `<div class="order-qr"><img src="${ticket.qr_code}" alt="QR Code"></div>` : ''}
            `;
            container.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        container.innerHTML = '<div class="error">Error loading orders.</div>';
    }
}
