/* ═══════════════════════════════════════════════════════════════
   AZINSU CSI — Core App Module
   Tab routing, fetch helpers, hero metrics
   ═══════════════════════════════════════════════════════════════ */

// ── Fetch Helper ─────────────────────────────────────────────
async function fetchAPI(endpoint) {
    try {
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`[FETCH] ${endpoint}:`, err);
        return null;
    }
}

// ── Vietnamese Number Formatting ─────────────────────────────
function fmtNum(n) {
    if (n == null) return '--';
    return Number(n).toLocaleString('vi-VN');
}

function fmtMoney(n) {
    if (n == null) return '--';
    if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(0) + 'K';
    return fmtNum(n);
}

function severityClass(sev) {
    if (!sev) return 'low';
    const s = sev.toUpperCase();
    if (s === 'CRITICAL' || s.includes('CUC')) return 'critical';
    if (s === 'HIGH' || s.includes('CAO')) return 'high';
    if (s === 'MEDIUM' || s.includes('TRUNG')) return 'medium';
    return 'low';
}

// ── Clock ────────────────────────────────────────────────────
function updateClock() {
    const el = document.getElementById('header-time');
    if (el) el.textContent = new Date().toLocaleString('vi-VN');
}
setInterval(updateClock, 1000);
updateClock();

// ── Tab Routing ──────────────────────────────────────────────
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');
const tabLoaded = {};

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;

        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById('tab-' + tab).classList.add('active');

        // Lazy-load tab data
        if (!tabLoaded[tab]) {
            tabLoaded[tab] = true;
            if (tab === 'network') loadNetwork();
            if (tab === 'audit') loadAuditRules();
            if (tab === 'suspects') loadSuspects();
            if (tab === 'timeline') loadTimeline();
            if (tab === 'diagnosis') loadDiagnosisAnalysis();
            if (tab === 'waiting') loadWaitingPeriodAnalysis();
            if (tab === 'reports') loadReports();
        }
    });
});

// ── Hero Metrics ─────────────────────────────────────────────
async function loadHeroMetrics() {
    const data = await fetchAPI('/api/overview');
    if (!data) return;

    document.getElementById('metric-claims').textContent = fmtNum(data.total_claims);
    document.getElementById('metric-highfreq').textContent = fmtNum(data.high_freq_claimants);
    document.getElementById('metric-anomaly').textContent = data.anomaly_pct + '%';
    document.getElementById('metric-syndicates').textContent = fmtNum(data.syndicates);
}

