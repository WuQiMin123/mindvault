// B站字幕提取 content script
// 从 URL 提取 bvid，通过 B站公开 API 获取视频信息和字幕数据
(function () {
  'use strict';

  const BVID_RE = /\/video\/(BV\w+)/;

  async function extract(bvid) {
    try {
      // 1. view API 获取 cid / aid / title
      const viewResp = await fetch('https://api.bilibili.com/x/web-interface/view?bvid=' + bvid);
      const viewJson = await viewResp.json();
      if (viewJson.code !== 0 || !viewJson.data) {
        console.log('[MindVault] view API 失败:', viewJson.message);
        return;
      }

      const { aid, cid, title } = viewJson.data;
      if (!cid || !aid) {
        console.log('[MindVault] 缺少 cid/aid');
        return;
      }

      // 2. player API 获取字幕列表（带 cookie）
      const params = new URLSearchParams({ cid, aid });
      const subResp = await fetch('https://api.bilibili.com/x/player/v2?' + params, {
        credentials: 'include',
      });
      const subJson = await subResp.json();
      if (subJson.code !== 0 || !subJson.data?.subtitle?.subtitles?.length) {
        console.log('[MindVault] 无字幕');
        return;
      }

      // 3. 选第一个非 close 的字幕
      const sub = subJson.data.subtitle.subtitles.find(s => s.lan !== 'close');
      if (!sub) return;

      // 4. 获取字幕正文
      const subUrl = sub.subtitle_url.startsWith('//')
        ? 'https:' + sub.subtitle_url
        : sub.subtitle_url;

      const textResp = await fetch(subUrl);
      const textData = await textResp.json();
      if (!textData?.body?.length) return;

      const lines = textData.body.map(item => item.content);
      const text = lines.join('\n');

      // 5. 发给 background 存入 session storage
      chrome.runtime.sendMessage({
        type: 'bilibiliData',
        data: {
          title: title,
          text: text,
          url: location.href,
          lang: sub.lan_doc || '未知',
          lineCount: textData.body.length,
        },
      });
      console.log('[MindVault] B站字幕已提取 ✓', title, '—', textData.body.length, '条,', sub.lan_doc);
    } catch (err) {
      console.error('[MindVault] 提取失败:', err);
    }
  }

  // 页面初始化时提取
  const m = location.pathname.match(BVID_RE);
  if (m) extract(m[1]);

  // 监听 SPA 路由变化（B站内部导航换视频时重新提取）
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      const m2 = location.pathname.match(BVID_RE);
      if (m2) extract(m2[1]);
    }
  }).observe(document, { subtree: true, childList: true });
})();
