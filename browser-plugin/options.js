const apiUrlInput = document.getElementById("apiUrl");
const saveBtn = document.getElementById("saveBtn");
const statusEl = document.getElementById("status");

chrome.storage.sync.get("apiUrl", ({ apiUrl }) => {
  if (apiUrl) apiUrlInput.value = apiUrl;
});

saveBtn.addEventListener("click", async () => {
  const apiUrl = apiUrlInput.value.trim();
  await chrome.storage.sync.set({ apiUrl });
  statusEl.textContent = "已保存";
  statusEl.className = "status success";
  setTimeout(() => { statusEl.className = "status"; }, 2000);
});