// ── Audit Rules ──────────────────────────────────────────────
const KEY_MAP = {
    'user_id': 'ID Người dùng',
    'ho_ten': 'Họ và Tên',
    'sdt': 'Số điện thoại',
    'so_ho_so': 'Số hồ sơ',
    'tong_tien': 'Tổng tiền',
    'tu_ngay': 'Từ ngày',
    'den_ngay': 'Đến ngày',
    'ma_benh_vien': 'Mã bệnh viện',
    'ma_bv': 'Mã bệnh viện',
    'chan_doan': 'Chẩn đoán',
    'so_lan_kham': 'Số lần khám',
    'so_nguoi': 'Số người',
    'tong_ho_so': 'Tổng hồ sơ',
    'mau_ten': 'Mẫu tên',
    'stk': 'Số tài khoản',
    'chu_tk': 'Chủ tài khoản',
    'tong_tien_nhan': 'Tổng tiền nhận',
    'bac_si': 'Bác sĩ',
    'so_loai_chan_doan': 'Số loại chẩn đoán',
    'mau_chan_doan': 'Mẫu chẩn đoán',
    'ho_so_nho': 'Hồ sơ < 200k',
    'ti_le_nho_pct': 'Tỷ lệ nhỏ (%)',
    'so_loai_benh': 'Số loại bệnh',
    'so_bv_khac_nhau': 'Số BV khác nhau',
    'mau_bv': 'Mẫu bệnh viện',
    'so_tien_claim': 'Số tiền Claim',
    'trung_vi_benh_ly': 'Trung vị Bệnh lý',
    'he_so_vuot': 'Hệ số vượt',
    'claim_id': 'Mã hồ sơ',
    'danh_muc': 'Danh mục',
    'ten_thuoc_dv': 'Tên Thuốc/DV',
    'don_gia_thuc': 'Đơn giá thực',
    'trung_vi_don_gia': 'Trung vị Đơn giá',
    'so_lan_xh': 'Số lần xuất hiện',
    'tong_phi': 'Tổng phí BH',
    'tong_boi_thuong': 'Tổng bồi thường',
    'ti_le_boi_thuong': 'Tỉ lệ Bồi thường',
    'median_per_diag': 'Trung vị bệnh lý',
    'mien_thuong': 'Số tiền miễn thường',
    'ti_le_tu_choi_pct': 'Tỉ lệ từ chối (%)',
    'ngay_het_han': 'Ngày hết hạn HĐ',
    'ngay_kham': 'Ngày khám/vào viện',
    'ngay_nop': 'Ngày nộp hồ sơ',
    'so_ngay_tre': 'Độ trễ (ngày)',
    'so_ngay_dieu_tri': 'Số ngày điều trị',
    'pathology': 'Bệnh lý',
    'duration': 'Số ngày nằm viện',
    // Rules 16-25
    'ma_hop_dong': 'Mã hợp đồng',
    'goi_bh': 'Gói bảo hiểm',
    'ngay_sau_hd': 'Ngày sau HĐ',
    'ngay_bat_dau_hd': 'Ngày bắt đầu HĐ',
    'ma_bac_si': 'Mã bác sĩ',
    'ten_bac_si': 'Tên bác sĩ',
    'so_benh_nhan': 'Số bệnh nhân',
    'top_benh_nhan': 'Top bệnh nhân',
    'bv_1': 'Bệnh viện 1',
    'bv_2': 'Bệnh viện 2',
    'claim_1': 'Claim 1',
    'claim_2': 'Claim 2',
    'so_ngay_cach': 'Số ngày cách',
    'so_dong_trung': 'Số dòng trùng',
    'ten_thu_huong': 'Tên thụ hưởng',
    'ngan_hang': 'Ngân hàng',
    'ten_dai_ly': 'Tên đại lý',
    'tong_duyet': 'Tổng duyệt',
    'ds_ten': 'Danh sách tên',
    'tong_claims': 'Tổng claims',
    'claims_cuoi_tuan': 'Claims cuối tuần',
    'ti_le_cuoi_tuan': 'Tỷ lệ cuối tuần (%)',
    'ds_claim_id': 'DS Claim ID',
    'benh_ly': 'Bệnh lý'
};

async function loadAuditRules() {
    const data = await fetchAPI('/api/audit-rules');
    if (!data) return;

    const grid = document.getElementById('audit-grid');
    grid.innerHTML = data.map(rule => `
        <div class="audit-card" onclick="showAuditDetail('${rule.rule_id}')">
            <div class="audit-card-header">
                <div>
                    <div class="audit-card-title">${rule.title}</div>
                    <span class="badge ${severityClass(rule.severity)}">${rule.severity}</span>
                </div>
                <div class="audit-card-count">${rule.count}</div>
            </div>
            <div class="audit-card-desc">${rule.description}</div>
        </div>
    `).join('');

    // Store data for detail view
    window._auditData = {};
    data.forEach(r => { window._auditData[r.rule_id] = r; });

    // Also store for charts
    window._auditSummary = data;
}

