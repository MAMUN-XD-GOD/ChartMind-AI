const upload = document.getElementById("chartUpload");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const result = document.getElementById("result");

let selectedFile = null;

upload.addEventListener("change", () => {
  preview.innerHTML = "";
  selectedFile = upload.files[0];
  if (!selectedFile) return;

  const img = document.createElement("img");
  img.src = URL.createObjectURL(selectedFile);
  preview.appendChild(img);
  analyzeBtn.disabled = false;
});

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  analyzeBtn.innerText = "Analyzing...";
  analyzeBtn.disabled = true;

  const formData = new FormData();
  formData.append("chart", selectedFile);
  formData.append("market", "binary");
  formData.append("timestamp", Math.floor(Date.now() / 1000));

  try {
    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    result.classList.remove("hidden");

    if (data.status === "blocked") {
      document.getElementById("signal").innerText = "NO TRADE ❌";
      document.getElementById("confidence").innerText = data.reason;
    } else if (data.status === "warning") {
      document.getElementById("signal").innerText = "RISKY ⚠️";
      document.getElementById("confidence").innerText =
        "Late by " + data.delay_sec + " sec";
    } else {
      document.getElementById("signal").innerText =
        data.signal + " ⬆";
      document.getElementById("confidence").innerText =
        "Confidence: " + data.confidence + "%";
    }
  } catch (err) {
    alert("Backend not running");
  }

  analyzeBtn.innerText = "Analyze Chart";
  analyzeBtn.disabled = false;
});
