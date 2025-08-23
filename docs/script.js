
        class DashboardController {
            constructor() {
                this.currentPersona = 'engineer';
                this.articles = [];
                this.filteredArticles = [];
                this.init();
            }
            
            init() {
                this.setupPersonaToggle();
                this.setupFilters();
                this.setupSearch();
                this.loadArticles();
            }
            
            setupPersonaToggle() {
                const toggles = document.querySelectorAll('.persona-toggle button');
                toggles.forEach(toggle => {
                    toggle.addEventListener('click', (e) => {
                        const persona = e.target.dataset.persona;
                        this.switchPersona(persona);
                    });
                });
            }
            
            setupFilters() {
                const filterSelects = document.querySelectorAll('.filter-group select');
                filterSelects.forEach(select => {
                    select.addEventListener('change', () => this.applyFilters());
                });
                
                const scoreInputs = document.querySelectorAll('.filter-group input[type="range"]');
                scoreInputs.forEach(input => {
                    input.addEventListener('input', () => this.applyFilters());
                });
            }
            
            setupSearch() {
                const searchInput = document.querySelector('#search-input');
                if (searchInput) {
                    searchInput.addEventListener('input', (e) => {
                        this.searchArticles(e.target.value);
                    });
                }
            }
            
            switchPersona(persona) {
                this.currentPersona = persona;
                
                // Update active button
                document.querySelectorAll('.persona-toggle button').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.persona === persona);
                });
                
                // Update body class
                document.body.className = `persona-${persona}`;
                
                // Re-render articles with new persona
                this.renderArticles();
            }
            
            loadArticles() {
                // Get articles data from embedded JSON or API
                const articleData = document.querySelector('#articles-data');
                if (articleData) {
                    this.articles = JSON.parse(articleData.textContent);
                    this.filteredArticles = [...this.articles];
                    this.renderArticles();
                    this.updateSummaryStats();
                }
            }
            
            applyFilters() {
                const sourceTier = document.querySelector('#source-tier-filter')?.value;
                const minScore = parseFloat(document.querySelector('#min-score-filter')?.value || 0);
                const difficultyLevel = document.querySelector('#difficulty-filter')?.value;
                
                this.filteredArticles = this.articles.filter(article => {
                    // Source tier filter
                    if (sourceTier && sourceTier !== 'all' && article.source_tier !== parseInt(sourceTier)) {
                        return false;
                    }
                    
                    // Minimum score filter
                    const score = this.getPersonaScore(article);
                    if (score < minScore) {
                        return false;
                    }
                    
                    // Difficulty filter
                    if (difficultyLevel && difficultyLevel !== 'all' && article.difficulty_level !== difficultyLevel) {
                        return false;
                    }
                    
                    return true;
                });
                
                this.renderArticles();
                this.updateSummaryStats();
            }
            
            searchArticles(query) {
                if (!query.trim()) {
                    this.applyFilters();
                    return;
                }
                
                const lowQuery = query.toLowerCase();
                this.filteredArticles = this.filteredArticles.filter(article => {
                    return article.title.toLowerCase().includes(lowQuery) ||
                           article.content.toLowerCase().includes(lowQuery) ||
                           article.source.toLowerCase().includes(lowQuery) ||
                           (article.tags && article.tags.some(tag => tag.toLowerCase().includes(lowQuery)));
                });
                
                this.renderArticles();
                this.updateSummaryStats();
            }
            
            getPersonaScore(article) {
                if (!article.evaluation) return 0;
                const evaluation = article.evaluation[this.currentPersona];
                return evaluation ? evaluation.total_score : 0;
            }
            
            renderArticles() {
                const container = document.querySelector('.articles-grid');
                if (!container) return;
                
                container.innerHTML = '';
                
                this.filteredArticles
                    .sort((a, b) => this.getPersonaScore(b) - this.getPersonaScore(a))
                    .forEach(article => {
                        container.appendChild(this.createArticleCard(article));
                    });
            }
            
            createArticleCard(article) {
                const card = document.createElement('div');
                card.className = 'article-card';
                
                const score = this.getPersonaScore(article);
                const scorePercentage = Math.round(score * 100);
                
                card.innerHTML = `
                    <div class="source-tier tier-${article.source_tier}">
                        Tier ${article.source_tier}
                    </div>
                    <h3>
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                            ${article.title}
                        </a>
                    </h3>
                    <div class="article-meta">
                        <span>${article.source}</span>
                        <span>•</span>
                        <span>${this.formatDate(article.published_date)}</span>
                    </div>
                    <div class="article-content">
                        ${this.truncateText(article.content, 200)}
                    </div>
                    <div class="evaluation-scores">
                        <div class="score-item ${this.currentPersona}">
                            <span>${this.currentPersona === 'engineer' ? 'Tech' : 'Business'}</span>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${scorePercentage}%"></div>
                            </div>
                            <span>${scorePercentage}%</span>
                        </div>
                    </div>
                    ${article.tags ? `
                        <div class="tags">
                            ${article.tags.slice(0, 5).map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    ` : ''}
                `;
                
                return card;
            }
            
            formatDate(dateString) {
                if (!dateString) return 'Recent';
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric',
                    year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
                });
            }
            
            truncateText(text, maxLength) {
                if (!text || text.length <= maxLength) return text || '';
                return text.substring(0, maxLength).trim() + '...';
            }
            
            updateSummaryStats() {
                const totalElement = document.querySelector('#stat-total');
                const avgScoreElement = document.querySelector('#stat-avg-score');
                const tier1Element = document.querySelector('#stat-tier1');
                
                if (totalElement) {
                    totalElement.textContent = this.filteredArticles.length;
                }
                
                if (avgScoreElement) {
                    const avgScore = this.filteredArticles.reduce((sum, article) => {
                        return sum + this.getPersonaScore(article);
                    }, 0) / this.filteredArticles.length;
                    avgScoreElement.textContent = Math.round((avgScore || 0) * 100) + '%';
                }
                
                if (tier1Element) {
                    const tier1Count = this.filteredArticles.filter(a => a.source_tier === 1).length;
                    tier1Element.textContent = tier1Count;
                }
            }
        }
        
        // Initialize dashboard when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            new DashboardController();
        });
        
        // Theme switching functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }
        
        // Load saved theme
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });
        