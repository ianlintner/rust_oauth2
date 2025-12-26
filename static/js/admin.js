// Admin Dashboard JavaScript

// Fetch and update dashboard statistics
async function updateDashboardStats() {
    try {
        const response = await fetch('/admin/api/dashboard');
        const data = await response.json();
        
        document.getElementById('total-clients').textContent = data.total_clients || 0;
        document.getElementById('total-users').textContent = data.total_users || 0;
        document.getElementById('active-tokens').textContent = data.active_tokens || 0;
        document.getElementById('total-requests').textContent = data.total_requests || 0;
    } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
    }
}

// Initialize charts
function initCharts() {
    const tokenCtx = document.getElementById('tokenChart');
    if (tokenCtx) {
        new Chart(tokenCtx, {
            type: 'line',
            data: {
                labels: ['1h ago', '50m', '40m', '30m', '20m', '10m', 'Now'],
                datasets: [{
                    label: 'Tokens Issued',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    const requestCtx = document.getElementById('requestChart');
    if (requestCtx) {
        new Chart(requestCtx, {
            type: 'bar',
            data: {
                labels: ['1h ago', '50m', '40m', '30m', '20m', '10m', 'Now'],
                datasets: [{
                    label: 'Requests',
                    data: [65, 78, 90, 81, 96, 105, 112],
                    backgroundColor: '#10b981',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Fetch and update activity table
async function updateActivityTable() {
    try {
        const response = await fetch('/admin/api/activity');
        const activities = await response.json();
        
        const tbody = document.querySelector('#activity-table tbody');
        if (activities && activities.length > 0) {
            tbody.innerHTML = activities.map(activity => `
                <tr>
                    <td>${new Date(activity.timestamp).toLocaleString()}</td>
                    <td>${activity.event}</td>
                    <td>${activity.client_id}</td>
                    <td>${activity.user_id || 'N/A'}</td>
                    <td><span class="status-badge status-${activity.status}">${activity.status}</span></td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="5">No recent activity</td></tr>';
        }
    } catch (error) {
        console.error('Failed to fetch activity:', error);
        const tbody = document.querySelector('#activity-table tbody');
        tbody.innerHTML = '<tr><td colspan="5">Failed to load activity</td></tr>';
    }
}

// Auto-refresh dashboard
function startAutoRefresh() {
    // Refresh stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Refresh activity every 10 seconds
    setInterval(updateActivityTable, 10000);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateDashboardStats();
    initCharts();
    updateActivityTable();
    startAutoRefresh();
});
