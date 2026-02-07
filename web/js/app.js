/**
 * 彩票分析助手 - 前端应用
 * Lottery Analysis Assistant - Frontend Application
 */

// 全局状态
const state = {
    currentLottery: 'ssq',
    currentPeriod: 100,
    analysisData: null,
    charts: {}
};

// 模拟数据（实际应用中应从后端API获取）
const mockData = {
    ssq: {
        hotNumbers: [
            { number: '09', count: 27, percentage: 27 },
            { number: '02', count: 26, percentage: 26 },
            { number: '13', count: 23, percentage: 23 },
            { number: '03', count: 22, percentage: 22 },
            { number: '24', count: 22, percentage: 22 },
            { number: '08', count: 22, percentage: 22 },
            { number: '04', count: 21, percentage: 21 },
            { number: '05', count: 20, percentage: 20 },
            { number: '10', count: 20, percentage: 20 },
            { number: '19', count: 20, percentage: 20 }
        ],
        coldNumbers: [
            { number: '29', count: 9, percentage: 9 },
            { number: '21', count: 12, percentage: 12 },
            { number: '11', count: 14, percentage: 14 },
            { number: '28', count: 14, percentage: 14 },
            { number: '22', count: 14, percentage: 14 }
        ],
        blueHot: [
            { number: '10', count: 11 },
            { number: '05', count: 9 },
            { number: '08', count: 8 },
            { number: '15', count: 8 },
            { number: '16', count: 8 }
        ],
        missing: [
            { number: '17', count: 17 },
            { number: '14', count: 16 },
            { number: '11', count: 15 },
            { number: '21', count: 13 },
            { number: '08', count: 12 }
        ],
        oddEven: { '3:3': 37, '4:2': 25, '2:4': 20, '1:5': 10, '5:1': 7, '6:0': 1 },
        bigSmall: { '3:3': 38, '2:4': 24, '4:2': 24, '1:5': 10, '5:1': 3, '0:6': 1 },
        heatmap: [
            { number: '01', count: 16, level: 'heat-1' },
            { number: '02', count: 26, level: 'hot-3' },
            { number: '03', count: 22, level: 'hot-3' },
            { number: '04', count: 21, level: 'hot-2' },
            { number: '05', count: 20, level: 'hot-2' },
            { number: '06', count: 20, level: 'hot-2' },
            { number: '07', count: 15, level: 'heat-0' },
            { number: '08', count: 22, level: 'hot-3' },
            { number: '09', count: 27, level: 'hot-3' },
            { number: '10', count: 20, level: 'hot-2' },
            { number: '11', count: 14, level: 'heat-0' },
            { number: '12', count: 17, level: 'heat-1' },
            { number: '13', count: 23, level: 'hot-3' },
            { number: '14', count: 18, level: 'hot-1' },
            { number: '15', count: 19, level: 'hot-1' },
            { number: '16', count: 17, level: 'heat-1' },
            { number: '17', count: 19, level: 'hot-1' },
            { number: '18', count: 18, level: 'hot-1' },
            { number: '19', count: 20, level: 'hot-2' },
            { number: '20', count: 16, level: 'heat-1' },
            { number: '21', count: 12, level: 'heat-0' },
            { number: '22', count: 14, level: 'heat-0' },
            { number: '23', count: 17, level: 'heat-1' },
            { number: '24', count: 22, level: 'hot-3' },
            { number: '25', count: 17, level: 'heat-1' },
            { number: '26', count: 17, level: 'heat-1' },
            { number: '27', count: 16, level: 'heat-1' },
            { number: '28', count: 14, level: 'heat-0' },
            { number: '29', count: 9, level: 'heat-0' },
            { number: '30', count: 18, level: 'hot-1' },
            { number: '31', count: 17, level: 'heat-1' },
            { number: '32', count: 18, level: 'hot-1' },
            { number: '33', count: 19, level: 'hot-1' }
        ],
        stats: {
            consecutiveRate: 74,
            consecutivePeriods: 74,
            mostCommon: '12-13',
            sumMin: 46,
            sumMax: 134,
            sumAvg: 96.76
        }
    },
    dlt: {
        oddEven: { '3:2': 30, '2:3': 27, '1:4': 22, '4:1': 18, '5:0': 3 },
        bigSmall: { '2:3': 34, '3:2': 29, '4:1': 14, '1:4': 14, '0:5': 5, '5:0': 4 },
        stats: {
            consecutiveRate: 55,
            consecutivePeriods: 55,
            mostCommon: '34-35',
            sumMin: 33,
            sumMax: 155,
            sumAvg: 87.75
        }
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initTabs();
    loadReports();
});

