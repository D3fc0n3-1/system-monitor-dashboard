const serverListContainer = document.getElementById('server-list');
const themeToggleButton = document.getElementById('theme-toggle-button');
const bodyElement = document.body;

// const backendUrl = 'http://127.0.0.1:8000/servers';
const backendUrl = '/servers'; //
const refreshInterval = 5000; // Refresh every 5 seconds
const themeLocalStorageKey = 'dashboard-theme'; // Key for localStorage

// --- Theme Handling ---

function applyTheme(theme) {
    if (theme === 'dark') {
        bodyElement.classList.add('dark-theme');
        themeToggleButton.textContent = 'Light Mode'; // Set button text for dark mode
    } else {
        bodyElement.classList.remove('dark-theme');
        themeToggleButton.textContent = 'Dark Mode'; // Set button text for light mode
    }
}

function toggleTheme() {
    let currentTheme = 'light';
    if (bodyElement.classList.contains('dark-theme')) {
        // It's currently dark, switch to light
        currentTheme = 'light';
        localStorage.setItem(themeLocalStorageKey, 'light');
    } else {
        // It's currently light, switch to dark
        currentTheme = 'dark';
        localStorage.setItem(themeLocalStorageKey, 'dark');
    }
    applyTheme(currentTheme);
}

// Check for saved theme on initial load
const savedTheme = localStorage.getItem(themeLocalStorageKey);
if (savedTheme) {
    applyTheme(savedTheme); // Apply saved theme
} else {
    applyTheme('light'); // Default to light theme if nothing is saved
    // Optional: Check system preference if no theme is saved
    // if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    //     applyTheme('dark');
    // } else {
    //     applyTheme('light');
    // }
}


// Add event listener for the button
themeToggleButton.addEventListener('click', toggleTheme);


// --- Server Data Fetching ---

async function fetchServerData() {
    console.log("Fetching server data...");
    try {
        const response = await fetch(backendUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const servers = await response.json();
        console.log("Data received:", servers);
        updateServerList(servers);
    } catch (error) {
        console.error("Failed to fetch server data:", error);
        serverListContainer.innerHTML = `<p class="error-message">Error loading server data: ${error.message}. Please check if the backend is running.</p>`;
    }
}

function updateServerList(servers) {
    serverListContainer.innerHTML = '';

    if (!servers || servers.length === 0) {
        serverListContainer.innerHTML = '<p>No server data available.</p>';
        return;
    }

    servers.forEach(server => {
        const card = document.createElement('div');
        card.classList.add('server-card');

        let statusClass = 'status-offline';
        let statusText = server.status?.toUpperCase() || 'UNKNOWN'; // Safer access
        if (server.status === 'online') {
            statusClass = 'status-online';
        } else if (server.status === 'error') {
            statusClass = 'status-error';
        }

        let cardContent = `
            <h2>${server.name || 'N/A'}</h2>
            <div class="status ${statusClass}">${statusText}</div>
        `;

        if (server.status === 'online') {
            // Use optional chaining (?.) and nullish coalescing (??) for safety
            cardContent += `
                <p><span class="label">CPU:</span> ${server.cpu_usage_percent?.toFixed(1) ?? 'N/A'}%</p>
                <p><span class="label">Memory:</span> ${server.mem_usage_percent?.toFixed(1) ?? 'N/A'}%</p>
                <p><span class="label">Disk I/O:</span> ${server.disk_io_rate?.toFixed(2) ?? 'N/A'} MB/s</p>
                <p><span class="label">Net I/O:</span> ${server.net_io_rate?.toFixed(2) ?? 'N/A'} Mbps</p>
            `;
        } else if (server.error) {
             cardContent += `<p><span class="label">Error:</span> ${server.error}</p>`;
        }

        card.innerHTML = cardContent;
        serverListContainer.appendChild(card);
    });
}

// Initial fetch
fetchServerData();

// Set interval for periodic refresh
setInterval(fetchServerData, refreshInterval);