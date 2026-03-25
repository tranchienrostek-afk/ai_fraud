/* ═══════════════════════════════════════════════════════════════
   AZINSU CSI — ECharts Module
   Timeline, Heatmap, Audit Bar Chart
   ═══════════════════════════════════════════════════════════════ */

const ECHARTS_DARK = {
    backgroundColor: 'transparent',
    textStyle: { fontFamily: '"JetBrains Mono", monospace', color: '#888' },
};

async function loadTimeline() {
    // Load timeline + heatmap + audit bar in parallel
    const [timelineData, heatmapData] = await Promise.all([
        fetchAPI('/api/timeline'),
        fetchAPI('/api/heatmap'),
    ]);

    renderTimeline(timelineData);
    renderHeatmap(heatmapData);
    renderAuditBar();
}

// ── Timeline Chart ───────────────────────────────────────────
function renderTimeline(data) {
    const el = document.getElementById('chart-timeline');
    if (!el || !data || !data.length) return;

    const chart = echarts.init(el);

    const months = data.map(d => d.month);
    const counts = data.map(d => d.claim_count);
    const amounts = data.map(d => d.total_amount);

    chart.setOption({
        ...ECHARTS_DARK,
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(10,10,10,0.9)',
            borderColor: '#00ff41',
            textStyle: { color: '#e0e0e0', fontFamily: '"JetBrains Mono", monospace', fontSize: 11 },
        },
        legend: {
            data: ['Số hồ sơ', 'Tổng số tiền'],
            textStyle: { color: '#888' },
            top: 0,
        },
        grid: { left: 60, right: 60, top: 40, bottom: 30 },
        xAxis: {
            type: 'category',
            data: months,
            axisLine: { lineStyle: { color: '#2a2a2a' } },
            axisLabel: { color: '#888', fontSize: 10, rotate: 45 },
        },
        yAxis: [
            {
                type: 'value',
                name: 'Hồ sơ',
                nameTextStyle: { color: '#00ff41' },
                axisLine: { lineStyle: { color: '#2a2a2a' } },
                splitLine: { lineStyle: { color: '#1a1a1a' } },
                axisLabel: { color: '#888', fontSize: 10 },
            },
            {
                type: 'value',
                name: 'Số tiền (VNĐ)',
                nameTextStyle: { color: '#ff8c00' },
                axisLine: { lineStyle: { color: '#2a2a2a' } },
                splitLine: { show: false },
                axisLabel: {
                    color: '#888',
                    fontSize: 10,
                    formatter: function(v) {
                        if (v >= 1e9) return (v / 1e9).toFixed(0) + 'B';
                        if (v >= 1e6) return (v / 1e6).toFixed(0) + 'M';
                        return v;
                    },
                },
            },
        ],
        series: [
            {
                name: 'Số hồ sơ',
                type: 'bar',
                data: counts,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#00ff41' },
                        { offset: 1, color: 'rgba(0,255,65,0.2)' },
                    ]),
                },
                barMaxWidth: 30,
            },
            {
                name: 'Tổng số tiền',
                type: 'line',
                yAxisIndex: 1,
                data: amounts,
                lineStyle: { color: '#ff8c00', width: 2 },
                itemStyle: { color: '#ff8c00' },
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
            },
        ],
    });

    window.addEventListener('resize', () => chart.resize());
}

