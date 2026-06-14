/**
 * 共轭智能全球投资策略平台 - 核心应用逻辑
 * SPA路由管理、API调用、用户认证、UI交互
 */

const App = {
    // 配置
    API_BASE: 'http://localhost:8000',
    currentRoute: 'home',

    // 状态
    state: {
        isAuthenticated: false,
        token: null,
        user: null,
        strategies: [],
        selectedStrategy: null,
        chatOpen: false,
        chatMessages: []
    },

    /**
     * 应用初始化
     */
    init() {
        // 初始化图表模块
        Charts.init();

        // 恢复认证状态
        this.restoreAuth();

        // 初始化路由
        this.initRouter();

        // 绑定事件
        this.bindEvents();

        // 初始化AI聊天
        this.initChat();

        // 加载首页
        this.navigate('home');
    },

    // ==================== 路由管理 ====================

    /**
     * 初始化路由系统
     */
    initRouter() {
        // 监听浏览器前进/后退
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.route) {
                this.renderPage(e.state.route);
            }
        });
    },

    /**
     * 导航到指定页面
     */
    navigate(route) {
        this.currentRoute = route;
        window.history.pushState({ route }, '', `#${route}`);
        this.renderPage(route);
        this.updateNavActive(route);
    },

    /**
     * 渲染页面
     */
    renderPage(route) {
        // 隐藏所有页面
        document.querySelectorAll('.page-view').forEach(p => {
            p.classList.remove('active');
        });

        // 显示目标页面
        const page = document.getElementById(`page-${route}`);
        if (page) {
            page.classList.add('active');
        }

        // 页面特定初始化
        switch (route) {
            case 'home':
                this.renderHomePage();
                break;
            case 'strategies':
                this.renderStrategiesPage();
                break;
            case 'analysis':
                this.renderAnalysisPage();
                break;
            case 'about':
                break;
        }

        // 滚动到顶部
        window.scrollTo(0, 0);
    },

    /**
     * 更新导航栏激活状态
     */
    updateNavActive(route) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.route === route) {
                link.classList.add('active');
            }
        });
    },

    // ==================== 首页 ====================

    renderHomePage() {
        const stats = StrategiesData.getStats();
        const statsContainer = document.getElementById('home-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.totalStrategies}</div>
                    <div class="stat-label">策略总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.activeStrategies}</div>
                    <div class="stat-label">运行中策略</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.avgReturn}</div>
                    <div class="stat-label">平均年化收益</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.avgSharpe}</div>
                    <div class="stat-label">平均夏普比率</div>
                </div>
            `;
        }

        // 渲染热门策略
        const hotStrategies = StrategiesData.strategies.slice(0, 4);
        const hotContainer = document.getElementById('home-hot-strategies');
        if (hotContainer) {
            hotContainer.innerHTML = hotStrategies.map(s => this.renderStrategyCard(s)).join('');
            this.bindStrategyCardEvents(hotContainer);
        }
    },

    // ==================== 策略中心 ====================

    renderStrategiesPage() {
        this.renderStrategyList('all');
        this.bindStrategyFilters();
    },

    /**
     * 渲染策略列表
     */
    renderStrategyList(category, keyword) {
        let strategies;
        if (keyword) {
            strategies = StrategiesData.search(keyword);
        } else if (category && category !== 'all') {
            strategies = StrategiesData.getByCategory(category);
        } else {
            strategies = StrategiesData.strategies;
        }

        const container = document.getElementById('strategy-list');
        if (!container) return;

        if (strategies.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <p>未找到匹配的策略</p>
                </div>
            `;
            return;
        }

        container.innerHTML = strategies.map(s => this.renderStrategyCard(s)).join('');
        this.bindStrategyCardEvents(container);
    },

    /**
     * 渲染单个策略卡片
     */
    renderStrategyCard(strategy) {
        const catInfo = StrategiesData.getCategoryInfo(strategy.category);
        const riskColors = {
            '低': '#00d084',
            '中低': '#4fc3f7',
            '中': '#f5c518',
            '中高': '#ff9800',
            '高': '#e94560'
        };
        const riskColor = riskColors[strategy.riskLevel] || '#f5c518';

        return `
            <div class="strategy-card" data-id="${strategy.id}">
                <div class="strategy-card-header">
                    <span class="strategy-category-badge" style="background: ${catInfo ? catInfo.color : '#4fc3f7'}20; color: ${catInfo ? catInfo.color : '#4fc3f7'}">
                        ${catInfo ? catInfo.icon : ''} ${catInfo ? catInfo.name : ''}
                    </span>
                    <span class="strategy-risk-badge" style="background: ${riskColor}20; color: ${riskColor}">
                        ${strategy.riskLevel}风险
                    </span>
                </div>
                <h3 class="strategy-name">${strategy.name}</h3>
                <p class="strategy-desc">${strategy.description}</p>
                <div class="strategy-tags">
                    ${strategy.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
                <div class="strategy-metrics">
                    <div class="strategy-metric">
                        <span class="metric-label">年化收益</span>
                        <span class="metric-value positive">${strategy.annualReturn}</span>
                    </div>
                    <div class="strategy-metric">
                        <span class="metric-label">最大回撤</span>
                        <span class="metric-value negative">${strategy.maxDrawdown}</span>
                    </div>
                    <div class="strategy-metric">
                        <span class="metric-label">夏普比率</span>
                        <span class="metric-value">${strategy.sharpeRatio}</span>
                    </div>
                    <div class="strategy-metric">
                        <span class="metric-label">胜率</span>
                        <span class="metric-value">${strategy.winRate}</span>
                    </div>
                </div>
                <div class="strategy-card-footer">
                    <span class="min-investment">起投 ${strategy.minInvestment}</span>
                    <button class="btn btn-primary btn-sm strategy-detail-btn" data-id="${strategy.id}">查看详情</button>
                </div>
            </div>
        `;
    },

    /**
     * 绑定策略卡片事件
     */
    bindStrategyCardEvents(container) {
        container.querySelectorAll('.strategy-detail-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                this.showStrategyDetail(id);
            });
        });

        container.querySelectorAll('.strategy-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showStrategyDetail(card.dataset.id);
            });
        });
    },

    /**
     * 绑定策略筛选事件
     */
    bindStrategyFilters() {
        // 分类筛选
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.category-filter').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const keyword = document.getElementById('strategy-search')?.value || '';
                this.renderStrategyList(btn.dataset.category, keyword);
            });
        });

        // 搜索
        const searchInput = document.getElementById('strategy-search');
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const activeCategory = document.querySelector('.category-filter.active');
                    const category = activeCategory ? activeCategory.dataset.category : 'all';
                    this.renderStrategyList(category, searchInput.value);
                }, 300);
            });
        }
    },

    /**
     * 显示策略详情弹窗
     */
    showStrategyDetail(strategyId) {
        const strategy = StrategiesData.getById(strategyId);
        if (!strategy) return;

        const catInfo = StrategiesData.getCategoryInfo(strategy.category);
        const modal = document.getElementById('strategy-detail-modal');
        const content = document.getElementById('strategy-detail-content');

        content.innerHTML = `
            <div class="detail-header">
                <span class="strategy-category-badge" style="background: ${catInfo.color}20; color: ${catInfo.color}">
                    ${catInfo.icon} ${catInfo.name}
                </span>
                <h2>${strategy.name}</h2>
                <p class="detail-desc">${strategy.description}</p>
            </div>
            <div class="detail-metrics-grid">
                <div class="detail-metric-card">
                    <div class="detail-metric-label">年化收益率</div>
                    <div class="detail-metric-value positive">${strategy.annualReturn}</div>
                </div>
                <div class="detail-metric-card">
                    <div class="detail-metric-label">最大回撤</div>
                    <div class="detail-metric-value negative">${strategy.maxDrawdown}</div>
                </div>
                <div class="detail-metric-card">
                    <div class="detail-metric-label">夏普比率</div>
                    <div class="detail-metric-value">${strategy.sharpeRatio}</div>
                </div>
                <div class="detail-metric-card">
                    <div class="detail-metric-label">胜率</div>
                    <div class="detail-metric-value">${strategy.winRate}</div>
                </div>
                <div class="detail-metric-card">
                    <div class="detail-metric-label">风险等级</div>
                    <div class="detail-metric-value">${strategy.riskLevel}</div>
                </div>
                <div class="detail-metric-card">
                    <div class="detail-metric-label">起投金额</div>
                    <div class="detail-metric-value">${strategy.minInvestment}</div>
                </div>
            </div>
            <div class="detail-tags">
                ${strategy.tags.map(t => `<span class="tag">${t}</span>`).join('')}
            </div>
            <div class="detail-actions">
                <button class="btn btn-primary" onclick="App.goToAnalysis('${strategy.id}')">立即分析</button>
                <button class="btn btn-secondary" onclick="App.closeModal('strategy-detail-modal')">关闭</button>
            </div>
        `;

        modal.classList.add('active');
    },

    // ==================== 数据分析 ====================

    renderAnalysisPage() {
        this.populateStrategySelect();
        this.initFileUpload();
    },

    /**
     * 填充策略选择下拉框
     */
    populateStrategySelect() {
        const select = document.getElementById('analysis-strategy-select');
        if (!select) return;

        select.innerHTML = '<option value="">请选择策略...</option>' +
            StrategiesData.strategies.map(s =>
                `<option value="${s.id}">${s.name}</option>`
            ).join('');
    },

    /**
     * 初始化文件上传
     */
    initFileUpload() {
        const dropZone = document.getElementById('upload-dropzone');
        const fileInput = document.getElementById('file-input');

        if (!dropZone || !fileInput) return;

        // 点击上传
        dropZone.addEventListener('click', () => fileInput.click());

        // 拖拽事件
        ['dragenter', 'dragover'].forEach(evt => {
            dropZone.addEventListener(evt, (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(evt => {
            dropZone.addEventListener(evt, (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                this.handleFileUpload(fileInput.files[0]);
            }
        });
    },

    /**
     * 处理文件上传
     */
    handleFileUpload(file) {
        // 验证文件类型
        const validTypes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv'
        ];
        const validExts = ['.xlsx', '.xls', '.csv'];

        const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
            this.showToast('请上传 Excel (.xlsx/.xls) 或 CSV 文件', 'error');
            return;
        }

        // 更新上传区域显示
        const dropZone = document.getElementById('upload-dropzone');
        const fileName = document.getElementById('upload-file-name');
        if (dropZone) dropZone.classList.add('file-selected');
        if (fileName) fileName.textContent = file.name;

        this.state.uploadedFile = file;
        this.showToast('文件上传成功，请选择策略后开始分析', 'success');
    },

    /**
     * 开始分析
     */
    async startAnalysis() {
        const strategyId = document.getElementById('analysis-strategy-select')?.value;
        if (!strategyId) {
            this.showToast('请先选择一个策略', 'warning');
            return;
        }

        if (!this.state.uploadedFile) {
            this.showToast('请先上传数据文件', 'warning');
            return;
        }

        // 显示加载状态
        const resultsSection = document.getElementById('analysis-results');
        const loadingOverlay = document.getElementById('analysis-loading');
        if (resultsSection) resultsSection.classList.remove('hidden');
        if (loadingOverlay) loadingOverlay.classList.add('active');

        try {
            // 尝试调用后端API
            const formData = new FormData();
            formData.append('file', this.state.uploadedFile);
            formData.append('strategy_id', strategyId);

            const result = await this.apiCall('/api/analyze', {
                method: 'POST',
                body: formData,
                isFormData: true
            });

            if (result) {
                Charts.renderAnalysisDashboard(result);
            } else {
                // 使用模拟数据
                const mockResult = StrategiesData.getMockAnalysisResult(strategyId);
                Charts.renderAnalysisDashboard(mockResult);
            }
        } catch (error) {
            console.log('使用模拟数据:', error.message);
            // 后端不可用时使用模拟数据
            const mockResult = StrategiesData.getMockAnalysisResult(strategyId);
            Charts.renderAnalysisDashboard(mockResult);
        } finally {
            if (loadingOverlay) loadingOverlay.classList.remove('active');
        }
    },

    /**
     * 从策略中心跳转到分析页
     */
    goToAnalysis(strategyId) {
        this.closeModal('strategy-detail-modal');
        this.navigate('analysis');
        // 等待页面渲染后设置策略选择
        setTimeout(() => {
            const select = document.getElementById('analysis-strategy-select');
            if (select) select.value = strategyId;
        }, 100);
    },

    // ==================== API 调用 ====================

    /**
     * API 调用封装
     */
    async apiCall(endpoint, options = {}) {
        const url = `${this.API_BASE}${endpoint}`;
        const config = {
            headers: {},
            ...options
        };

        // 添加 JWT Token
        if (this.state.token && !config.isFormData) {
            config.headers['Authorization'] = `Bearer ${this.state.token}`;
            config.headers['Content-Type'] = 'application/json';
        }

        // FormData 不设置 Content-Type（浏览器自动设置 boundary）
        if (config.isFormData) {
            delete config.headers['Content-Type'];
            delete config.isFormData;
        }

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.warn(`API call failed: ${endpoint}`, error.message);
            return null;
        }
    },

    // ==================== 用户认证 ====================

    /**
     * 恢复认证状态
     */
    restoreAuth() {
        const token = localStorage.getItem('cj_token');
        const user = localStorage.getItem('cj_user');

        if (token && user) {
            this.state.token = token;
            this.state.user = JSON.parse(user);
            this.state.isAuthenticated = true;
            this.updateAuthUI();
        }
    },

    /**
     * 用户登录
     */
    async login(username, password) {
        try {
            const result = await this.apiCall('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            if (result && result.access_token) {
                this.state.token = result.access_token;
                this.state.user = result.user || { username };
                this.state.isAuthenticated = true;

                localStorage.setItem('cj_token', result.access_token);
                localStorage.setItem('cj_user', JSON.stringify(this.state.user));

                this.updateAuthUI();
                this.closeModal('auth-modal');
                this.showToast(`欢迎回来，${this.state.user.username}`, 'success');
                return true;
            } else {
                // 模拟登录（后端不可用时）
                if (username && password.length >= 4) {
                    this.state.token = 'mock_token_' + Date.now();
                    this.state.user = { username };
                    this.state.isAuthenticated = true;

                    localStorage.setItem('cj_token', this.state.token);
                    localStorage.setItem('cj_user', JSON.stringify(this.state.user));

                    this.updateAuthUI();
                    this.closeModal('auth-modal');
                    this.showToast(`欢迎回来，${username}`, 'success');
                    return true;
                }
                this.showToast('用户名或密码错误', 'error');
                return false;
            }
        } catch (error) {
            this.showToast('登录失败，请稍后重试', 'error');
            return false;
        }
    },

    /**
     * 用户注册
     */
    async register(username, email, password) {
        try {
            const result = await this.apiCall('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });

            if (result) {
                this.showToast('注册成功，请登录', 'success');
                this.switchAuthTab('login');
                return true;
            } else {
                // 模拟注册
                if (username && email && password.length >= 4) {
                    this.showToast('注册成功，请登录', 'success');
                    this.switchAuthTab('login');
                    return true;
                }
                this.showToast('注册信息不完整', 'error');
                return false;
            }
        } catch (error) {
            this.showToast('注册失败，请稍后重试', 'error');
            return false;
        }
    },

    /**
     * 用户登出
     */
    logout() {
        this.state.token = null;
        this.state.user = null;
        this.state.isAuthenticated = false;

        localStorage.removeItem('cj_token');
        localStorage.removeItem('cj_user');

        this.updateAuthUI();
        this.showToast('已安全退出', 'success');
    },

    /**
     * 更新认证相关UI
     */
    updateAuthUI() {
        const authBtn = document.getElementById('auth-btn');
        const userInfo = document.getElementById('user-info');

        if (this.state.isAuthenticated) {
            if (authBtn) authBtn.style.display = 'none';
            if (userInfo) {
                userInfo.style.display = 'flex';
                const nameEl = userInfo.querySelector('.user-name');
                if (nameEl) nameEl.textContent = this.state.user.username;
            }
        } else {
            if (authBtn) authBtn.style.display = 'inline-flex';
            if (userInfo) userInfo.style.display = 'none';
        }
    },

    /**
     * 切换登录/注册标签
     */
    switchAuthTab(tab) {
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

        document.querySelector(`.auth-tab[data-tab="${tab}"]`)?.classList.add('active');
        document.getElementById(`form-${tab}`)?.classList.add('active');
    },

    // ==================== AI 聊天 ====================

    /**
     * 初始化AI聊天
     */
    initChat() {
        // 添加欢迎消息
        this.state.chatMessages.push({
            role: 'assistant',
            content: '您好！我是共轭智能AI助手，可以为您解答投资策略、市场分析等相关问题。请问有什么可以帮您的？'
        });
    },

    /**
     * 切换聊天窗口
     */
    toggleChat() {
        const chatBox = document.getElementById('chat-box');
        const chatToggle = document.getElementById('chat-toggle');
        this.state.chatOpen = !this.state.chatOpen;

        if (this.state.chatOpen) {
            chatBox?.classList.add('open');
            chatToggle?.classList.add('active');
            this.renderChatMessages();
            // 聚焦输入框
            setTimeout(() => {
                document.getElementById('chat-input')?.focus();
            }, 300);
        } else {
            chatBox?.classList.remove('open');
            chatToggle?.classList.remove('active');
        }
    },

    /**
     * 渲染聊天消息
     */
    renderChatMessages() {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        container.innerHTML = this.state.chatMessages.map(msg => `
            <div class="chat-message ${msg.role}">
                <div class="chat-avatar">${msg.role === 'assistant' ? '🤖' : '👤'}</div>
                <div class="chat-bubble">${this.formatMessage(msg.content)}</div>
            </div>
        `).join('');

        // 滚动到底部
        container.scrollTop = container.scrollHeight;
    },

    /**
     * 格式化消息内容（简单处理换行）
     */
    formatMessage(text) {
        return text.replace(/\n/g, '<br>');
    },

    /**
     * 发送聊天消息
     */
    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        if (!input) return;

        const message = input.value.trim();
        if (!message) return;

        // 添加用户消息
        this.state.chatMessages.push({ role: 'user', content: message });
        this.renderChatMessages();
        input.value = '';

        // 显示加载
        const container = document.getElementById('chat-messages');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat-message assistant chat-loading';
        loadingDiv.innerHTML = `
            <div class="chat-avatar">🤖</div>
            <div class="chat-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>
        `;
        container.appendChild(loadingDiv);
        container.scrollTop = container.scrollHeight;

        try {
            // 调用后端API
            const result = await this.apiCall('/api/chat', {
                method: 'POST',
                body: JSON.stringify({ message, history: this.state.chatMessages.slice(-10) })
            });

            // 移除加载动画
            loadingDiv.remove();

            if (result && result.reply) {
                this.state.chatMessages.push({ role: 'assistant', content: result.reply });
            } else {
                // 模拟AI回复
                const mockReplies = [
                    `关于您提到的"${message}"，这是一个很好的问题。我们的平台提供多种量化策略工具，可以帮助您进行数据驱动的投资决策。建议您前往策略中心了解更多详情。`,
                    `感谢您的提问。基于共轭智能的分析框架，我们建议您关注以下几个方面：市场趋势、风险管理、以及资产配置优化。如需更详细的分析，请上传您的数据文件到数据分析页面。`,
                    `这是一个值得深入探讨的话题。我们的AI量化模型会综合考虑多个因子来生成投资信号。您可以在策略中心查看各策略的历史表现和风险指标。`
                ];
                const reply = mockReplies[Math.floor(Math.random() * mockReplies.length)];
                this.state.chatMessages.push({ role: 'assistant', content: reply });
            }
        } catch (error) {
            loadingDiv.remove();
            this.state.chatMessages.push({
                role: 'assistant',
                content: '抱歉，我暂时无法处理您的请求。请稍后再试。'
            });
        }

        this.renderChatMessages();
    },

    // ==================== 模态框管理 ====================

    /**
     * 打开模态框
     */
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    },

    /**
     * 关闭模态框
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    },

    // ==================== Toast 通知 ====================

    /**
     * 显示 Toast 通知
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
        `;

        container.appendChild(toast);

        // 触发动画
        requestAnimationFrame(() => toast.classList.add('show'));

        // 自动移除
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // ==================== 事件绑定 ====================

    bindEvents() {
        // 导航链接
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = link.dataset.route;
                if (route) this.navigate(route);
            });
        });

        // 登录/注册按钮
        const authBtn = document.getElementById('auth-btn');
        if (authBtn) {
            authBtn.addEventListener('click', () => this.openModal('auth-modal'));
        }

        // 登出按钮
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // 认证标签切换
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchAuthTab(tab.dataset.tab);
            });
        });

        // 登录表单提交
        const loginForm = document.getElementById('form-login');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const username = document.getElementById('login-username')?.value;
                const password = document.getElementById('login-password')?.value;
                if (username && password) this.login(username, password);
            });
        }

        // 注册表单提交
        const registerForm = document.getElementById('form-register');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const username = document.getElementById('reg-username')?.value;
                const email = document.getElementById('reg-email')?.value;
                const password = document.getElementById('reg-password')?.value;
                if (username && email && password) this.register(username, email, password);
            });
        }

        // 模态框关闭
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.classList.remove('active');
                }
            });
        });

        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.modal-overlay').classList.remove('active');
            });
        });

        // AI聊天切换
        const chatToggle = document.getElementById('chat-toggle');
        if (chatToggle) {
            chatToggle.addEventListener('click', () => this.toggleChat());
        }

        // 聊天发送
        const chatSend = document.getElementById('chat-send');
        if (chatSend) {
            chatSend.addEventListener('click', () => this.sendChatMessage());
        }

        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendChatMessage();
            });
        }

        // 分析按钮
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.startAnalysis());
        }

        // ESC 关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
            }
        });
    }
};

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
