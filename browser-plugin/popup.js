const noSelection = document.getElementById("noSelection");
const form = document.getElementById("form");
const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const sourceLabel = document.getElementById("sourceLabel");
const tagInput = document.getElementById("tagInput");
const addTagBtn = document.getElementById("addTagBtn");
const tagsContainer = document.getElementById("tags");
const availableTagsEl = document.getElementById("availableTags");
const saveBtn = document.getElementById("saveBtn");
const cancelBtn = document.getElementById("cancelBtn");
const statusEl = document.getElementById("status");

let tags = [];
let sourceUrl = "";
let allTags = [];

chrome.storage.session.get(["pendingData", "bilibiliData"], ({ pendingData, bilibiliData }) => {
  // 优先级: 右键/快捷键选中文本 > B站自动字幕 > 无内容
  if (pendingData && pendingData.text) {
    showForm(pendingData.title || "", pendingData.text, pendingData.url || "", "");
    chrome.storage.session.remove("pendingData");
  } else if (bilibiliData && bilibiliData.text) {
    const label = "— B站字幕 (" + (bilibiliData.lang || "") + ", " + (bilibiliData.lineCount || 0) + " 条)";
    showForm(bilibiliData.title || "", bilibiliData.text, bilibiliData.url || "", label);
    chrome.storage.session.remove("bilibiliData");
  } else {
    // 可能是正在加载，重试 3 次
    retryLoad(3);
  }
});

function showForm(title, text, url, label) {
  form.style.display = "flex";
  titleInput.value = title;
  contentInput.value = text;
  sourceUrl = url;
  sourceLabel.textContent = label;
  saveBtn.disabled = false;
  loadAvailableTags();
}

async function loadAvailableTags() {
  const { apiUrl } = await chrome.storage.sync.get("apiUrl");
  const baseUrl = apiUrl || "http://localhost:8001/api/v1";
  try {
    const res = await fetch(`${baseUrl}/tags`);
    if (res.ok) {
      allTags = await res.json();
      renderAvailableTags();
    }
  } catch {
    // 获取标签失败时静默忽略
  }
}

function renderAvailableTags() {
  availableTagsEl.innerHTML = allTags
    .map((t) => {
      const used = tags.includes(t.name);
      return `<span class="available-tag${used ? " used" : ""}" data-tag="${t.name}">${t.name}</span>`;
    })
    .join("");
  availableTagsEl.querySelectorAll(".available-tag:not(.used)").forEach((el) => {
    el.addEventListener("click", () => {
      const name = el.dataset.tag;
      if (name && !tags.includes(name)) {
        tags.push(name);
        renderTags();
        renderAvailableTags();
      }
    });
  });
}

function retryLoad(remaining) {
  setTimeout(() => {
    chrome.storage.session.get(["pendingData", "bilibiliData"], ({ pendingData, bilibiliData }) => {
      if (pendingData && pendingData.text) {
        showForm(pendingData.title || "", pendingData.text, pendingData.url || "", "");
        chrome.storage.session.remove("pendingData");
      } else if (bilibiliData && bilibiliData.text) {
        const label = "— B站字幕 (" + (bilibiliData.lang || "") + ", " + (bilibiliData.lineCount || 0) + " 条)";
        showForm(bilibiliData.title || "", bilibiliData.text, bilibiliData.url || "", label);
        chrome.storage.session.remove("bilibiliData");
      } else if (remaining > 0) {
        retryLoad(remaining - 1);
      } else {
        noSelection.querySelector("p").textContent = "请在 B站视频页面点击此插件，或者先在网页上选中内容。";
        noSelection.style.display = "block";
      }
    });
  }, 1200);
}

addTagBtn.addEventListener("click", () => {
  const t = tagInput.value.trim();
  if (t && !tags.includes(t)) {
    tags.push(t);
    renderTags();
    renderAvailableTags();
  }
  tagInput.value = "";
});

tagInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") addTagBtn.click();
});

cancelBtn.addEventListener("click", () => window.close());

saveBtn.addEventListener("click", async () => {
  const title = titleInput.value.trim();
  const content = contentInput.value.trim();
  if (!content) return;

  saveBtn.disabled = true;
  saveBtn.textContent = "保存中...";
  setStatus("", "");

  const { apiUrl } = await chrome.storage.sync.get("apiUrl");
  const baseUrl = apiUrl || "http://localhost:8001/api/v1";

  try {
    const res = await fetch(`${baseUrl}/ingest/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: title || "未命名",
        content,
        url: sourceUrl,
        tags,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`API ${res.status}: ${err}`);
    }

    setStatus("保存成功！", "success");
    setTimeout(() => window.close(), 600);
  } catch (e) {
    setStatus(`保存失败: ${e.message}`, "error");
    saveBtn.disabled = false;
    saveBtn.textContent = "保存";
  }
});

function renderTags() {
  tagsContainer.innerHTML = tags
    .map((t) => `<span class="tag">${t}<button data-tag="${t}">&times;</button></span>`)
    .join("");
  tagsContainer.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      tags = tags.filter((t) => t !== btn.dataset.tag);
      renderTags();
      renderAvailableTags();
    });
  });
}

function setStatus(msg, type) {
  statusEl.textContent = msg;
  statusEl.className = "status" + (type ? ` ${type}` : "");
}
