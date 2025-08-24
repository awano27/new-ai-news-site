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
    const texts = { must_read: '必読', recommended: '注目', consider: '参考', skip: '見送り' };
    return texts[rec] || rec;
  }
  function getRecommendationDesc(rec) {
    const desc = {
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

    const groups = { must_read: [], recommended: [], consider: [], skip: [] };
    filteredArticles.forEach(article => {
      const rec = (article.evaluation && article.evaluation[currentPersona] && article.evaluation[currentPersona].recommendation) || 'consider';
      (groups[rec] || groups.consider).push(article);
    });

    const order = ['must_read','recommended','consider','skip'];
    order.forEach(rec => {
      const items = groups[rec];
      if (!items || items.length === 0) return;

      const section = document.createElement('section');
      section.className = `rec-section rec-${rec}` + (rec === 'consider' || rec === 'skip' ? ' collapsed' : '');
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
          if (idx >= limitTop) el.classList.add('extra');
          content.appendChild(el);
        });
      } else {
        const sorted = items.sort((a,b) => getPersonaScore(b) - getPersonaScore(a));
        const limit = 5;
        sorted.forEach((article, idx) => content.appendChild(createCompactItem(article, idx >= limit)));
      }

      section.appendChild(content);
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
    row.innerHTML = `
      <div class="left">
        <div class="title"><a href="${article.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a></div>
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