// ── Heatmap Chart ────────────────────────────────────────────
function renderHeatmap(data) {
    const el = document.getElementById('chart-heatmap');
    if (!el || !data || !data.length) return;

    const chart = echarts.init(el);

    // Extract unique months and days
    const months = [...new Set(data.map(d => d.month))].sort();
    const days = Array.from({ length: 31 }, (_, i) => i + 1);

    // Build heatmap data: [monthIndex, dayIndex, value]
    const heatmapPoints = [];
    let maxVal = 0;

    data.forEach(d => {
        const mi = months.indexOf(d.month);
        const di = (d.day_of_month || 1) - 1;
        const v = d.cnt || 0;
        if (v > maxVal) maxVal = v;
        heatmapPoints.push([mi, di, v]);
    });

    chart.setOption({
        ...ECHARTS_DARK,
        tooltip: {
            position: 'top',
            backgroundColor: 'rgba(10,10,10,0.9)',
            borderColor: '#00ff41',
            textStyle: { color: '#e0e0e0', fontSize: 11 },
            formatter: function(p) {
                return `${months[p.data[0]]} | Ngày ${p.data[1] + 1}<br/>Số hồ sơ: <b>${p.data[2]}</b>`;
            },
        },
        grid: { left: 50, right: 20, top: 10, bottom: 50 },
        xAxis: {
            type: 'category',
            data: months,
            axisLabel: { color: '#888', fontSize: 9, rotate: 45 },
            axisLine: { lineStyle: { color: '#2a2a2a' } },
            splitArea: { show: false },
        },
        yAxis: {
            type: 'category',
            data: days.map(String),
            axisLabel: { color: '#888', fontSize: 9 },
            axisLine: { lineStyle: { color: '#2a2a2a' } },
            splitArea: { show: false },
        },
        visualMap: {
            min: 0,
            max: maxVal || 100,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: 0,
            inRange: {
                color: ['#0a0a0a', '#003300', '#006600', '#00cc33', '#00ff41'],
            },
            textStyle: { color: '#888', fontSize: 10 },
        },
        series: [{
            type: 'heatmap',
            data: heatmapPoints,
            emphasis: {
                itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,255,65,0.5)' },
            },
        }],
    });

    window.addEventListener('resize', () => chart.resize());
}

// ── Audit Bar Chart ──────────────────────────────────────────
function renderAuditBar() {
    const el = document.getElementById('chart-audit-bar');
    if (!el) return;

    // Wait for audit data
    const tryRender = () => {
        const data = window._auditSummary;
        if (!data) {
            // Load audit data if not yet loaded
            fetchAPI('/api/audit-rules').then(d => {
                window._auditSummary = d;
                doRender(d);
            });
            return;
        }
        doRender(data);
    };

    function doRender(data) {
        if (!data || !data.length) return;

        const chart = echarts.init(el);
        const sevColors = {
            CRITICAL: '#ff4444',
            HIGH: '#ff8c00',
            MEDIUM: '#ffd700',
            LOW: '#90ee90',
        };

        const names = data.map(d => d.title.length > 25 ? d.title.slice(0, 25) + '...' : d.title);
        const counts = data.map(d => d.count);
        const colors = data.map(d => sevColors[d.severity] || '#888');

        chart.setOption({
            ...ECHARTS_DARK,
            tooltip: {
                backgroundColor: 'rgba(10,10,10,0.9)',
                borderColor: '#00ff41',
                textStyle: { color: '#e0e0e0', fontSize: 11 },
            },
            grid: { left: 180, right: 30, top: 10, bottom: 20 },
            xAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#2a2a2a' } },
                splitLine: { lineStyle: { color: '#1a1a1a' } },
                axisLabel: { color: '#888', fontSize: 10 },
            },
            yAxis: {
                type: 'category',
                data: names,
                inverse: true,
                axisLine: { lineStyle: { color: '#2a2a2a' } },
                axisLabel: { color: '#e0e0e0', fontSize: 10 },
            },
            series: [{
                type: 'bar',
                data: counts.map((v, i) => ({
                    value: v,
                    itemStyle: { color: colors[i] },
                })),
                barMaxWidth: 20,
                label: {
                    show: true,
                    position: 'right',
                    color: '#e0e0e0',
                    fontSize: 11,
                    fontWeight: 'bold',
                },
            }],
        });

        window.addEventListener('resize', () => chart.resize());
    }

    tryRender();
}
// ── Person Story Mini-Charts ─────────────────────────────────
function renderPersonTimeline(data) {
    const el = document.getElementById('story-chart-timeline');
    if (!el || !data) return;
    const chart = echarts.init(el);
    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'Tần suất & Số tiền (Duyệt)', textStyle: { color: '#888', fontSize: 12 } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.map(d => d.month), axisLabel: { fontSize: 9 } },
        yAxis: [
            { type: 'value', name: 'HS', axisLabel: { fontSize: 9 } }, 
            { type: 'value', name: 'Duyệt', axisLabel: { fontSize: 9, formatter: v => fmtMoney(v) } }
        ],
        series: [
            { name: 'Hồ sơ', type: 'bar', data: data.map(d => d.claim_count), itemStyle: { color: '#00ff41' } },
            { name: 'Số tiền duyệt', type: 'line', yAxisIndex: 1, data: data.map(d => d.approved_amount), itemStyle: { color: '#ff8c00' } }
        ]
    });
}

