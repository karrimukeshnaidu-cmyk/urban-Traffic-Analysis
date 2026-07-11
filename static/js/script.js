// State variables for charts
const chartInstances = {};
let fullscreenChart = null;

// Modern theme-based color palettes
const themes = {
    light: {
        text: '#1e293b',
        mutedText: '#64748b',
        gridLines: '#e2e8f0',
        cardBg: '#ffffff',
        accent: '#4f46e5',
        chartColors: {
            primary: 'rgba(79, 70, 229, 0.85)',
            secondary: 'rgba(139, 92, 246, 0.85)',
            trend: 'rgba(244, 63, 94, 0.85)',
            junctions: [
                'rgba(20, 184, 166, 0.85)', // Teal
                'rgba(59, 130, 246, 0.85)', // Blue
                'rgba(168, 85, 247, 0.85)', // Purple
                'rgba(249, 115, 22, 0.85)'  // Orange
            ],
            peak: ['rgba(239, 68, 68, 0.85)', 'rgba(16, 185, 129, 0.85)'], // Red, Green
            week: ['rgba(59, 130, 246, 0.85)', 'rgba(245, 158, 11, 0.85)']  // Blue, Gold
        }
    },
    dark: {
        text: '#f8fafc',
        mutedText: '#94a3b8',
        gridLines: 'rgba(255, 255, 255, 0.08)',
        cardBg: '#111827',
        accent: '#6366f1',
        chartColors: {
            primary: 'rgba(99, 102, 241, 0.9)',
            secondary: 'rgba(167, 139, 250, 0.9)',
            trend: 'rgba(251, 113, 133, 0.9)',
            junctions: [
                'rgba(45, 212, 191, 0.9)', // Teal
                'rgba(96, 165, 250, 0.9)', // Blue
                'rgba(192, 132, 252, 0.9)', // Purple
                'rgba(251, 146, 60, 0.9)'  // Orange
            ],
            peak: ['rgba(248, 113, 113, 0.9)', 'rgba(52, 211, 153, 0.9)'], // Red, Green
            week: ['rgba(96, 165, 250, 0.9)', 'rgba(251, 191, 36, 0.9)']  // Blue, Gold
        }
    }
};

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
    // 1. Set theme from local storage
    const savedTheme = localStorage.getItem("theme") || "light";
    document.body.setAttribute("data-theme", savedTheme);
    updateThemeButtonUI(savedTheme);

    // 2. Set default date picker to today's date if not set
    const dateInput = document.getElementById("pred-date");
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
    }

    // 3. Initialize all 7 charts
    initializeCharts(savedTheme);
});

// Theme Management
function toggleTheme() {
    const currentTheme = document.body.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    
    document.body.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateThemeButtonUI(newTheme);
    
    // Update chart styles dynamically without reloading
    updateChartsTheme(newTheme);
}

function updateThemeButtonUI(theme) {
    const icon = document.getElementById("themeBtnIcon");
    const text = document.getElementById("themeBtnText");
    
    if (theme === "dark") {
        if (icon) icon.innerText = "☀️";
        if (text) text.innerText = "Light Mode";
    } else {
        if (icon) icon.innerText = "🌙";
        if (text) text.innerText = "Dark Mode";
    }
}

// Chart Initializations
function getChartOptions(themeName, titleText) {
    const theme = themes[themeName];
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: theme.text,
                    font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }
                }
            },
            tooltip: {
                backgroundColor: themeName === 'dark' ? '#1f2937' : '#0f172a',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: theme.gridLines,
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
                titleFont: { family: 'Plus Jakarta Sans', weight: '700' },
                bodyFont: { family: 'Plus Jakarta Sans' }
            }
        },
        scales: {
            x: {
                grid: { color: theme.gridLines },
                ticks: {
                    color: theme.mutedText,
                    font: { family: 'Plus Jakarta Sans', size: 10 }
                }
            },
            y: {
                grid: { color: theme.gridLines },
                ticks: {
                    color: theme.mutedText,
                    font: { family: 'Plus Jakarta Sans', size: 10 }
                }
            }
        }
    };
}

function hideSkeleton(chartId) {
    const skel = document.getElementById(`skeleton-${chartId}`);
    if (skel) {
        skel.style.opacity = '0';
        setTimeout(() => {
            skel.style.display = 'none';
        }, 500);
    }
}

