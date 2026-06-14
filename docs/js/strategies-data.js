/**
 * 共轭智能全球投资策略平台 - 前端策略数据缓存
 * 用于快速渲染策略列表，与后端策略数据结构对应
 */

const StrategiesData = {
    // 策略分类
    categories: [
        { id: 'stock', name: '股票策略', icon: '📈', color: '#e94560' },
        { id: 'bond', name: '债券策略', icon: '🏦', color: '#00d084' },
        { id: 'option', name: '期权策略', icon: '⚡', color: '#f5c518' },
        { id: 'futures', name: '期货策略', icon: '🔥', color: '#4fc3f7' }
    ],

    // 策略列表
    strategies: [
        // 股票策略
        {
            id: 'stock-alpha-01',
            name: 'Alpha多因子选股策略',
            category: 'stock',
            description: '基于机器学习的多因子选股模型，结合基本面、技术面和市场情绪因子，通过共轭梯度优化算法筛选优质标的。',
            riskLevel: '中高',
            annualReturn: '18.5%',
            maxDrawdown: '-12.3%',
            sharpeRatio: '1.85',
            winRate: '62%',
            status: 'active',
            tags: ['机器学习', '多因子', 'A股'],
            minInvestment: '10万',
            createdAt: '2025-01-15'
        },
        {
            id: 'stock-momentum-02',
            name: '动量反转轮动策略',
            category: 'stock',
            description: '捕捉市场动量效应与均值回归机会，动态调整行业配置权重，实现风险调整后的超额收益。',
            riskLevel: '中',
            annualReturn: '15.2%',
            maxDrawdown: '-9.8%',
            sharpeRatio: '1.62',
            winRate: '58%',
            status: 'active',
            tags: ['动量', '轮动', '行业配置'],
            minInvestment: '5万',
            createdAt: '2025-02-20'
        },
        {
            id: 'stock-value-03',
            name: '深度价值挖掘策略',
            category: 'stock',
            description: '基于深度学习的企业价值评估模型，识别被市场低估的优质公司，长期持有等待价值回归。',
            riskLevel: '中',
            annualReturn: '14.8%',
            maxDrawdown: '-8.5%',
            sharpeRatio: '1.75',
            winRate: '65%',
            status: 'active',
            tags: ['价值投资', '深度学习', '长期持有'],
            minInvestment: '10万',
            createdAt: '2025-03-10'
        },
        {
            id: 'stock-quant-04',
            name: '高频量化交易策略',
            category: 'stock',
            description: '基于微秒级行情数据的统计套利策略，利用市场微观结构中的定价偏差进行快速交易。',
            riskLevel: '高',
            annualReturn: '25.3%',
            maxDrawdown: '-15.6%',
            sharpeRatio: '2.10',
            winRate: '55%',
            status: 'active',
            tags: ['高频交易', '统计套利', '微观结构'],
            minInvestment: '50万',
            createdAt: '2025-04-05'
        },

        // 债券策略
        {
            id: 'bond-duration-01',
            name: '智能久期管理策略',
            category: 'bond',
            description: '基于利率周期预测模型，动态调整债券组合久期，在控制信用风险的同时优化收益风险比。',
            riskLevel: '低',
            annualReturn: '6.8%',
            maxDrawdown: '-2.1%',
            sharpeRatio: '2.35',
            winRate: '78%',
            status: 'active',
            tags: ['久期管理', '利率预测', '信用风险'],
            minInvestment: '5万',
            createdAt: '2025-01-20'
        },
        {
            id: 'bond-credit-02',
            name: '信用债增强策略',
            category: 'bond',
            description: '利用NLP技术分析企业信用舆情，结合传统信用评级模型，挖掘信用利差收窄机会。',
            riskLevel: '中',
            annualReturn: '8.5%',
            maxDrawdown: '-3.5%',
            sharpeRatio: '1.95',
            winRate: '72%',
            status: 'active',
            tags: ['信用分析', 'NLP', '利差交易'],
            minInvestment: '10万',
            createdAt: '2025-02-15'
        },
        {
            id: 'bond-convert-03',
            name: '可转债套利策略',
            category: 'bond',
            description: '基于期权定价理论的可转债定价模型，识别转股溢价率异常的可转债进行套利交易。',
            riskLevel: '中低',
            annualReturn: '10.2%',
            maxDrawdown: '-4.2%',
            sharpeRatio: '2.05',
            winRate: '68%',
            status: 'active',
            tags: ['可转债', '套利', '期权定价'],
            minInvestment: '5万',
            createdAt: '2025-03-25'
        },

        // 期权策略
        {
            id: 'option-vol-01',
            name: '波动率曲面套利策略',
            category: 'option',
            description: '基于局部波动率模型的期权定价系统，实时监控波动率曲面异常，执行Delta中性套利。',
            riskLevel: '高',
            annualReturn: '22.1%',
            maxDrawdown: '-11.5%',
            sharpeRatio: '1.90',
            winRate: '60%',
            status: 'active',
            tags: ['波动率', '套利', 'Delta中性'],
            minInvestment: '20万',
            createdAt: '2025-01-30'
        },
        {
            id: 'option-spread-02',
            name: '多腿价差组合策略',
            category: 'option',
            description: '利用AI优化算法构建最优多腿期权价差组合，在限定风险预算下最大化期望收益。',
            riskLevel: '中高',
            annualReturn: '16.8%',
            maxDrawdown: '-8.9%',
            sharpeRatio: '1.72',
            winRate: '63%',
            status: 'active',
            tags: ['价差', '组合优化', '风险管理'],
            minInvestment: '10万',
            createdAt: '2025-02-28'
        },
        {
            id: 'option-tail-03',
            name: '尾部风险对冲策略',
            category: 'option',
            description: '基于极值理论的市场崩盘预测模型，动态配置尾部风险对冲工具，保护组合免受黑天鹅事件冲击。',
            riskLevel: '低',
            annualReturn: '5.2%',
            maxDrawdown: '-1.8%',
            sharpeRatio: '1.55',
            winRate: '85%',
            status: 'active',
            tags: ['尾部风险', '对冲', '极值理论'],
            minInvestment: '50万',
            createdAt: '2025-04-10'
        },

        // 期货策略
        {
            id: 'futures-cta-01',
            name: 'CTA趋势跟踪策略',
            category: 'futures',
            description: '跨品种、跨周期的趋势跟踪系统，结合自适应止损和仓位管理，在趋势行情中获取超额收益。',
            riskLevel: '中高',
            annualReturn: '20.5%',
            maxDrawdown: '-13.2%',
            sharpeRatio: '1.68',
            winRate: '52%',
            status: 'active',
            tags: ['CTA', '趋势跟踪', '跨品种'],
            minInvestment: '20万',
            createdAt: '2025-01-10'
        },
        {
            id: 'futures-spread-02',
            name: '跨期套利策略',
            category: 'futures',
            description: '基于协整关系的跨期价差交易模型，在价差偏离均值时建仓，等待均值回归获利。',
            riskLevel: '中低',
            annualReturn: '12.3%',
            maxDrawdown: '-5.1%',
            sharpeRatio: '2.15',
            winRate: '70%',
            status: 'active',
            tags: ['跨期套利', '协整', '均值回归'],
            minInvestment: '10万',
            createdAt: '2025-03-05'
        },
        {
            id: 'futures-macro-03',
            name: '宏观对冲策略',
            category: 'futures',
            description: '基于宏观经济指标和央行政策分析，构建股、债、汇、商品多资产对冲组合。',
            riskLevel: '中',
            annualReturn: '14.6%',
            maxDrawdown: '-7.8%',
            sharpeRatio: '1.82',
            winRate: '60%',
            status: 'active',
            tags: ['宏观对冲', '多资产', '政策分析'],
            minInvestment: '50万',
            createdAt: '2025-04-20'
        },
        {
            id: 'futures-hft-04',
            name: '期货高频做市策略',
            category: 'futures',
            description: '基于深度强化学习的做市策略，在提供流动性的同时赚取买卖价差，实现稳定收益。',
            riskLevel: '高',
            annualReturn: '28.7%',
            maxDrawdown: '-6.5%',
            sharpeRatio: '2.85',
            winRate: '75%',
            status: 'active',
            tags: ['做市', '强化学习', '高频'],
            minInvestment: '100万',
            createdAt: '2025-05-01'
        }
    ],

    // 根据分类获取策略
    getByCategory(categoryId) {
        return this.strategies.filter(s => s.category === categoryId);
    },

    // 搜索策略
    search(keyword) {
        const kw = keyword.toLowerCase();
        return this.strategies.filter(s =>
            s.name.toLowerCase().includes(kw) ||
            s.description.toLowerCase().includes(kw) ||
            s.tags.some(t => t.toLowerCase().includes(kw))
        );
    },

    // 获取策略详情
    getById(strategyId) {
        return this.strategies.find(s => s.id === strategyId);
    },

    // 获取分类信息
    getCategoryInfo(categoryId) {
        return this.categories.find(c => c.id === categoryId);
    },

    // 获取统计数据
    getStats() {
        return {
            totalStrategies: this.strategies.length,
            activeStrategies: this.strategies.filter(s => s.status === 'active').length,
            avgReturn: '16.1%',
            avgSharpe: '1.91',
            categories: this.categories.length
        };
    },

    // 模拟分析结果数据
    getMockAnalysisResult(strategyId) {
        const strategy = this.getById(strategyId);
        if (!strategy) return null;

        // 生成模拟的月度收益数据（12个月）
        const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
        const baseReturn = parseFloat(strategy.annualReturn) / 100 / 12;

        const monthlyReturns = months.map((m, i) => ({
            month: m,
            strategyReturn: parseFloat(((baseReturn + (Math.random() - 0.4) * 0.03) * 100).toFixed(2)),
            benchmarkReturn: parseFloat(((0.005 + (Math.random() - 0.5) * 0.02) * 100).toFixed(2))
        }));

        // 累计收益曲线
        let cumStrategy = 0;
        let cumBenchmark = 0;
        const cumulativeReturns = months.map((m, i) => {
            cumStrategy += monthlyReturns[i].strategyReturn / 100;
            cumBenchmark += monthlyReturns[i].benchmarkReturn / 100;
            return {
                month: m,
                strategy: parseFloat((cumStrategy * 100).toFixed(2)),
                benchmark: parseFloat((cumBenchmark * 100).toFixed(2))
            };
        });

        // 回撤数据
        let peak = 0;
        const drawdowns = cumulativeReturns.map(d => {
            if (d.strategy > peak) peak = d.strategy;
            return {
                month: d.month,
                drawdown: parseFloat((d.strategy - peak).toFixed(2))
            };
        });

        // 资产配置
        const assetAllocation = [
            { name: '股票', value: 45, color: '#e94560' },
            { name: '债券', value: 25, color: '#00d084' },
            { name: '商品', value: 15, color: '#f5c518' },
            { name: '现金', value: 10, color: '#4fc3f7' },
            { name: '另类', value: 5, color: '#ab47bc' }
        ];

        // 关键指标
        const keyMetrics = {
            annualReturn: strategy.annualReturn,
            sharpeRatio: strategy.sharpeRatio,
            maxDrawdown: strategy.maxDrawdown,
            winRate: strategy.winRate,
            calmarRatio: (parseFloat(strategy.annualReturn) / Math.abs(parseFloat(strategy.maxDrawdown))).toFixed(2),
            sortinoRatio: (parseFloat(strategy.sharpeRatio) * 1.2).toFixed(2),
            volatility: (Math.abs(parseFloat(strategy.maxDrawdown)) * 0.8).toFixed(1) + '%',
            informationRatio: '0.85'
        };

        return {
            strategy: strategy,
            monthlyReturns,
            cumulativeReturns,
            drawdowns,
            assetAllocation,
            keyMetrics
        };
    }
};

// 导出（浏览器环境直接挂载到 window）
if (typeof window !== 'undefined') {
    window.StrategiesData = StrategiesData;
}