function renderPersonDiag(data) {
    const el = document.getElementById('story-chart-diag');
    if (!el || !data) return;
    const chart = echarts.init(el);
    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'Cơ cấu Bệnh lý', textStyle: { color: '#888', fontSize: 12 } },
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: data,
            label: { show: true, fontSize: 9, color: '#aaa' },
            itemStyle: { borderRadius: 4 }
        }]
    });
}

function renderPersonHosp(data) {
    const el = document.getElementById('story-chart-hosp');
    if (!el || !data) return;
    const chart = echarts.init(el);
    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'Phân bổ Cơ sở Y tế', textStyle: { color: '#888', fontSize: 12 } },
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: data,
            label: { show: true, fontSize: 9, color: '#aaa' },
            itemStyle: { borderRadius: 4 }
        }]
    });
}

function renderPersonDoctor(data) {
    const el = document.getElementById('story-chart-doctor');
    if (!el || !data) return;
    const chart = echarts.init(el);
    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'Phân bổ Bác sĩ', textStyle: { color: '#888', fontSize: 12 } },
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            data: data,
            label: { show: true, fontSize: 9, color: '#aaa' },
            itemStyle: { borderRadius: 4 }
        }]
    });
}

function renderPersonFinancials(data) {
    const el = document.getElementById('story-chart-financials');
    if (!el || !data) return;
    const chart = echarts.init(el);
    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'So sánh Số tiền Yêu cầu vs Duyệt (VNĐ)', textStyle: { color: '#00ff41', fontSize: 12 } },
        tooltip: { trigger: 'axis' },
        legend: { data: ['Yêu cầu', 'Đã duyệt'], textStyle: { color: '#888' }, top: 25 },
        grid: { left: 60, right: 30, top: 60, bottom: 30 },
        xAxis: { type: 'category', data: data.map(d => d.month), axisLabel: { fontSize: 9 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 9, formatter: v => fmtMoney(v) } },
        series: [
            { 
                name: 'Yêu cầu', type: 'line', data: data.map(d => d.req_amount), 
                lineStyle: { color: '#ff4444', width: 2 }, itemStyle: { color: '#ff4444' }
            },
            { 
                name: 'Đã duyệt', type: 'line', data: data.map(d => d.approved_amount), 
                lineStyle: { color: '#00ff41', width: 2 }, itemStyle: { color: '#00ff41' },
                areaStyle: { color: 'rgba(0,255,65,0.1)' }
            }
        ]
    });
}