function showAuditDetail(ruleId) {
    const rule = window._auditData[ruleId];
    if (!rule || !rule.records.length) return;

    const panel = document.getElementById('audit-detail');
    const cols = Object.keys(rule.records[0]);

    let html = `<h3 style="color:var(--accent);margin-bottom:12px">${rule.title}</h3>`;
    html += '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
    cols.forEach(c => { 
        const header = KEY_MAP[c] || c;
        html += `<th>${header}</th>`; 
    });
    html += '</tr></thead><tbody>';
    rule.records.forEach(row => {
        html += '<tr>';
        cols.forEach(c => {
            const v = row[c];
            const display = Array.isArray(v) ? v.join(', ') : (v ?? '');
            const isNum = typeof v === 'number';
            
            // Special handling for Name/User ID/Phone to allow drill-down
            if (c === 'ho_ten' || c === 'user_id' || c === 'sdt') {
                // ho_ten/user_id → dùng user_id để drill-down (không dùng tên)
                const drillId = (c === 'sdt') ? row[c] : (row['user_id'] || row[c]);
                const func = (c === 'sdt') ? 'drillDownPhoneAndStory' : 'drillDownAndStory';
                html += `<td><span class="clickable" onclick="${func}('${drillId}')">${display}</span></td>`;
            } else {
                html += `<td class="${isNum ? 'num' : ''}">${isNum ? fmtNum(v) : display}</td>`;
            }
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    
    panel.innerHTML = html;
    panel.classList.add('show');
}

async function drillDownAndStory(userId) {
    // 1. Switch to network tab and load ego-network
    drillDown(userId); // from app.js but calls graph.js
    
    // 2. Load and render the story
    const storySection = document.getElementById('person-story-section');
    if (!storySection) return;
    
    storySection.style.display = 'block';
    document.getElementById('story-person-name').textContent = userId;
    
    const data = await fetchAPI(`/api/person-story/${userId}`);
    if (!data) return;
    
    renderPersonStory(data);
    
    // 3. Load and render Risk Radar
    const radarData = await fetchAPI(`/api/person-risk-radar/${userId}`);
    if (radarData && window.renderRiskRadar) {
        window.renderRiskRadar(radarData.data);
    }
    
    // Smooth scroll to story
    setTimeout(() => {
        storySection.scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

async function drillDownPhoneAndStory(phone) {
    // 1. Switch to network tab
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanes.forEach(p => p.classList.remove('active'));
    document.querySelector('[data-tab="network"]').classList.add('active');
    document.getElementById('tab-network').classList.add('active');
    
    // 2. Load phone network
    if (window.loadPhoneNetwork) window.loadPhoneNetwork(phone);

    // 3. Load and render phone story
    const storySection = document.getElementById('person-story-section');
    if (!storySection) return;
    
    storySection.style.display = 'block';
    document.getElementById('story-person-name').textContent = `SĐT: ${phone}`;
    
    const data = await fetchAPI(`/api/phone-story/${phone}`);
    if (!data) return;
    
    renderPhoneStory(data);
    
    // Smooth scroll to story
    setTimeout(() => {
        storySection.scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

function renderPersonStory(data) {
    // This will call ECharts functions in charts.js
    if (window.renderPersonTimeline) renderPersonTimeline(data.timeline);
    if (window.renderPersonDiag) renderPersonDiag(data.diagnoses);
    if (window.renderPersonHosp) renderPersonHosp(data.hospitals);
    if (window.renderPersonDoctor) renderPersonDoctor(data.doctors);
    if (window.renderPersonFinancials) renderPersonFinancials(data.timeline);
    
    // Populate Claims Table
    const claimsBody = document.getElementById('story-claims-body');
    if (claimsBody && data.claims) {
        claimsBody.innerHTML = data.claims.map(c => `
            <tr>
                <td><b class="clickable" style="color:var(--accent)" onclick="showClaimDetail('${c.claim_id}')">${c.claim_id}</b></td>
                <td>${c.date}</td>
                <td title="${c.diagnosis}">${c.diagnosis ? c.diagnosis.substring(0, 30) + '...' : 'N/A'}</td>
                <td style="color:var(--accent)">${fmtMoney(c.amount)}</td>
                <td>${c.hospital || 'N/A'}</td>
                <td><button class="btn-sm" onclick="showClaimDetail('${c.claim_id}')">🔬 Soi chi phí</button></td>
            </tr>
        `).join('');
    }

    // Narrative generation
    const totalClaims = data.timeline.reduce((a, b) => a + (b.claim_count || 0), 0);
    const totalReq = data.timeline.reduce((a, b) => a + (b.req_amount || 0), 0);
    const totalAppr = data.timeline.reduce((a, b) => a + (b.approved_amount || 0), 0);
    const topDiag = data.diagnoses[0]?.name || 'không rõ';
    const topHosp = data.hospitals[0]?.name || 'không rõ';
    const topDoctor = data.doctors[0]?.name || 'không rõ';
    
    const denialRatio = totalReq > 0 ? ((totalReq - totalAppr) * 100 / totalReq).toFixed(1) : 0;
    
    document.getElementById('story-narrative').innerHTML = `
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p>👤 <b>Tóm lược Hồ sơ:</b></p>
                <ul>
                    <li>Tổng số: <b>${fmtNum(totalClaims)} hồ sơ</b></li>
                    <li>Tổng yêu cầu: <b>${fmtMoney(totalReq)} VNĐ</b></li>
                    <li>Tổng được duyệt: <b>${fmtMoney(totalAppr)} VNĐ</b></li>
                    <li>Tỷ lệ từ chối: <b style="color:var(--high)">${denialRatio}%</b></li>
                </ul>
            </div>
            <div>
                <p>🏥 <b>Đặc điểm khám chữa bệnh:</b></p>
                <ul>
                    <li>Bệnh lý chính: <b>${topDiag}</b></li>
                    <li>Cơ sở thường xuyên: <b>${topHosp}</b></li>
                    <li>Bác sĩ điều trị chính: <b>${topDoctor}</b></li>
                </ul>
            </div>
        </div>
        <p style="margin-top:15px; padding-top:15px; border-top:1px solid rgba(255,255,255,0.1)">
            📝 <b>Phân tích AI:</b> Dựa trên dòng thời gian, đối tượng có xu hướng tập trung khám chữa bệnh tại <b>${topHosp}</b> 
            với sự chỉ định của bác sĩ <b>${topDoctor}</b>. Khoảng cách giữa số tiền yêu cầu và phê duyệt 
            (${denialRatio}%) cho thấy có nhiều hạng mục chi phí bị xuất toán hoặc không hợp lệ, 
            là dấu hiệu cần kiểm tra thực tế quy trình chỉ định tại cơ sở này.
        </p>
    `;
}

function renderPhoneStory(data) {
    if (window.renderPersonTimeline) renderPersonTimeline(data.timeline);
    if (window.renderPersonDiag) renderPersonDiag(data.diagnoses);
    
    const s = data.stats || {};
    const topDiag = data.diagnoses[0]?.name || 'không rõ';
    const members = (s.member_preview || []).join(', ');

    document.getElementById('story-narrative').innerHTML = `
        Cụm số điện thoại này được chia sẻ bởi <b>${s.num_people || 0} người</b> (bao gồm: ${members}...). 
        Tổng cộng nhóm này đã nộp <b>${fmtNum(s.num_claims || 0)} hồ sơ</b> với tổng tiền bồi thường <b>${fmtNum(s.total_amount || 0)} VNĐ</b>. 
        Các hồ sơ tập trung nhiều nhất vào bệnh lý <b>${topDiag}</b>. 
        Việc chia sẻ một số điện thoại cho nhiều người dùng khác nhau là dấu hiệu điển hình của việc trục lợi có tổ chức hoặc mượn danh tính.
    `;
}

// ── Suspects Table ───────────────────────────────────────────
async function loadSuspects() {
    const data = await fetchAPI('/api/top-suspects?limit=50');
    if (!data || !data.length) return;

    const container = document.getElementById('suspects-table');

    let html = '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
    html += '<th>#</th><th>Họ Tên</th><th>User ID</th><th>Số hồ sơ</th>';
    html += '<th>Tổng bồi thường</th><th>Phí BH</th><th>Tỷ lệ tổn thất</th><th>Điểm rủi ro</th>';
    html += '</tr></thead><tbody>';

    data.forEach((r, i) => {
        const risk = r.composite_risk || 0;
        const riskColor = risk >= 8 ? 'var(--critical)' : risk >= 6 ? 'var(--high)' : risk >= 4 ? 'var(--medium)' : 'var(--low)';
        const barWidth = Math.min(risk * 10, 100);
        const lossRatio = r.total_premium > 0 ? (r.total_approved / r.total_premium) : 0;
        const lossColor = lossRatio > 5 ? 'var(--critical)' : lossRatio > 2 ? 'var(--high)' : 'var(--accent)';

        html += `<tr>
            <td>${i + 1}</td>
            <td>
                <span class="clickable" onclick="drillDownAndStory('${r.user_id}')">${r.full_name || '--'}</span>
            </td>
            <td>${r.user_id || ''}</td>
            <td class="num">${fmtNum(r.num_claims)}</td>
            <td class="num">${fmtMoney(r.total_approved)}</td>
            <td class="num">${fmtMoney(r.total_premium)}</td>
            <td class="num" style="color:${lossColor};font-weight:bold">${lossRatio.toFixed(1)}×</td>
            <td>
                <span class="risk-bar"><span class="risk-bar-fill" style="width:${barWidth}%;background:${riskColor}"></span></span>
                <span style="color:${riskColor}">${risk.toFixed(1)}</span>
            </td>
        </tr>`;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// ── Drill-down (switch to Network tab & load ego-network) ────
function drillDown(userId) {
    // Switch to network tab
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanes.forEach(p => p.classList.remove('active'));
    document.querySelector('[data-tab="network"]').classList.add('active');
    document.getElementById('tab-network').classList.add('active');

    // Load ego-network
    loadEgoNetwork(userId);
}

// ── Diagnosis Analysis ───────────────────────────────────────
async function loadDiagnosisAnalysis() {
    const data = await fetchAPI('/api/diagnosis-stats');
    if (!data || !data.length) return;

    // Render scatter chart
    if (window.renderDiagScatter) renderDiagScatter(data);

    // Render sortable table
    renderDiagTable(data);
}

function renderDiagTable(data) {
    const container = document.getElementById('diag-table-container');
    if (!container) return;

    let sortKey = 'max_vs_median';
    let sortAsc = false;

    function render() {
        const sorted = [...data].sort((a, b) => {
            const va = a[sortKey] ?? 0, vb = b[sortKey] ?? 0;
            return sortAsc ? va - vb : vb - va;
        });

        let html = '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
        const cols = [
            { key: 'diagnosis', label: 'Bệnh lý', num: false },
            { key: 'cnt', label: 'Số HS', num: true },
            { key: 'median_amt', label: 'Trung vị', num: true },
            { key: 'avg_amt', label: 'Bình quân', num: true },
            { key: 'max_amt', label: 'Max', num: true },
            { key: 'max_vs_median', label: 'Hệ số (Max/Median)', num: true },
        ];

        cols.forEach(c => {
            const arrow = sortKey === c.key ? (sortAsc ? ' ▲' : ' ▼') : '';
            html += `<th class="sortable" data-key="${c.key}" style="cursor:pointer">${c.label}${arrow}</th>`;
        });
        html += '</tr></thead><tbody>';

        sorted.forEach(r => {
            const isOutlier = (r.max_vs_median || 0) > 5;
            const rowStyle = isOutlier ? 'background:rgba(255,68,68,0.15)' : '';
            html += `<tr style="${rowStyle};cursor:pointer" onclick="showDiagDetail('${(r.diagnosis || '').replace(/'/g, "\\'")}')">`;
            cols.forEach(c => {
                const v = r[c.key];
                if (c.num) {
                    html += `<td class="num">${fmtNum(v)}</td>`;
                } else {
                    html += `<td>${v || ''}</td>`;
                }
            });
            html += '</tr>';
        });

        html += '</tbody></table></div>';
        container.innerHTML = html;

        // Add sort listeners
        container.querySelectorAll('.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const key = th.dataset.key;
                if (sortKey === key) { sortAsc = !sortAsc; }
                else { sortKey = key; sortAsc = false; }
                render();
            });
        });
    }

    render();
}

async function showDiagDetail(diagnosis) {
    const panel = document.getElementById('diag-detail');
    if (!panel) return;

    panel.innerHTML = '<div class="loading"><div class="spinner"></div> Đang tải chi tiết...</div>';
    panel.classList.add('show');

    const data = await fetchAPI(`/api/diagnosis-detail/${encodeURIComponent(diagnosis)}`);
    if (!data || !data.length) {
        panel.innerHTML = '<p>Không có dữ liệu cho bệnh lý này.</p>';
        return;
    }

    let html = `<h3 style="color:var(--accent);margin-bottom:12px">Chi tiết: ${diagnosis} (${data.length} hồ sơ)</h3>`;
    html += '<div style="overflow-x:auto"><table class="data-table"><thead><tr>';
    html += '<th>User ID</th><th>Họ Tên</th><th>Mã HS</th><th>Số tiền</th><th>Ngày Claim</th><th>Bệnh viện</th>';
    html += '</tr></thead><tbody>';

    data.forEach(r => {
        html += `<tr>
            <td><span class="clickable" onclick="drillDownAndStory('${r.user_id}')">${r.user_id || ''}</span></td>
            <td>${r.ho_ten || ''}</td>
            <td>${r.claim_id || ''}</td>
            <td class="num">${fmtNum(r.so_tien)}</td>
            <td>${r.ngay_claim || ''}</td>
            <td>${r.benh_vien || ''}</td>
        </tr>`;
    });

    html += '</tbody></table></div>';
    panel.innerHTML = html;
    panel.scrollIntoView({ behavior: 'smooth' });
}

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadHeroMetrics();
    // Network tab is active by default
    tabLoaded['network'] = true;
    loadNetwork();
});

// ── Waiting Period Analysis ──────────────────────────────
async function loadWaitingPeriodAnalysis() {
    const data = await fetchAPI('/api/waiting-period-stats');
    if (data && window.renderWaitingHistogram) {
        renderWaitingHistogram(data);
    }
}

async function showWaitingDetail(monthIndex) {
    const section = document.getElementById('waiting-detail-section');
    const title = document.getElementById('waiting-detail-title');
    const tbody = document.getElementById('waiting-detail-body');
    
    if (!section || !title || !tbody) return;
    
    section.style.display = 'block';
    title.innerText = `Danh sách Bệnh lý Nghi vấn (Tháng thứ ${monthIndex + 1})`;
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Đang tải dữ liệu...</td></tr>';
    
    const data = await fetchAPI(`/api/waiting-period-detail/${monthIndex}`);
    if (!data) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--high)">Lỗi tải dữ liệu</td></tr>';
        return;
    }
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">Không có dữ liệu nghi vấn trong tháng này.</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(row => `
        <tr class="${row.is_chronic ? 'row-critical' : ''}">
            <td title="${row.disease}"><b>${row.disease.length > 50 ? row.disease.substring(0, 50) + '...' : row.disease}</b></td>
            <td><a href="#" onclick="drillDownAndStory('${row.user_id}', '${row.person_name}')">${row.person_name}</a></td>
            <td>${row.date}</td>
            <td style="color:var(--accent)">${fmtMoney(row.amount)}</td>
            <td>${row.is_chronic ? '<span class="severity critical">Bệnh mãn tính</span>' : '<span class="severity low">Thông thường</span>'}</td>
            <td><button class="btn-sm" onclick="drillDownAndStory('${row.user_id}', '${row.person_name}')">🔍 Soi</button></td>
        </tr>
    `).join('');
    
    section.scrollIntoView({ behavior: 'smooth' });
}

/** AGGREGATED REPORTS **/
async function loadReports() {
    loadHospitalReport();
    loadDiagnosisReport();
    loadWaitingAnomaliesReport();
}

async function loadHospitalReport() {
    const data = await fetchAPI('/api/reports/top-hospitals');
    if (!data) return;
    const tbody = document.getElementById('report-hospitals-body');
    tbody.innerHTML = data.map(r => {
        const ratio = r.total_req > 0 ? (r.total_approved / r.total_req * 100) : 0;
        return `
            <tr>
                <td><b>${r.name}</b></td>
                <td class="num">${fmtNum(r.frequency)}</td>
                <td class="num">${fmtMoney(r.total_req)}</td>
                <td class="num" style="color:var(--accent)">${fmtMoney(r.total_approved)}</td>
                <td class="num" style="font-weight:bold; color:${ratio < 50 ? 'var(--high)' : 'var(--accent)'}">${ratio.toFixed(1)}%</td>
                <td class="num" style="color:#888">${fmtMoney(r.avg_approved)}</td>
            </tr>
        `;
    }).join('');
}

async function loadDiagnosisReport() {
    const data = await fetchAPI('/api/reports/top-diagnoses');
    if (!data) return;
    window._diagnosisReports = data;
    const tbody = document.getElementById('report-diagnoses-body');
    tbody.innerHTML = data.map((r, idx) => `
        <tr class="clickable" onclick="showDiagnosisSeasonality(${idx})">
            <td><code>${r.code}</code></td>
            <td title="${r.name}">${r.name.length > 30 ? r.name.substring(0,30)+'...' : r.name}</td>
            <td class="num">${fmtNum(r.cases)}</td>
            <td class="num" style="color:var(--accent)">${fmtMoney(r.total_approved)}</td>
            <td><button class="btn-sm">📈 Biểu đồ</button></td>
        </tr>
    `).join('');
    
    // Auto-show first one
    if (data.length > 0) showDiagnosisSeasonality(0);
}

function showDiagnosisSeasonality(idx) {
    const r = window._diagnosisReports[idx];
    if (r && window.renderDiagnosisSeasonality) {
        renderDiagnosisSeasonality(r.name, r.seasonality);
        loadDiagHospitalBreakdown(r.code);
    }
}

async function loadDiagHospitalBreakdown(icd) {
    const data = await fetchAPI(`/api/reports/diagnosis-hospitals/${icd}`);
    if (!data) return;
    
    // Find disease name for chart title
    const diag = window._diagnosisReports.find(r => r.code === icd);
    const diseaseName = diag ? diag.name : icd;

    // Render Table
    const tbody = document.getElementById('report-diag-hospitals-body');
    tbody.innerHTML = data.map(r => `
        <tr>
            <td title="${r.name}" style="font-size:11px">${r.name.length > 25 ? r.name.substring(0,25)+'...' : r.name}</td>
            <td class="num">${fmtNum(r.frequency)}</td>
            <td class="num" style="color:var(--accent)">${fmtMoney(r.avg_approved)}</td>
        </tr>
    `).join('');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; color:#555">Không có dữ liệu CSYT</td></tr>';
    }

    // Render Chart
    if (window.renderDiagHospitalChart) {
        window.renderDiagHospitalChart(diseaseName, data);
    }
}

async function loadWaitingAnomaliesReport() {
    const [listData, diagData] = await Promise.all([
        fetchAPI('/api/reports/waiting-anomalies'),
        fetchAPI('/api/reports/anti-selection-diagnoses')
    ]);
    
    if (listData) {
        const tbody = document.getElementById('report-waiting-anomalies-body');
        tbody.innerHTML = listData.map(r => `
            <tr class="${r.days_diff <= 1 ? 'row-critical' : ''}">
                <td><a href="#" onclick="drillDownAndStory('${r.user_id}', '${r.person}')"><b>${r.person}</b></a></td>
                <td>${r.start_date}</td>
                <td>${r.claim_date}</td>
                <td class="num" style="font-weight:bold">${r.days_diff} ngày</td>
                <td class="num" style="color:var(--accent)">${fmtMoney(r.amount)}</td>
                <td><button class="btn-sm" onclick="drillDownAndStory('${r.user_id}', '${r.person}')">🔍 Soi</button></td>
            </tr>
        `).join('');
    }

    if (diagData && window.renderAntiSelectionDiagChart) {
        window.renderAntiSelectionDiagChart(diagData);
    }
}

/** CLAIM DETAIL DEEP DIVE **/
async function showClaimDetail(claimId) {
    const modal = document.getElementById('claim-modal');
    if (!modal) return;
    
    document.getElementById('modal-claim-id').innerText = claimId;
    modal.style.display = 'flex';
    
    const metaEl = document.getElementById('claim-meta-info');
    const bodyEl = document.getElementById('claim-expenses-body');
    const analysisEl = document.getElementById('claim-cost-analysis');
    
    metaEl.innerHTML = 'Đang tải...';
    bodyEl.innerHTML = '<tr><td colspan="7" style="text-align:center">Đang tải bảng kê...</td></tr>';
    analysisEl.innerHTML = '';

    const data = await fetchAPI(`/api/claim-detail/${claimId}`);
    if (!data) return;

    // Render Meta
    const m = data.meta;
    metaEl.innerHTML = `
        <div><b>🕒 Ngày:</b> ${m.date || '--'}</div>
        <div><b>🏥 BV:</b> ${m.hospital || '--'}</div>
        <div><b>🧑‍⚕️ BS:</b> ${m.doctor || '--'}</div>
        <div><b>👤 Đối tượng:</b> ${m.person || '--'}</div>
        <div><b>📋 Bệnh:</b> ${m.diagnosis || '--'}</div>
        <div><b>💵 Duyệt:</b> <span style="color:var(--accent)">${fmtMoney(m.approved)}</span> / ${fmtMoney(m.req)}</div>
    `;

    // Render Expenses
    let outliersCount = 0;
    bodyEl.innerHTML = data.expenses.map(e => {
        if (e.is_outlier) outliersCount++;
        return `
            <tr class="${e.is_outlier ? 'row-critical' : ''}">
                <td>${e.item}</td>
                <td style="font-size:11px; color:#888">${e.category}</td>
                <td>${e.qty}</td>
                <td>${fmtMoney(e.price)}</td>
                <td style="color:#888">${fmtMoney(e.median)}</td>
                <td><b>${fmtMoney(e.total)}</b></td>
                <td>${e.is_outlier ? '<span class="severity high">⚠️ > 3x Median</span>' : '<span class="severity low">Hợp lý</span>'}</td>
            </tr>
        `;
    }).join('');

    // Analysis
    if (outliersCount > 0) {
        analysisEl.innerHTML = `
            <p>🚨 <b>Phát hiện bất thường:</b> Có <b>${outliersCount}</b> hạng mục chi phí vượt quá 3 lần trung vị của bệnh lý <b>${m.diagnosis}</b>.</p>
            <p style="font-size:12px">Khuyến nghị: Kiểm tra hóa đơn gốc và sự cần thiết y khoa đối với các hạng mục được đánh dấu vàng/đỏ.</p>
        `;
        analysisEl.style.backgroundColor = 'rgba(255,68,68,0.1)';
        analysisEl.style.borderColor = 'var(--high)';
    } else {
        analysisEl.innerHTML = `<p>✅ <b>Kết luận:</b> Các chi phí Thuốc/DV trong hồ sơ này đều nằm trong ngưỡng trung vị hợp lý của bệnh lý tương ứng.</p>`;
        analysisEl.style.backgroundColor = 'rgba(0,255,65,0.05)';
        analysisEl.style.borderColor = 'var(--accent)';
    }
}

function closeClaimModal() {
    document.getElementById('claim-modal').style.display = 'none';
}
