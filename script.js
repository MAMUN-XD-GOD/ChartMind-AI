const upload = document.getElementById("chartUpload");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const result = document.getElementById("result");

upload.addEventListener("change", () => {
  preview.innerHTML = "";
  const file = upload.files[0];
  if (!file) return;

  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  preview.appendChild(img);
  analyzeBtn.disabled = false;
});

analyzeBtn.addEventListener("click", () => {
  analyzeBtn.innerText = "Analyzing...";
  setTimeout(() => {
    result.classList.remove("hidden");
    document.getElementById("signal").innerText = "CALL ⬆";
    document.getElementById("confidence").innerText = "Confidence: 68%";
    analyzeBtn.innerText = "Analyze Chart";
  }, 2000);
});
