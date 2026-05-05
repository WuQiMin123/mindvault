// 右键菜单
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "save-to-mindvault",
    title: "保存到 MindVault",
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "save-to-mindvault" && info.selectionText) {
    openPopup({ text: info.selectionText, title: tab?.title || "", url: tab?.url || "" });
  }
});

chrome.commands.onCommand.addListener((command) => {
  if (command === "save-to-mindvault") {
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (!tab?.id) return;
      chrome.scripting.executeScript(
        {
          target: { tabId: tab.id },
          func: () => window.getSelection()?.toString() || "",
        },
        (results) => {
          const text = results?.[0]?.result || "";
          if (!text) return;
          openPopup({ text, title: tab.title || "", url: tab.url || "" });
        }
      );
    });
  }
});

// 接收 content script 发来的 B站字幕数据
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type === "bilibiliData" && message.data) {
    chrome.storage.session.set({ bilibiliData: message.data });
  }
});

function openPopup(data) {
  chrome.storage.session.set({ pendingData: data }, () => {
    chrome.action.openPopup();
  });
}