// ── Diagnosis Scatter Chart ─────────────────────────────────
function renderDiagScatter(data) {
    const el = document.getElementById('chart-diag-scatter');
    if (!el || !data || !data.length) return;

    const chart = echarts.init(el);

    // Normalize bubble size: sqrt scale based on cnt
    const maxCnt = Math.max(...data.map(d => d.cnt || 1));
    const minSize = 8, maxSize = 40;

    const normalPts = [];
    const outlierPts = [];

    data.forEach(d => {
        const median = d.median_amt || 0;
        const max = d.max_amt || 0;
        const ratio = d.max_vs_median || 0;
        const size = minSize + (maxSize - minSize) * Math.sqrt((d.cnt || 1) / maxCnt);
        const point = {
            value: [median, max, d.cnt, ratio],
            symbolSize: size,
            name: d.diagnosis,
            _data: d,
        };
        if (ratio > 3) {
            outlierPts.push(point);
        } else {
            normalPts.push(point);
        }
    });

    // Reference line y=3x: from origin to max median
    const maxMedian = Math.max(...data.map(d => d.median_amt || 0));
    const lineData = [[0, 0], [maxMedian, maxMedian * 3]];

    chart.setOption({
        ...ECHARTS_DARK,
        tooltip: {
            backgroundColor: 'rgba(10,10,10,0.95)',
            borderColor: '#00ff41',
            textStyle: { color: '#e0e0e0', fontFamily: '"JetBrains Mono", monospace', fontSize: 11 },
            formatter: function(p) {
                const d = p.data._data;
                if (!d) return '';
                return `<b>${d.diagnosis}</b><br/>` +
                    `Số HS: ${(d.cnt || 0).toLocaleString('vi-VN')}<br/>` +
                    `Trung vị: ${(d.median_amt || 0).toLocaleString('vi-VN')} đ<br/>` +
                    `Max: ${(d.max_amt || 0).toLocaleString('vi-VN')} đ<br/>` +
                    `Hệ số: <b style="color:${(d.max_vs_median || 0) > 3 ? '#ff4444' : '#00ff41'}">${d.max_vs_median}×</b>`;
            },
        },
        legend: {
            data: ['Bình thường', 'Bất thường (>3×)'],
            textStyle: { color: '#888' },
            top: 0,
        },
        grid: { left: 80, right: 40, top: 50, bottom: 50 },
        xAxis: {
            type: 'value',
            name: 'Trung vị (VNĐ)',
            nameTextStyle: { color: '#00ff41', fontSize: 11 },
            axisLine: { lineStyle: { color: '#2a2a2a' } },
            splitLine: { lineStyle: { color: '#1a1a1a' } },
            axisLabel: {
                color: '#888', fontSize: 10,
                formatter: function(v) {
                    if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
                    if (v >= 1e3) return (v / 1e3).toFixed(0) + 'K';
                    return v;
                },
            },
        },
        yAxis: {
            type: 'value',
            name: 'Max Claim (VNĐ)',
            nameTextStyle: { color: '#ff8c00', fontSize: 11 },
            axisLine: { lineStyle: { color: '#2a2a2a' } },
            splitLine: { lineStyle: { color: '#1a1a1a' } },
            axisLabel: {
                color: '#888', fontSize: 10,
                formatter: function(v) {
                    if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
                    if (v >= 1e3) return (v / 1e3).toFixed(0) + 'K';
                    return v;
                },
            },
        },
        series: [
            {
                name: 'Bình thường',
                type: 'scatter',
                data: normalPts,
                itemStyle: { color: 'rgba(0,255,65,0.7)', borderColor: '#00ff41', borderWidth: 1 },
            },
            {
                name: 'Bất thường (>3×)',
                type: 'scatter',
                data: outlierPts,
                itemStyle: { color: 'rgba(255,68,68,0.7)', borderColor: '#ff4444', borderWidth: 1 },
            },
            {
                name: 'Ngưỡng 3×',
                type: 'line',
                data: lineData,
                lineStyle: { color: '#ff4444', width: 2, type: 'dashed' },
                symbol: 'none',
                tooltip: { show: false },
            },
        ],
    });

    chart.on('click', function(params) {
        if (params.data && params.data.name && params.seriesType === 'scatter') {
            if (window.showDiagDetail) showDiagDetail(params.data.name);
        }
    });

    window.addEventListener('resize', () => chart.resize());
}