// 导航功能
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            showSection(targetId);
            
            // 更新活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// 显示指定部分
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// 标签页功能
function initTabs() {
    // 固定号码分析标签
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // 更新按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 更新面板
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(tabId + '-panel').classList.add('active');
        });
    });
}

// 切换彩种
function switchLottery(type) {
    state.currentLottery = type;
    
    // 更新按钮状态
    document.querySelectorAll('.lottery-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-type') === type) {
            btn.classList.add('active');
        }
    });
}

// 运行分析
function runAnalysis() {
    const period = document.getElementById('periodSelect').value;
    state.currentPeriod = period;
    
    // 显示加载状态
    const resultsContainer = document.getElementById('analysisResults');
    resultsContainer.innerHTML = `
        <div class="placeholder">
            <i class="fas fa-spinner fa-spin"></i>
            <p>正在分析数据，请稍候...</p>
        </div>
    `;
    
    // 模拟异步加载
    setTimeout(() => {
        renderAnalysisResults();
    }, 500);
}

// 渲染分析结果
function renderAnalysisResults() {
    const data = mockData[state.currentLottery];
    const container = document.getElementById('analysisResults');
    
    if (state.currentLottery === 'ssq') {
        container.innerHTML = `
            <div class="analysis-grid">
                <!-- 热号冷号 -->
                <div class="analysis-card">
                    <h3><i class="fas fa-fire"></i> 热号 TOP10</h3>
                    <table class="data-table">
                        <thead>
                            <tr><th>排名</th><th>号码</th><th>次数</th><th>频率</th></tr>
                        </thead>
                        <tbody>
                            ${data.hotNumbers.map((n, i) => `
                                <tr>
                                    <td>${i + 1}</td>
                                    <td><span class="ball red">${n.number}</span></td>
                                    <td>${n.count}</td>
                                    <td>${n.percentage}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <div class="analysis-card">
                    <h3><i class="fas fa-snowflake"></i> 冷号 TOP10</h3>
                    <table class="data-table">
                        <thead>
                            <tr><th>排名</th><th>号码</th><th>次数</th><th>频率</th></tr>
                        </thead>
                        <tbody>
                            ${data.coldNumbers.map((n, i) => `
                                <tr>
                                    <td>${i + 1}</td>
                                    <td><span class="ball red">${n.number}</span></td>
                                    <td>${n.count}</td>
                                    <td>${n.percentage}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <!-- 蓝球热号 -->
                <div class="analysis-card">
                    <h3><i class="fas fa-fire"></i> 蓝球热号 TOP5</h3>
                    <div class="ball-grid">
                        ${data.blueHot.map(n => `
                            <div class="ball-item">
                                <span class="ball blue">${n.number}</span>
                                <span class="count">${n.count}次</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- 遗漏值 -->
                <div class="analysis-card">
                    <h3><i class="fas fa-clock"></i> 遗漏值 TOP10</h3>
                    <table class="data-table">
                        <thead>
                            <tr><th>号码</th><th>遗漏期数</th></tr>
                        </thead>
                        <tbody>
                            ${data.missing.map(n => `
                                <tr>
                                    <td><span class="ball red">${n.number}</span></td>
                                    <td class="missing-${n.count > 15 ? 'high' : n.count > 10 ? 'medium' : 'low'}">${n.count}期</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <!-- 热力图 -->
                <div class="analysis-card full-width">
                    <h3><i class="fas fa-th"></i> 号码分布热力图</h3>
                    <div class="heatmap">
                        ${data.heatmap.map(h => `
                            <div class="heatmap-cell ${h.level}" title="${h.number}号: ${h.count}次">
                                ${h.number}
                            </div>
                        `).join('')}
                    </div>
                    <div class="heatmap-legend">
                        <span><span class="legend-color hot-3"></span> 最热</span>
                        <span><span class="legend-color hot-2"></span> 很热</span>
                        <span><span class="legend-color hot-1"></span> 较热</span>
                        <span><span class="legend-color heat-1"></span> 温热</span>
                        <span><span class="legend-color heat-0"></span> 微温</span>
                    </div>
                </div>
                
                <!-- 图表 -->
                <div class="analysis-card">
                    <h3><i class="fas fa-chart-pie"></i> 奇偶比分布</h3>
                    <canvas id="oddEvenChart"></canvas>
                </div>
                
                <div class="analysis-card">
                    <h3><i class="fas fa-chart-pie"></i> 大小比分布</h3>
                    <canvas id="bigSmallChart"></canvas>
                </div>
                
                <!-- 统计信息 -->
                <div class="analysis-card full-width">
                    <h3><i class="fas fa-info-circle"></i> 统计概览</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">连号出现率</span>
                            <span class="stat-value">${data.stats.consecutiveRate}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">最常见连号</span>
                            <span class="stat-value">${data.stats.mostCommon}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">平均和值</span>
                            <span class="stat-value">${data.stats.sumAvg}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">和值范围</span>
                            <span class="stat-value">${data.stats.sumMin}-${data.stats.sumMax}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 初始化图表
        initCharts();
    } else {
        // 大乐透分析结果
        container.innerHTML = `
            <div class="analysis-grid">
                <div class="analysis-card">
                    <h3><i class="fas fa-chart-pie"></i> 奇偶比分布</h3>
                    <canvas id="oddEvenChartDlt"></canvas>
                </div>
                <div class="analysis-card">
                    <h3><i class="fas fa-chart-pie"></i> 大小比分布</h3>
                    <canvas id="bigSmallChartDlt"></canvas>
                </div>
                <div class="analysis-card full-width">
                    <h3><i class="fas fa-info-circle"></i> 统计概览</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">连号出现率</span>
                            <span class="stat-value">${data.stats.consecutiveRate}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">最常见连号</span>
                            <span class="stat-value">${data.stats.mostCommon}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">平均和值</span>
                            <span class="stat-value">${data.stats.sumAvg}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        initChartsDlt();
    }
}

// 初始化图表
function initCharts() {
    const data = mockData.ssq;
    
    // 奇偶比饼图
    const oddEvenCtx = document.getElementById('oddEvenChart');
    if (oddEvenCtx) {
        new Chart(oddEvenCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.oddEven),
                datasets: [{
                    data: Object.values(data.oddEven),
                    backgroundColor: [
                        '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
    
    // 大小比饼图
    const bigSmallCtx = document.getElementById('bigSmallChart');
    if (bigSmallCtx) {
        new Chart(bigSmallCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.bigSmall),
                datasets: [{
                    data: Object.values(data.bigSmall),
                    backgroundColor: [
                        '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
}

// 大乐透图表
function initChartsDlt() {
    const data = mockData.dlt;
    
    const oddEvenCtx = document.getElementById('oddEvenChartDlt');
    if (oddEvenCtx) {
        new Chart(oddEvenCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.oddEven),
                datasets: [{
                    data: Object.values(data.oddEven),
                    backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
    
    const bigSmallCtx = document.getElementById('bigSmallChartDlt');
    if (bigSmallCtx) {
        new Chart(bigSmallCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.bigSmall),
                datasets: [{
                    data: Object.values(data.bigSmall),
                    backgroundColor: ['#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
}

// 分析固定号码
function analyzeFixedNumbers() {
    const isSsq = document.getElementById('ssq-fixed-panel').classList.contains('active');
    
    let fixedRed = [];
    let fixedBlue = [];
    
    if (isSsq) {
        // 获取双色球号码
        for (let i = 1; i <= 6; i++) {
            const val = document.getElementById(`ssq-red-${i}`).value;
            if (val) fixedRed.push(parseInt(val));
        }
        const blueVal = document.getElementById('ssq-blue-1').value;
        if (blueVal) fixedBlue.push(parseInt(blueVal));
    } else {
        // 获取大乐透号码
        for (let i = 1; i <= 5; i++) {
            const val = document.getElementById(`dlt-front-${i}`).value;
            if (val) fixedRed.push(parseInt(val));
        }
        for (let i = 1; i <= 2; i++) {
            const val = document.getElementById(`dlt-back-${i}`).value;
            if (val) fixedBlue.push(parseInt(val));
        }
    }
    
    if (fixedRed.length === 0 && fixedBlue.length === 0) {
        alert('请至少输入一个号码');
        return;
    }
    
    // 显示分析结果
    const resultPanel = document.getElementById('fixedAnalysisResult');
    resultPanel.innerHTML = `
        <div class="fixed-result">
            <h3>📊 固定号码分析结果</h3>
            <div class="result-section">
                <h4>输入号码</h4>
                <div class="input-balls">
                    ${isSsq ? `
                        <div class="red-balls-display">
                            <span class="label">红球:</span>
                            ${fixedRed.map(n => `<span class="ball red">${n.toString().padStart(2, '0')}</span>`).join('')}
                        </div>
                        ${fixedBlue.length > 0 ? `
                            <div class="blue-balls-display">
                                <span class="label">蓝球:</span>
                                <span class="ball blue">${fixedBlue[0].toString().padStart(2, '0')}</span>
                            </div>
                        ` : ''}
                    ` : `
                        <div class="red-balls-display">
                            <span class="label">前区:</span>
                            ${fixedRed.map(n => `<span class="ball red">${n.toString().padStart(2, '0')}</span>`).join('')}
                        </div>
                        ${fixedBlue.length > 0 ? `
                            <div class="blue-balls-display">
                                <span class="label">后区:</span>
                                ${fixedBlue.map(n => `<span class="ball blue">${n.toString().padStart(2, '0')}</span>`).join('')}
                            </div>
                        ` : ''}
                    `}
                </div>
            </div>
            
            <div class="result-section">
                <h4>组合评估</h4>
                <div class="evaluation">
                    <div class="eval-item">
                        <span class="label">奇偶比:</span>
                        <span class="value">${calculateOddEven(fixedRed)}</span>
                        <span class="score">⭐⭐⭐⭐⭐</span>
                    </div>
                    <div class="eval-item">
                        <span class="label">大小比:</span>
                        <span class="value">${calculateBigSmall(fixedRed, isSsq)}</span>
                        <span class="score">⭐⭐⭐⭐⭐</span>
                    </div>
                </div>
            </div>
            
            <div class="result-section">
                <h4>历史表现（模拟数据）</h4>
                <table class="data-table">
                    <thead>
                        <tr><th>号码</th><th>出现次数</th><th>频率</th><th>状态</th></tr>
                    </thead>
                    <tbody>
                        ${fixedRed.map(n => `
                            <tr>
                                <td><span class="ball red">${n.toString().padStart(2, '0')}</span></td>
                                <td>${Math.floor(Math.random() * 30) + 20}次</td>
                                <td>${(Math.random() * 10 + 10).toFixed(1)}%</td>
                                <td><span class="status hot">热号</span></td>
                            </tr>
                        `).join('')}
                        ${fixedBlue.map(n => `
                            <tr>
                                <td><span class="ball blue">${n.toString().padStart(2, '0')}</span></td>
                                <td>${Math.floor(Math.random() * 15) + 5}次</td>
                                <td>${(Math.random() * 5 + 3).toFixed(1)}%</td>
                                <td><span class="status normal">正常</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

// 计算奇偶比
function calculateOddEven(numbers) {
    const odd = numbers.filter(n => n % 2 === 1).length;
    const even = numbers.length - odd;
    return `${odd}:${even}`;
}

// 计算大小比
function calculateBigSmall(numbers, isSsq) {
    const boundary = isSsq ? 17 : 18;
    const big = numbers.filter(n => n >= boundary).length;
    const small = numbers.length - big;
    return `${big}:${small}`;
}

// 生成组合
function generateCombinations() {
    analyzeFixedNumbers(); // 先进行分析
    
    const resultPanel = document.getElementById('fixedAnalysisResult');
    const existingContent = resultPanel.innerHTML;
    
    // 添加生成的组合
    resultPanel.innerHTML = existingContent + `
        <div class="result-section">
            <h4>🎲 推荐组合（娱乐性质）</h4>
            <div class="combinations">
                ${[1, 2, 3].map(i => `
                    <div class="combination-item">
                        <span class="combo-number">组合 ${i}</span>
                        <div class="combo-balls">
                            ${generateRandomCombo()}
                        </div>
                    </div>
                `).join('')}
            </div>
            <p class="disclaimer-text">⚠️ 以上组合仅供娱乐参考，不构成投注建议</p>
        </div>
    `;
}

// 生成随机组合（模拟）
function generateRandomCombo() {
    const reds = [];
    while (reds.length < 6) {
        const n = Math.floor(Math.random() * 33) + 1;
        if (!reds.includes(n)) reds.push(n);
    }
    reds.sort((a, b) => a - b);
    const blue = Math.floor(Math.random() * 16) + 1;
    
    return `
        <span class="balls red">${reds.map(n => n.toString().padStart(2, '0')).join(' ')}</span>
        <span class="balls blue">${blue.toString().padStart(2, '0')}</span>
    `;
}

// 清空输入
function clearFixedInputs() {
    document.querySelectorAll('.ball-input').forEach(input => {
        input.value = '';
    });
    document.getElementById('fixedAnalysisResult').innerHTML = `
        <div class="result-placeholder">
            <i class="fas fa-chart-pie"></i>
            <p>输入您的固定号码，点击"分析号码"查看结果</p>
        </div>
    `;
}

// 加载历史报告
function loadReports() {
    const grid = document.getElementById('reportsGrid');
    if (!grid) return;
    
    const reports = [
        { title: '双色球100期分析报告', date: '2026-02-08', type: 'ssq', size: '245 KB' },
        { title: '大乐透100期分析报告', date: '2026-02-08', type: 'dlt', size: '198 KB' },
        { title: '双色球热号统计分析', date: '2026-02-07', type: 'ssq', size: '156 KB' },
        { title: '遗漏值深度分析', date: '2026-02-06', type: 'ssq', size: '134 KB' }
    ];
    
    grid.innerHTML = reports.map(r => `
        <div class="report-card">
            <div class="report-header">
                <span class="report-icon">${r.type === 'ssq' ? '🔴' : '🔵'}</span>
                <span class="report-type">${r.type === 'ssq' ? '双色球' : '大乐透'}</span>
            </div>
            <h4 class="report-title">${r.title}</h4>
            <div class="report-meta">
                <span><i class="fas fa-calendar"></i> ${r.date}</span>
                <span><i class="fas fa-file"></i> ${r.size}</span>
            </div>
            <button class="btn btn-primary btn-sm" onclick="viewReport('${r.title}')">
                <i class="fas fa-eye"></i> 查看报告
            </button>
        </div>
    `).join('');
}

// 查看报告
function viewReport(title) {
    alert(`正在打开报告: ${title}\n\n在实际应用中，这里会打开详细的HTML报告。`);
}

// 更新分析
function updateAnalysis() {
    // 期数改变时的处理
    state.currentPeriod = document.getElementById('periodSelect').value;
}