function initializeCharts(themeName) {
    const t = themes[themeName];
    const baseOpts = (title) => getChartOptions(themeName, title);

    // 1. Traffic by Hour (Line)
    chartInstances['hourChart'] = new Chart(document.getElementById("hourChart"), {
        type: 'line',
        data: {
            labels: hours.map(h => `${h.toString().padStart(2, '0')}:00`),
            datasets: [{
                label: 'Avg Vehicles',
                data: hour_values,
                borderColor: t.accent,
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: t.accent
            }]
        },
        options: baseOpts('Traffic by Hour')
    });
    hideSkeleton('hourChart');

    // 2. Traffic by Day (Bar)
    chartInstances['dayChart'] = new Chart(document.getElementById("dayChart"), {
        type: 'bar',
        data: {
            labels: days,
            datasets: [{
                label: 'Avg Vehicles',
                data: day_values,
                backgroundColor: t.chartColors.secondary,
                borderRadius: 6
            }]
        },
        options: baseOpts('Traffic by Day')
    });
    hideSkeleton('dayChart');

    // 3. Traffic by Location (Bar)
    chartInstances['locChart'] = new Chart(document.getElementById("locChart"), {
        type: 'bar',
        data: {
            labels: locations.map(l => `Junction ${l}`),
            datasets: [{
                label: 'Avg Vehicles',
                data: loc_values,
                backgroundColor: t.chartColors.junctions,
                borderRadius: 6
            }]
        },
        options: baseOpts('Traffic by Junction')
    });
    hideSkeleton('locChart');

    // 4. Peak vs Non-Peak (Doughnut)
    chartInstances['peakChart'] = new Chart(document.getElementById("peakChart"), {
        type: 'doughnut',
        data: {
            labels: peak_labels,
            datasets: [{
                data: peak_values,
                backgroundColor: t.chartColors.peak,
                borderWidth: 0
            }]
        },
        options: {
            ...baseOpts('Peak vs Non-Peak'),
            cutout: '65%'
        }
    });
    hideSkeleton('peakChart');

    // 5. Top 5 Locations (Horizontal Bar)
    chartInstances['topChart'] = new Chart(document.getElementById("topChart"), {
        type: 'bar',
        data: {
            labels: top_locations.map(l => `Junction ${l}`),
            datasets: [{
                label: 'Avg Traffic Load',
                data: top_values,
                backgroundColor: t.chartColors.primary,
                borderRadius: 6
            }]
        },
        options: {
            ...baseOpts('Top 5 Junctions'),
            indexAxis: 'y'
        }
    });
    hideSkeleton('topChart');

    // 6. Traffic Trend (Line - Date-wise)
    chartInstances['trendChart'] = new Chart(document.getElementById("trendChart"), {
        type: 'line',
        data: {
            labels: trend_dates,
            datasets: [{
                label: 'Traffic Load',
                data: trend_values,
                borderColor: t.chartColors.trend,
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 2,
                tension: 0.1
            }]
        },
        options: baseOpts('Trend')
    });
    hideSkeleton('trendChart');

    // 7. Weekday vs Weekend (Pie)
    chartInstances['weekChart'] = new Chart(document.getElementById("weekChart"), {
        type: 'pie',
        data: {
            labels: week_labels,
            datasets: [{
                data: week_values,
                backgroundColor: t.chartColors.week,
                borderWidth: 0
            }]
        },
        options: baseOpts('Weekday vs Weekend')
    });
    hideSkeleton('weekChart');
}

function updateChartsTheme(themeName) {
    const t = themes[themeName];
    
    Object.keys(chartInstances).forEach(key => {
        const chart = chartInstances[key];
        
        // Update general fonts and gridlines
        chart.options.plugins.legend.labels.color = t.text;
        chart.options.plugins.tooltip.backgroundColor = themeName === 'dark' ? '#1f2937' : '#0f172a';
        chart.options.plugins.tooltip.borderColor = t.gridLines;
        
        if (chart.options.scales) {
            if (chart.options.scales.x) {
                chart.options.scales.x.grid.color = t.gridLines;
                chart.options.scales.x.ticks.color = t.mutedText;
            }
            if (chart.options.scales.y) {
                chart.options.scales.y.grid.color = t.gridLines;
                chart.options.scales.y.ticks.color = t.mutedText;
            }
        }
        
        // Update specific datasets colors
        if (key === 'hourChart') {
            chart.data.datasets[0].borderColor = t.accent;
            chart.data.datasets[0].pointBackgroundColor = t.accent;
        } else if (key === 'dayChart') {
            chart.data.datasets[0].backgroundColor = t.chartColors.secondary;
        } else if (key === 'locChart') {
            chart.data.datasets[0].backgroundColor = t.chartColors.junctions;
        } else if (key === 'peakChart') {
            chart.data.datasets[0].backgroundColor = t.chartColors.peak;
        } else if (key === 'topChart') {
            chart.data.datasets[0].backgroundColor = t.chartColors.primary;
        } else if (key === 'trendChart') {
            chart.data.datasets[0].borderColor = t.chartColors.trend;
        } else if (key === 'weekChart') {
            chart.data.datasets[0].backgroundColor = t.chartColors.week;
        }
        
        chart.update();
    });
}

