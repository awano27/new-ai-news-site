// Externalized UI logic for docs index
(() => {
  const tierTexts = { 1: '高信頼ソース', 2: '一般ソース' };
  const metricLabels = {
    engineer: ['技術的新規性', '実装可能性', '再現性', '実務寄与', '学習価値'],
    business: ['事業影響度', '投資判断材料', '戦略的価値', '実現可能性', 'リスク評価']
  };
  const breakdownOrder = {
    engineer: ['temporal', 'relevance', 'trust', 'quality', 'actionability'],
    business: ['quality', 'relevance', 'trust', 'temporal', 'actionability']
  };

  let currentPersona = 'engineer';
  let filteredArticles = [];

  function getPersonaScore(article) {
    const evalData = article.evaluation && article.evaluation[currentPersona];
    return evalData ? evalData.total_score : 0;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text ?? '';
    return div.innerHTML;
  }

  function getRecommendationText(rec) {
    const texts = { x: 'X最新', must_read: '必読', recommended: '注目', consider: '参考', skip: '見送り' };
    return texts[rec] || rec;
  }
  function getRecommendationDesc(rec) {
    const desc = {
      x: 'Xの注目ポスト',
      must_read: '重要で読むべき記事',
      recommended: '有益でおすすめ・注目記事',
      consider: '時間があれば参考にする記事',
      skip: '今回は優先度が低い記事'
    };
    return desc[rec] || '';
  }
  function getRecommendationHeading(rec) {
    return `<span>${getRecommendationText(rec)}</span><span class="rec-subtext">${getRecommendationDesc(rec)}</span>`;
  }

  function createArticleCard(article) {
    const card = document.createElement('div');
    card.className = 'article-card';
    const personaEval = (article.evaluation && article.evaluation[currentPersona]) || {};
    const breakdown = personaEval.breakdown || {};
    const totalPercentage = Math.round((personaEval.total_score || 0) * 100);
    const order = breakdownOrder[currentPersona] || ['quality','relevance','temporal','trust','actionability'];
    let breakdownHtml = '';
    order.forEach((key, idx) => {
      const val = Math.round(((breakdown[key] || 0) * 100));
      const label = (metricLabels[currentPersona] && metricLabels[currentPersona][idx]) || key;
      breakdownHtml += `<div class="score-item"><div class="score-value">${val}</div><div class="score-label">${label}</div></div>`;
    });
    const rec = personaEval.recommendation || 'consider';
    const recIcon = rec === 'consider' ? '<span class="icon info-icon"></span>' : (rec === 'skip' ? '<span class="icon skip-icon"></span>' : '');
    card.innerHTML = `
      <span class="source-tier tier-${article.source_tier}">${tierTexts[article.source_tier] || ''}</span>
      <h3 class="article-title">
        <a href="${article.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a>
      </h3>
      <div class="article-meta">
        <span>${escapeHtml(article.source)}</span> • <span>${article.published_date}</span>
      </div>
      <div class="article-content">${escapeHtml(article.content)}</div>
      <div class="evaluation-panel">
        <div class="score-display">
          <div class="total-score">${totalPercentage}</div>
          <div class="score-label-text">総合評価</div>
          <div class="score-bar"><div class="score-bar-fill" style="width: ${totalPercentage}%"></div></div>
        </div>
        <div class="score-breakdown">${breakdownHtml}</div>
        <div class="recommendation rec-${rec}" title="${getRecommendationDesc(rec)}" aria-label="${getRecommendationDesc(rec)}">${recIcon}${getRecommendationText(rec)}</div>
      </div>
      ${Array.isArray(article.tags) && article.tags.length ? `
      <div class="tags">
        ${article.tags.slice(0, 6).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
      </div>
      ` : ''}
    `;
    return card;
  }

  function renderArticles() {
    const container = document.getElementById('articles-container');
    if (!container) return;
    container.innerHTML = '';

    const isX = (a) => (typeof a.source === 'string' && a.source.startsWith('X(@')) || (Array.isArray(a.tags) && a.tags.includes('x_post'));
    const xItems = filteredArticles.filter(isX);
    const rest = filteredArticles.filter(a => !isX(a));

    const groups = { x: xItems, must_read: [], recommended: [], consider: [], skip: [] };
    rest.forEach(article => {
      const rec = (article.evaluation && article.evaluation[currentPersona] && article.evaluation[currentPersona].recommendation) || 'consider';
      (groups[rec] || groups.consider).push(article);
    });

    const order = ['x','must_read','recommended','consider','skip'];
    order.forEach(rec => {
      const items = groups[rec];
      if (!items || items.length === 0) return;

      const section = document.createElement('section');
      section.className = `rec-section rec-${rec}` + (rec === 'skip' ? ' collapsed' : '');
      section.dataset.rec = rec;
      section.id = `sec-${rec}`;

      const heading = document.createElement('h2');
      heading.className = `rec-heading rec-${rec}`;
      heading.setAttribute('role','button');
      heading.setAttribute('tabindex','0');
      heading.dataset.rec = rec;
      heading.innerHTML = `${getRecommendationHeading(rec)}<span class="meta"><span class="count">${items.length}件</span><span class="caret">▾</span></span>`;
      section.appendChild(heading);

      const content = document.createElement('div');
      content.className = 'rec-content ' + ((rec === 'must_read' || rec === 'recommended') ? 'cards-grid' : 'compact-list');

      if (rec === 'must_read' || rec === 'recommended') {
        const sorted = items.sort((a,b) => getPersonaScore(b) - getPersonaScore(a));
        const limitTop = 8;
        sorted.forEach((article, idx) => {
          const el = createArticleCard(article);
          // inject readable summary into cards
          const baseText = article.content || '';
          const origText = article.original_content || '';
          const summaryLead = highlightKeywords(extractLead(baseText || origText));
          const labeled = deriveLabeledKeyPoints(baseText || origText, 3);
          const bullets = labeled.map(({label,text}) => `${label?`<span class=\\\"kp-label\\\">${label}</span> `:''}${highlightKeywords(text)}`);
          const showOriginalToggle = !!origText && isJapanese(baseText);
          const headerAfter = el.querySelector('.article-meta');
          if (headerAfter) {
            const sum = document.createElement('div');
            sum.className = 'summary';
            sum.innerHTML = `${summaryLead ? `<p class=\"summary-lead\">${summaryLead}</p>` : ''}${bullets.length ? `<ul class=\"key-points\">${bullets.map(b=>`<li>${b}</li>`).join('')}</ul>` : ''}${showOriginalToggle ? `<button class=\"original-toggle\" type=\"button\">英語原文を表示</button><div class=\"original-excerpt\">${escapeHtml((origText||'').slice(0,500))}${(origText||'').length>500?'…':''}</div>` : ''}`;
            headerAfter.insertAdjacentElement('afterend', sum);
            const ac = el.querySelector('.article-content');
            if (ac) ac.style.display = 'none';
          }
          if (idx >= limitTop) el.classList.add('extra');
          content.appendChild(el);
        });
      } else {
        const sorted = items.sort((a,b) => getPersonaScore(b) - getPersonaScore(a));
        const limit = rec === 'x' ? 10 : 5;
        sorted.forEach((article, idx) => content.appendChild(createCompactItem(article, idx >= limit)));
      }

      section.appendChild(content);
      if (rec === 'x' && items.length > 10) {
        const btn = document.createElement('button');
        btn.className = 'show-more';
        btn.type = 'button';
        btn.setAttribute('aria-expanded', 'false');
        btn.textContent = 'もっと見る';
        section.appendChild(btn);
      }
      if ((rec === 'consider' || rec === 'skip') && items.length > 5) {
        const btn = document.createElement('button');
        btn.className = 'show-more';
        btn.type = 'button';
        btn.setAttribute('aria-expanded', 'false');
        btn.textContent = 'もっと見る';
        section.appendChild(btn);
      }
      if ((rec === 'must_read' || rec === 'recommended') && items.length > 8) {
        const btn = document.createElement('button');
        btn.className = 'show-more';
        btn.type = 'button';
        btn.setAttribute('aria-expanded', 'false');
        btn.textContent = 'もっと見る';
        section.appendChild(btn);
      }
      container.appendChild(section);
    });

    // Update nav counts
    updateRecNavCounts(groups);

    if (!container.children.length) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.textContent = '検索条件に一致する記事がありません';
      container.appendChild(empty);
    }
  }

  function createCompactItem(article, isExtra = false) {
    const row = document.createElement('div');
    row.className = 'compact-item';
    if (isExtra) row.classList.add('extra');
    const personaEval = (article.evaluation && article.evaluation[currentPersona]) || {};
    const scorePct = Math.round((personaEval.total_score || 0) * 100);
    const rec = personaEval.recommendation || 'consider';
    const recIcon = rec === 'consider' ? '<span class="icon info-icon"></span>' : (rec === 'skip' ? '<span class="icon skip-icon"></span>' : '');
    const baseText = article.content || '';
    const origText = article.original_content || '';
    const labeled = deriveLabeledKeyPoints(baseText || origText, 1);
    const mini = labeled.length ? `${labeled[0].label?`<span class=\\\"kp-label\\\">${labeled[0].label}</span> `:''}${highlightKeywords(labeled[0].text)}` : '';
    row.innerHTML = `
      <div class="left">
        <div class="title"><a href="${article.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a></div>
        ${mini ? `<div class=\"mini-highlight\">${mini}</div>` : ''}
        <div class="source">${escapeHtml(article.source)} • ${article.published_date || ''}</div>
      </div>
      <div class="right">
        <div class="mini-bar"><span style="width:${scorePct}%"></span></div>
        <span class="recommendation rec-${rec}" title="${getRecommendationDesc(rec)}" aria-label="${getRecommendationDesc(rec)}">${recIcon}${getRecommendationText(rec)}</span>
      </div>
    `;
    return row;
  }

  function updateSummaryStats() {
    const totalEl = document.getElementById('stat-total');
    const avgEl = document.getElementById('stat-avg-score');
    const tier1El = document.getElementById('stat-tier1');
    totalEl && (totalEl.textContent = filteredArticles.length);
    const avgScore = filteredArticles.reduce((sum, art) => sum + getPersonaScore(art), 0) / (filteredArticles.length || 1);
    avgEl && (avgEl.textContent = Math.round(avgScore * 100) + '%');
    const tier1Count = filteredArticles.filter(a => a.source_tier === 1).length;
    tier1El && (tier1El.textContent = tier1Count);
  }

  // Readability helpers
  function isJapanese(text) {
    if (!text) return false;
    const jp = /[\u3040-\u30FF\u4E00-\u9FAF]/;
    return jp.test(text);
  }
  function splitSentences(text) {
    return (text || '')
      .replace(/\s+/g,' ')
      .split(/(?<=[。．.!?！？])\s+/)
      .map(s => s.trim())
      .filter(Boolean);
  }
  function extractLead(text) {
    if (!text) return '';
    const sents = splitSentences(text);
    if (!sents.length) return text.slice(0, 120);
    let lead = sents[0];
    if (lead.length < 40 && sents[1]) lead += ' ' + sents[1];
    return lead.trim();
  }
  function extractKeyPoints(text, count = 3) {
    if (!text) return [];
    const sents = splitSentences(text).filter(s => s.length > 25);
    if (!sents.length) return [];
    const keywords = ['AI','生成','モデル','LLM','RAG','エージェント','改善','発表','研究','性能','コスト','導入','事例','OpenAI','Google','Meta','Microsoft','Anthropic','Gemini','Claude','GPT','Llama'];
    const scored = sents.map(s => ({ s, score: keywords.reduce((acc,k)=>acc + (s.includes(k)?1:0), 0) + s.length/200 }));
    scored.sort((a,b) => b.score - a.score);
    const picks = scored.slice(0, count).map(x => x.s.trim());
    const uniq = [];
    picks.forEach(p => { if (!uniq.some(u => u.slice(0,12) === p.slice(0,12))) uniq.push(p); });
    return uniq;
  }
  function deriveLabeledKeyPoints(text, count = 3) {
    const categories = [
      { key: '発表', patterns: [/発表|公開|ローンチ|リリース/] },
      { key: '性能', patterns: [/性能|精度|スコア|ベンチマーク|速度|高速|低遅延|throughput|latency/i] },
      { key: '導入', patterns: [/導入|使い方|セットアップ|手順|サンプル|コード|チュートリアル/] },
      { key: '影響', patterns: [/影響|価値|ROI|コスト|効率|生産性|採用|事業|ビジネス/] },
      { key: '研究', patterns: [/研究|論文|arXiv|paper/i] },
      { key: '注意', patterns: [/リスク|注意|制限|制約|課題|バグ|脆弱性/] }
    ];
    const sents = splitSentences(text || '').filter(s => s.length > 20);
    const results = [];
    const used = new Set();
    for (const cat of categories) {
      let bestIdx = -1, bestScore = -1;
      for (let i=0;i<sents.length;i++) {
        if (used.has(i)) continue;
        const s = sents[i];
        if (cat.patterns.some(re => re.test(s))) {
          const score = s.length + cat.patterns.reduce((acc,re)=>acc+(re.test(s)?50:0),0);
          if (score > bestScore) { bestScore = score; bestIdx = i; }
        }
      }
      if (bestIdx >= 0) { used.add(bestIdx); results.push({ label: cat.key, text: sents[bestIdx] }); }
      if (results.length >= count) break;
    }
    if (results.length < count) {
      extractKeyPoints(text, count - results.length).forEach(p => results.push({ label: '', text: p }));
    }
    return results.slice(0, count);
  }
  function highlightKeywords(text) {
    if (!text) return '';
    const pairs = [
      ['RAG','RAG'], ['LLM','LLM'], ['GPT-4','GPT-4'], ['GPT-5','GPT-5'],
      ['Claude','Claude'], ['Gemini','Gemini'], ['Llama','Llama'],
      ['エージェント','エージェント'], ['生成AI','生成AI'], ['ベンチマーク','ベンチマーク'],
      ['性能','性能'], ['コスト','コスト'], ['導入','導入'], ['研究','研究'], ['発表','発表']
    ];
    let out = escapeHtml(text);
    pairs.forEach(([k,label]) => {
      const re = new RegExp(k.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&'),'g');
      out = out.replace(re, `<span class=\"kw\">${label}</span>`);
    });
    return out;
  }

  function applyFilters() {
    const tierFilter = document.getElementById('source-tier-filter').value;
    const minScore = parseFloat(document.getElementById('min-score-filter').value || 0);
    const searchQuery = document.getElementById('search-input').value.toLowerCase();
    filteredArticles = (window.articles || []).filter(article => {
      if (tierFilter !== 'all' && article.source_tier !== parseInt(tierFilter)) return false;
      if (getPersonaScore(article) < minScore) return false;
      if (searchQuery) {
        const haystack = (article.title + article.content + article.source).toLowerCase();
        if (!haystack.includes(searchQuery)) return false;
      }
      return true;
    });
    renderArticles();
    updateSummaryStats();
  }

  function initUI() {
    // Persona toggle
    document.querySelectorAll('.header .persona-toggle button[data-persona]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.header .persona-toggle button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPersona = btn.dataset.persona;
        applyFilters();
      });
    });
    // Filters
    document.getElementById('source-tier-filter')?.addEventListener('change', applyFilters);
    document.getElementById('min-score-filter')?.addEventListener('input', applyFilters);
    document.getElementById('search-input')?.addEventListener('input', applyFilters);

    // Theme
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
      themeBtn.textContent = savedTheme === 'dark' ? '🌞' : '🌙';
      themeBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        themeBtn.textContent = next === 'dark' ? '🌞' : '🌙';
      });
    }

    // Slider bubble
    const rangeEl = document.getElementById('min-score-filter');
    const outEl = document.getElementById('min-score-value');
    const setRangeText = () => { if (outEl && rangeEl) outEl.textContent = Math.round(parseFloat(rangeEl.value || '0') * 100) + '%'; };
    if (rangeEl) { setRangeText(); rangeEl.addEventListener('input', setRangeText); }

    // Filters accordion on mobile
    const filters = document.querySelector('.filters');
    const toggleBtn = document.querySelector('.filters-toggle');
    const applyInitialCollapsed = () => {
      if (!filters || !toggleBtn) return;
      const isMobile = window.matchMedia('(max-width: 768px)').matches;
      if (isMobile) {
        filters.classList.add('collapsed');
        toggleBtn.setAttribute('aria-expanded', 'false');
      } else {
        filters.classList.remove('collapsed');
        toggleBtn.setAttribute('aria-expanded', 'true');
      }
    };
    applyInitialCollapsed();
    window.addEventListener('resize', applyInitialCollapsed);
    toggleBtn?.addEventListener('click', () => {
      const isCollapsed = filters.classList.toggle('collapsed');
      toggleBtn.setAttribute('aria-expanded', String(!isCollapsed));
    });

    // Collapsible recommendation sections (delegate)
    const articlesContainer = document.getElementById('articles-container');
    articlesContainer?.addEventListener('click', (e) => {
      const showMoreBtn = e.target.closest('.show-more');
      if (showMoreBtn) {
        e.stopPropagation();
        const section = showMoreBtn.closest('.rec-section');
        const expanded = section.classList.toggle('expanded');
        showMoreBtn.setAttribute('aria-expanded', String(expanded));
        showMoreBtn.textContent = expanded ? '少なく表示' : 'もっと見る';
        return;
      }
      const heading = e.target.closest('.rec-heading');
      if (!heading) return;
      const section = heading.closest('.rec-section');
      section?.classList.toggle('collapsed');
    });
    // Original excerpt toggle
    articlesContainer?.addEventListener('click', (e) => {
      const btn = e.target.closest('.original-toggle');
      if (!btn) return;
      const excerpt = btn.nextElementSibling;
      if (excerpt && excerpt.classList.contains('original-excerpt')) {
        const on = excerpt.classList.toggle('show');
        btn.textContent = on ? '英語原文を隠す' : '英語原文を表示';
      }
    });
    articlesContainer?.addEventListener('keydown', (e) => {
      if ((e.key === 'Enter' || e.key === ' ') && e.target.classList?.contains('rec-heading')) {
        e.preventDefault();
        e.target.closest('.rec-section')?.classList.toggle('collapsed');
      }
    });

    // Rec nav interactions
    document.querySelectorAll('.rec-nav .nav-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        const el = document.getElementById(`sec-${target}`);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });

    // Observe sections to update nav active state
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const rec = entry.target.dataset.rec;
          document.querySelectorAll('.rec-nav .nav-item').forEach(i => i.classList.toggle('active', i.getAttribute('data-target') === rec));
        }
      });
    }, { rootMargin: '-40% 0px -50% 0px', threshold: 0 });
    document.querySelectorAll('.rec-section').forEach(sec => obs.observe(sec));
  }

  function updateRecNavCounts(groups) {
    const ids = ['must_read','recommended','consider','skip'];
    ids.forEach(id => {
      const el = document.getElementById(`nav-count-${id}`);
      if (el) el.textContent = (groups[id] || []).length;
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    filteredArticles = [...(window.articles || [])];
    initUI();
    renderArticles();
    updateSummaryStats();
  });
})();
