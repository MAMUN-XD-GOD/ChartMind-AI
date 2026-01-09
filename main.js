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

    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        updateDashboard(data);
    } catch (err) {
        console.error("Chart upload error:", err);
        toastAlert("Chart upload failed!");
    }
}

// ----------------------
// Dashboard Update
// ----------------------
function updateDashboard(data) {
    currentSignalId = data.signal_id || "auto_" + Date.now();
    
    const context = data.context;

    document.getElementById('market').innerText = context.market;
    document.getElementById('pair').innerText = context.pair;
    document.getElementById('session').innerText = context.session;
    document.getElementById('trend').innerText = context.vision.trend_bias;
    document.getElementById('direction').innerText = context.signal.direction;
    document.getElementById('entry').innerText = context.signal.entry;
    document.getElementById('tp').innerText = context.signal.TP;
    document.getElementById('sl').innerText = context.signal.SL;
    document.getElementById('timeframe').innerText = context.signal.timeframe;

    // Phase 12 → Probability Score
    const probEl = document.getElementById('probability');
    probEl.innerText = context.signal.probability + "%";
    if (context.signal.probability >= 80) {
        probEl.style.color = "green";
    } else if (context.signal.probability >= 50) {
        probEl.style.color = "orange";
    } else {
        probEl.style.color = "red";
    }

    // Highlight dashboard if high probability
    if(context.signal.probability >= 85){
        toastAlert(`High Confidence Signal: ${context.signal.direction} on ${context.pair}`);
    }
}

// ----------------------
// Feedback Buttons
// ----------------------
document.getElementById('winBtn').addEventListener('click', async ()=>{
    if(!currentSignalId) return alert("No signal to feedback");
    await sendFeedback('win');
});

document.getElementById('lossBtn').addEventListener('click', async ()=>{
    if(!currentSignalId) return alert("No signal to feedback");
    await sendFeedback('loss');
});

async function sendFeedback(result){
    try {
        const res = await fetch('/feedback', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({
                signal_id: currentSignalId,
                market: document.getElementById('market').innerText,
                pair: document.getElementById('pair').innerText,
                result: result
            })
        });
        const data = await res.json();
        toastAlert(`${result.toUpperCase()} recorded. Overall Accuracy: ${data.overall_accuracy}%`);
    } catch(err){
        console.error("Feedback error:", err);
        toastAlert("Feedback submission failed!");
    }
}

// ----------------------
// Fetch News & Alerts (Phase 11)
// ----------------------
async function updateNews() {
    try {
        const res = await fetch('/news');
        const newsData = await res.json();
        const newsContainer = document.getElementById('newsContainer');
        newsContainer.innerHTML = '';

        newsData.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('newsItem');
            div.innerHTML = `<b>${item.headline}</b> | Impact: ${item.impact_score} | Source: ${item.source}`;
            newsContainer.appendChild(div);

            // High-impact popup alert
            if(item.impact_score >= 5){
                toastAlert(`High Impact News: ${item.headline}`);
            }
        });
    } catch(err){
        console.error("News fetch error:", err);
    }
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