// Fullscreen Chart Modal Management
function openFullscreen(chartId, title) {
    const originalChart = chartInstances[chartId];
    if (!originalChart) return;
    
    const modal = document.getElementById("fullscreenModal");
    const modalTitle = document.getElementById("modalChartTitle");
    const canvas = document.getElementById("fullscreenCanvas");
    
    modalTitle.innerText = title;
    modal.classList.add("active");
    
    // Destroy previous fullscreen chart if exists
    if (fullscreenChart) {
        fullscreenChart.destroy();
    }
    
    const currentTheme = document.body.getAttribute("data-theme") || "light";
    const t = themes[currentTheme];
    
    // Clone configuration for the fullscreen modal view
    const config = {
        type: originalChart.config.type,
        data: JSON.parse(JSON.stringify(originalChart.data)), // Deep copy data
        options: getChartOptions(currentTheme, title)
    };
    
    // Re-bind chart coloring manually as JSON cloning loses some color attributes
    config.data.datasets.forEach((dataset, idx) => {
        const origDataset = originalChart.data.datasets[idx];
        dataset.backgroundColor = origDataset.backgroundColor;
        dataset.borderColor = origDataset.borderColor;
        if (origDataset.pointBackgroundColor) {
            dataset.pointBackgroundColor = origDataset.pointBackgroundColor;
        }
    });

    if (config.type === 'doughnut') {
        config.options.cutout = '65%';
    }
    
    // Create new chart instance for modal canvas
    fullscreenChart = new Chart(canvas, config);
}

function closeFullscreen() {
    const modal = document.getElementById("fullscreenModal");
    modal.classList.remove("active");
    
    if (fullscreenChart) {
        setTimeout(() => {
            fullscreenChart.destroy();
            fullscreenChart = null;
        }, 300);
    }
}

// Prediction Panel Interactions
function updateHourLabel(val) {
    const hourLabel = document.getElementById("hourLabel");
    if (hourLabel) {
        hourLabel.innerText = `${val.toString().padStart(2, '0')}:00`;
    }
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function getPrediction(event) {
    event.preventDefault();
    
    const location = document.getElementById("pred-location").value;
    const date = document.getElementById("pred-date").value;
    const hour = document.getElementById("pred-hour").value;
    
    const loader = document.getElementById("predLoader");
    const emptyState = document.getElementById("predEmptyState");
    const output = document.getElementById("predOutput");
    
    // Transition UI state
    emptyState.style.display = "none";
    output.style.display = "none";
    loader.style.display = "block";
    
    // Build payload or query string (GET predict endpoint)
    const url = `/predict?location=${location}&date=${date}&hour=${hour}`;
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || 'API error') });
            }
            return response.json();
        })
        .then(res => {
            loader.style.display = "none";
            output.style.display = "flex";
            
            const data = res.data;
            
            // Set prediction count-up animation
            const predVehiclesEl = document.getElementById("predictedVehicles");
            animateValue(predVehiclesEl, 0, data.predicted_vehicles, 600);
            
            // Set Badge Category
            const badge = document.getElementById("trafficCategoryBadge");
            badge.innerText = `${data.traffic_category} Traffic`;
            badge.className = "badge"; // reset classes
            
            if (data.traffic_category === "Low") {
                badge.classList.add("badge-low");
            } else if (data.traffic_category === "Medium") {
                badge.classList.add("badge-medium");
            } else {
                badge.classList.add("badge-high");
            }
            
            // Details Update
            document.getElementById("predDetailLocation").innerText = `Junction ${data.location}`;
            document.getElementById("predDetailDay").innerText = `${data.day_name}`;
            document.getElementById("predDetailPeakHour").innerText = `${data.peak_hour_formatted}`;
            document.getElementById("predDetailPeakVolume").innerText = `${data.peak_volume} vehicles`;
        })
        .catch(err => {
            loader.style.display = "none";
            emptyState.style.display = "flex";
            alert(`Prediction Failed: ${err.message}`);
        });
}
