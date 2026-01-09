const analyzeBtn = document.getElementById('analyzeBtn');
const chartUpload = document.getElementById('chartUpload');

analyzeBtn.addEventListener('click', async () => {
    const files = chartUpload.files;
    if(files.length === 0){ alert('Please upload chart'); return; }

    const formData = new FormData();
    for(let i=0;i<files.length;i++){ formData.append('charts', files[i]); }

    const res = await fetch('/analyze', { method:'POST', body: formData });
    const data = await res.json();

    // Update Dashboard
    document.getElementById('market').innerText = data.context.market;
    document.getElementById('pair').innerText = data.context.pair;
    document.getElementById('session').innerText = data.context.session;
    document.getElementById('trend').innerText = data.context.vision.trend_bias;
    document.getElementById('direction').innerText = data.context.signal.direction;
    document.getElementById('entry').innerText = data.context.signal.entry;
    document.getElementById('tp').innerText = data.context.signal.TP;
    document.getElementById('sl').innerText = data.context.signal.SL;
    document.getElementById('timeframe').innerText = data.context.signal.timeframe;
});

// Feedback buttons
document.getElementById('winBtn').addEventListener('click',()=>{ alert('Win recorded'); });
document.getElementById('lossBtn').addEventListener('click',()=>{ alert('Loss recorded'); });