// ── Waiting Period Analysis ──────────────────────────────
window.renderWaitingHistogram = function(data) {
    const el = document.getElementById('chart-waiting-histogram');
    if (!el || !data) return;
    const chart = echarts.init(el);
    
    // Ensure 12 months are represented
    const months = Array.from({length: 12}, (_, i) => `Tháng ${i+1}`);
    const counts = new Array(12).fill(0);
    const amounts = new Array(12).fill(0);
    
    data.forEach(d => {
        if (d.month_offset >= 0 && d.month_offset < 12) {
            counts[d.month_offset] = d.claim_count;
            amounts[d.month_offset] = d.total_approved;
        }
    });

    chart.setOption({
        ...ECHARTS_DARK,
        tooltip: { 
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: { data: ['Số lượng hồ sơ', 'Số tiền (Duyệt)'], textStyle: { color: '#888' }, top: 5 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', data: months, axisLabel: { interval: 0, fontSize: 10 } },
        yAxis: [
            { type: 'value', name: 'Số hồ sơ', axisLabel: { fontSize: 10 } },
            { type: 'value', name: 'Số tiền', axisLabel: { fontSize: 10, formatter: v => (v/1e6).toFixed(1) + 'M' } }
        ],
        series: [
            { 
                name: 'Số lượng hồ sơ', type: 'bar', data: counts, 
                itemStyle: { color: '#00ff41', borderRadius: [4, 4, 0, 0] },
                barMaxWidth: 40
            },
            { 
                name: 'Số tiền (Duyệt)', type: 'line', yAxisIndex: 1, data: amounts, 
                itemStyle: { color: '#ff8c00' },
                lineStyle: { width: 3 }
            }
        ]
    });

    chart.on('click', function(params) {
        const monthIndex = params.dataIndex; // 0-indexed month_offset
        if (window.showWaitingDetail) window.showWaitingDetail(monthIndex);
    });
};

// ── Diagnosis Seasonality ──────────────────────────────
window.renderDiagnosisSeasonality = function(name, data) {
    const el = document.getElementById('chart-diagnosis-seasonality');
    if (!el || !data) return;
    const chart = echarts.init(el);
    
    const months = Array.from({length: 12}, (_, i) => `T${i+1}`);

    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: `Biểu đồ mùa vụ: ${name}`, textStyle: { color: '#888', fontSize: 13 }, top: 5, left: 5 },
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', data: months, boundaryGap: false },
        yAxis: { type: 'value', name: 'Số ca' },
        series: [{
            name: 'Số ca',
            type: 'line',
            data: data,
            smooth: true,
            lineStyle: { color: '#00ff41', width: 3 },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(0,255,65,0.3)' },
                    { offset: 1, color: 'rgba(0,255,65,0)' }
                ])
            },
            itemStyle: { color: '#00ff41' }
        }]
    });
    window.addEventListener('resize', () => chart.resize());
};

window.renderDiagHospitalChart = function(diseaseName, data) {
    const el = document.getElementById('chart-diag-hospital');
    if (!el || !data) return;
    const chart = echarts.init(el);
    
    const names = data.map(r => r.name.length > 20 ? r.name.substring(0,20)+'...' : r.name);
    const frequencies = data.map(r => r.frequency);
    const avgCosts = data.map(r => r.avg_approved);

    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: `So sánh CSYT cho: ${diseaseName}`, textStyle: { color: '#888', fontSize: 13 }, top: 5, left: 5 },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        legend: { data: ['Tần suất', 'Trung bình Duyệt'], textStyle: { color: '#888' }, top: 30 },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '25%', containLabel: true },
        xAxis: { 
            type: 'category', 
            data: names, 
            axisLabel: { interval: 0, rotate: 30, fontSize: 10 } 
        },
        yAxis: [
            { type: 'value', name: 'Tần suất', axisLabel: { fontSize: 10 } },
            { 
                type: 'value', 
                name: 'Chi phí (VNĐ)', 
                axisLabel: { 
                    fontSize: 10,
                    formatter: v => (v/1e6).toFixed(1) + 'M'
                } 
            }
        ],
        series: [
            {
                name: 'Tần suất',
                type: 'bar',
                data: frequencies,
                itemStyle: { color: '#00ff41', borderRadius: [4, 4, 0, 0] },
                barMaxWidth: 30
            },
            {
                name: 'Trung bình Duyệt',
                type: 'line',
                yAxisIndex: 1,
                data: avgCosts,
                lineStyle: { color: '#ff8c00', width: 2 },
                itemStyle: { color: '#ff8c00' },
                symbol: 'circle',
                symbolSize: 8
            }
        ]
    });
    window.addEventListener('resize', () => chart.resize());
};

