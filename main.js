// ----------------------
// Dashboard Variables
// ----------------------
let currentSignalId = null;

// ----------------------
// Chart Upload & Analysis
// ----------------------
async function uploadCharts(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('charts', files[i]);
    }

    const res = await fetch('/analyze', {
        method: 'POST',
        body: formData
    });
    const data = await res.json();
    updateDashboard(data);
}

// ----------------------
// Dashboard Update
// ----------------------
function updateDashboard(data) {
    currentSignalId = data.signal_id || "auto_" + Date.now();
    document.getElementById('market').innerText = data.context.market;
    document.getElementById('pair').innerText = data.context.pair;
    document.getElementById('session').innerText = data.context.session;
    document.getElementById('trend').innerText = data.context.vision.trend_bias;
    document.getElementById('direction').innerText = data.context.signal.direction;
    document.getElementById('entry').innerText = data.context.signal.entry;
    document.getElementById('tp').innerText = data.context.signal.TP;
    document.getElementById('sl').innerText = data.context.signal.SL;
    document.getElementById('timeframe').innerText = data.context.signal.timeframe;
}

// ----------------------
// Feedback Buttons
// ----------------------
document.getElementById('winBtn').addEventListener('click', async ()=>{
    if(!currentSignalId) return alert("No signal to feedback");
    const res = await fetch('/feedback', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
            signal_id: currentSignalId,
            market: document.getElementById('market').innerText,
            pair: document.getElementById('pair').innerText,
            result: 'win'
        })
    });
    const data = await res.json();
    alert(`Win recorded. Overall Accuracy: ${data.overall_accuracy}%`);
});

document.getElementById('lossBtn').addEventListener('click', async ()=>{
    if(!currentSignalId) return alert("No signal to feedback");
    const res = await fetch('/feedback', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
            signal_id: currentSignalId,
            market: document.getElementById('market').innerText,
            pair: document.getElementById('pair').innerText,
            result: 'loss'
        })
    });
    const data = await res.json();
    alert(`Loss recorded. Overall Accuracy: ${data.overall_accuracy}%`);
});

// ----------------------
// Fetch News & Alerts (Phase 11)
// ----------------------
async function updateNews() {
    const res = await fetch('/news');
    const newsData = await res.json();
    const newsContainer = document.getElementById('newsContainer');
    newsContainer.innerHTML = '';

    newsData.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('newsItem');
        div.innerHTML = `
            <b>${item.headline}</b> | Impact: ${item.impact_score} | Source: ${item.source}
        `;
        newsContainer.appendChild(div);

        // High-impact popup alert
        if(item.impact_score >= 5){
            toastAlert(`High Impact News: ${item.headline}`);
        }
    });
}

// ----------------------
// Toast / Popup Alert
// ----------------------
function toastAlert(message) {
    const toast = document.createElement('div');
    toast.classList.add('toastAlert');
    toast.innerText = message;
    document.body.appendChild(toast);

    setTimeout(()=>{toast.remove()}, 5000);
}

// ----------------------
// Initial Setup & Intervals
// ----------------------
document.getElementById('chartUpload').addEventListener('change', (e)=>{
    const files = e.target.files;
    if(files.length>0) uploadCharts(files);
});

// Fetch news every 60 seconds
updateNews();
setInterval(updateNews, 60000);
