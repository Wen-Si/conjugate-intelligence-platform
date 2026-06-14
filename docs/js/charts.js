/**
 * 共轭智能全球投资策略平台 - 图表绘制模块
 * 基于 Chart.js 实现各类金融图表
 */

const Charts = {
    // 存储所有图表实例，便于销毁和更新
    instances: {},

    // 全局 Chart.js 默认配置
    defaults: {
        colors: {
            primary: '#4fc3f7',
            secondary: '#e94560',
            success: '#00d084',
            warning: '#f5c518',
            purple: '#ab47bc',
            grid: 'rgba(255, 255, 255, 0.06)',
            text: 'rgba(255, 255, 255, 0.7)'
        },
        font: {
            family: "'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif"
        }
    },

    /**
     * 初始化 Chart.js 全局默认设置
     */
    init() {
        Chart.defaults.color = this.defaults.colors.text;
        Chart.defaults.font.family = this.defaults.font.family;
        Chart.defaults.plugins.legend.labels.padding = 16;
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26, 26, 46, 0.95)';
        Chart.defaults.plugins.tooltip.borderColor = 'rgba(79, 195, 247, 0.3)';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.titleFont = { size: 13, weight: 'bold' };
        Chart.defaults.plugins.tooltip.bodyFont = { size: 12 };
        Chart.defaults.scale.grid = { color: this.defaults.colors.grid };
        Chart.defaults.scale.border = { color: 'rgba(255, 255, 255, 0.1)' };
    },

    /**
     * 销毁指定图表
     */
    destroy(chartId) {
        if (this.instances[chartId]) {
            this.instances[chartId].destroy();
            delete this.instances[chartId];
        }
    },

    /**
     * 销毁所有图表
     */
    destroyAll() {
        Object.keys(this.instances).forEach(id => this.destroy(id));
    },

    /**
     * 获取 Canvas 上下文
     */
    getContext(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element #${canvasId} not found`);
            return null;
        }
        return canvas.getContext('2d');
    },

    /**
     * 收益曲线图（折线图）
     * @param {string} canvasId - Canvas 元素 ID
     * @param {Array} data - { labels, strategy, benchmark }
     */
    renderReturnCurve(canvasId, data) {
        this.destroy(canvasId);
        const ctx = this.getContext(canvasId);
        if (!ctx) return;

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: '策略收益',
                        data: data.strategy,
                        borderColor: this.defaults.colors.primary,
                        backgroundColor: 'rgba(79, 195, 247, 0.1)',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        pointBackgroundColor: this.defaults.colors.primary,
                        pointBorderColor: '#1a1a2e',
                        pointBorderWidth: 2
                    },
                    {
                        label: '基准收益',
                        data: data.benchmark,
                        borderColor: 'rgba(255, 255, 255, 0.35)',
                        backgroundColor: 'rgba(255, 255, 255, 0.03)',
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 2,
                        pointHoverRadius: 5,
                        pointBackgroundColor: 'rgba(255, 255, 255, 0.5)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: '累计收益曲线',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 16 }
                    },
                    legend: {
                        position: 'top',
                        align: 'end'
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: val => val.toFixed(1) + '%'
                        },
                        title: {
                            display: true,
                            text: '累计收益率 (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '时间'
                        }
                    }
                }
            }
        });
    },

    /**
     * 回撤分析图（面积图）
     * @param {string} canvasId
     * @param {Array} data - { labels, drawdowns }
     */
    renderDrawdown(canvasId, data) {
        this.destroy(canvasId);
        const ctx = this.getContext(canvasId);
        if (!ctx) return;

        // 创建渐变
        const canvas = document.getElementById(canvasId);
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.clientHeight || 300);
        gradient.addColorStop(0, 'rgba(233, 69, 96, 0.4)');
        gradient.addColorStop(0.5, 'rgba(233, 69, 96, 0.15)');
        gradient.addColorStop(1, 'rgba(233, 69, 96, 0.02)');

        this.instances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '回撤',
                    data: data.drawdowns,
                    borderColor: this.defaults.colors.secondary,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    pointBackgroundColor: this.defaults.colors.secondary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: '最大回撤分析',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 16 }
                    },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: val => val.toFixed(1) + '%'
                        },
                        title: {
                            display: true,
                            text: '回撤幅度 (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '时间'
                        }
                    }
                }
            }
        });
    },

    /**
     * 月度收益热力图（使用柱状图模拟）
     * @param {string} canvasId
     * @param {Array} data - { labels, returns }
     */
    renderMonthlyHeatmap(canvasId, data) {
        this.destroy(canvasId);
        const ctx = this.getContext(canvasId);
        if (!ctx) return;

        // 根据收益正负着色
        const bgColors = data.returns.map(v =>
            v >= 0 ? 'rgba(0, 208, 132, 0.7)' : 'rgba(233, 69, 96, 0.7)'
        );
        const borderColors = data.returns.map(v =>
            v >= 0 ? '#00d084' : '#e94560'
        );

        this.instances[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '月度收益率',
                    data: data.returns,
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: 1.5,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: '月度收益分布',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 16 }
                    },
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `收益率: ${ctx.parsed.y.toFixed(2)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: val => val.toFixed(1) + '%'
                        },
                        title: {
                            display: true,
                            text: '收益率 (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '月份'
                        }
                    }
                }
            }
        });
    },

    /**
     * 资产配置饼图
     * @param {string} canvasId
     * @param {Array} data - [{ name, value, color }]
     */
    renderAssetAllocation(canvasId, data) {
        this.destroy(canvasId);
        const ctx = this.getContext(canvasId);
        if (!ctx) return;

        this.instances[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => d.value),
                    backgroundColor: data.map(d => d.color),
                    borderColor: '#1a1a2e',
                    borderWidth: 3,
                    hoverBorderColor: '#fff',
                    hoverBorderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    title: {
                        display: true,
                        text: '资产配置比例',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 16 }
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 16,
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, i) => ({
                                    text: `${label}  ${data.datasets[0].data[i]}%`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    strokeStyle: 'transparent',
                                    pointStyle: 'rectRounded',
                                    index: i
                                }));
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.label}: ${ctx.parsed}%`
                        }
                    }
                }
            }
        });
    },

    /**
     * 关键指标仪表盘（使用雷达图）
     * @param {string} canvasId
     * @param {Object} metrics - { annualReturn, sharpeRatio, winRate, calmarRatio, sortinoRatio }
     */
    renderMetricsDashboard(canvasId, metrics) {
        this.destroy(canvasId);
        const ctx = this.getContext(canvasId);
        if (!ctx) return;

        // 归一化指标到 0-100 范围
        const normalize = (val, max) => Math.min(100, (parseFloat(val) / max) * 100);

        const labels = ['年化收益', '夏普比率', '胜率', '卡玛比率', '索提诺比率'];
        const values = [
            normalize(metrics.annualReturn, 30),
            normalize(metrics.sharpeRatio, 3),
            normalize(metrics.winRate, 100),
            normalize(metrics.calmarRatio, 3),
            normalize(metrics.sortinoRatio, 4)
        ];

        this.instances[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: '策略评分',
                    data: values,
                    backgroundColor: 'rgba(79, 195, 247, 0.15)',
                    borderColor: this.defaults.colors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: this.defaults.colors.primary,
                    pointBorderColor: '#1a1a2e',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '策略综合评分',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 16 }
                    },
                    legend: { display: false }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            backdropColor: 'transparent',
                            color: 'rgba(255, 255, 255, 0.4)',
                            font: { size: 10 }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.08)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.08)'
                        },
                        pointLabels: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    },

    /**
     * 渲染完整的分析结果面板
     * @param {Object} analysisResult - 来自 StrategiesData.getMockAnalysisResult()
     */
    renderAnalysisDashboard(analysisResult) {
        if (!analysisResult) return;

        const { monthlyReturns, cumulativeReturns, drawdowns, assetAllocation, keyMetrics } = analysisResult;

        // 1. 收益曲线
        this.renderReturnCurve('chart-return-curve', {
            labels: cumulativeReturns.map(d => d.month),
            strategy: cumulativeReturns.map(d => d.strategy),
            benchmark: cumulativeReturns.map(d => d.benchmark)
        });

        // 2. 回撤分析
        this.renderDrawdown('chart-drawdown', {
            labels: drawdowns.map(d => d.month),
            drawdowns: drawdowns.map(d => d.drawdown)
        });

        // 3. 月度收益
        this.renderMonthlyHeatmap('chart-monthly', {
            labels: monthlyReturns.map(d => d.month),
            returns: monthlyReturns.map(d => d.strategyReturn)
        });

        // 4. 资产配置
        this.renderAssetAllocation('chart-allocation', assetAllocation);

        // 5. 指标仪表盘
        this.renderMetricsDashboard('chart-metrics', keyMetrics);

        // 渲染指标表格
        this.renderMetricsTable(keyMetrics);
    },

    /**
     * 渲染关键指标表格
     */
    renderMetricsTable(metrics) {
        const tableBody = document.getElementById('metrics-table-body');
        if (!tableBody) return;

        const rows = [
            { label: '年化收益率', value: metrics.annualReturn, icon: '📈' },
            { label: '夏普比率', value: metrics.sharpeRatio, icon: '📊' },
            { label: '最大回撤', value: metrics.maxDrawdown, icon: '📉' },
            { label: '胜率', value: metrics.winRate, icon: '🎯' },
            { label: '卡玛比率', value: metrics.calmarRatio, icon: '⚖️' },
            { label: '索提诺比率', value: metrics.sortinoRatio, icon: '📐' },
            { label: '年化波动率', value: metrics.volatility, icon: '🌀' },
            { label: '信息比率', value: metrics.informationRatio, icon: 'ℹ️' }
        ];

        tableBody.innerHTML = rows.map(row => `
            <tr>
                <td><span class="metric-icon">${row.icon}</span>${row.label}</td>
                <td class="metric-value">${row.value}</td>
            </tr>
        `).join('');
    }
};

// 导出
if (typeof window !== 'undefined') {
    window.Charts = Charts;
}