window.renderAntiSelectionDiagChart = function(data) {
    const el = document.getElementById('chart-anti-selection-diag');
    if (!el || !data) return;
    const chart = echarts.init(el);
    
    chart.setOption({
        ...ECHARTS_DARK,
        tooltip: { trigger: 'item', formatter: '{b}: <b>{c} ca</b> ({d}%)' },
        series: [{
            name: 'Bệnh lý',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: true,
            itemStyle: { borderRadius: 10, borderColor: '#0a0a0a', borderWidth: 2 },
            label: { show: true, fontSize: 10, color: '#aaa', formatter: '{b}\n{d}%' },
            data: data
        }]
    });
    window.addEventListener('resize', () => chart.resize());
};

window.renderRiskRadar = function(data) {
    const el = document.getElementById('story-chart-radar');
    if (!el || !data) return;
    const chart = echarts.init(el);

    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: 'Radar Rủi ro Cá nhân', textStyle: { color: '#00f2fe', fontSize: 14 } },
        tooltip: { trigger: 'item' },
        radar: {
            indicator: [
                { name: 'Tần suất', max: 100 },
                { name: 'Hồ sơ nhỏ', max: 100 },
                { name: 'Bồi thường', max: 100 },
                { name: 'Thời gian đ.trị', max: 100 },
                { name: 'Độ trễ nộp', max: 100 }
            ],
            splitArea: { show: false },
            splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } },
            axisLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.2)' } }
        },
        series: [{
            name: 'Chỉ số rủi ro',
            type: 'radar',
            data: [{
                value: data,
                name: 'Rủi ro cá nhân',
                areaStyle: { color: 'rgba(0, 242, 254, 0.3)' },
                lineStyle: { color: '#00f2fe', width: 2 },
                itemStyle: { color: '#00f2fe' }
            }]
        }]
    });
    window.addEventListener('resize', () => chart.resize());
};

window.renderEntityRadar = function(elementId, title, labels, data, color) {
    const el = document.getElementById(elementId);
    if (!el || !data) return;
    const chart = echarts.init(el);
    const rgba = color === '#ff8c00' ? 'rgba(255,140,0,0.3)'
               : color === '#ff4444' ? 'rgba(255,68,68,0.3)'
               : 'rgba(0, 242, 254, 0.3)';

    chart.setOption({
        ...ECHARTS_DARK,
        title: { text: title, textStyle: { color: color, fontSize: 13 } },
        tooltip: { trigger: 'item' },
        radar: {
            indicator: labels.map(l => ({ name: l, max: 100 })),
            splitArea: { show: false },
            splitLine: { lineStyle: { color: color.replace(')', ',0.15)').replace('rgb', 'rgba') } },
            axisLine: { lineStyle: { color: color.replace(')', ',0.2)').replace('rgb', 'rgba') } },
            axisName: { color: '#888', fontSize: 10 }
        },
        series: [{
            type: 'radar',
            data: [{
                value: data,
                name: title,
                areaStyle: { color: rgba },
                lineStyle: { color: color, width: 2 },
                itemStyle: { color: color }
            }]
        }]
    });
    window.addEventListener('resize', () => chart.resize());
};
