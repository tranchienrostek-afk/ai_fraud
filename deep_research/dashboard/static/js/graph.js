/* ═══════════════════════════════════════════════════════════════
   AZINSU CSI — Cytoscape.js Network Graph Module
   Neo4j-style: Inspector, Expand, Cascading Hide
   ═══════════════════════════════════════════════════════════════ */

let cy = null;

// Track expand ancestry: parentId -> Set of child IDs added by expand
const _expandTree = {};
// Currently selected element
let _selectedEle = null;

const NODE_COLORS = {
    Person:   '#ff4444',
    Bank:     '#ce93d8',
    Phone:    '#00ff41',
    Hospital: '#4fc3f7',
    Claim:    '#ffd700',
    Doctor:   '#00e5ff',
    Expense:  '#ff8c00',
    Insurer:  '#90ee90',
};

const NODE_SHAPES = {
    Person:   'ellipse',
    Bank:     'diamond',
    Phone:    'hexagon',
    Hospital: 'rectangle',
    Claim:    'round-triangle',
    Doctor:   'star',
    Expense:  'round-rectangle',
    Insurer:  'pentagon',
};

const EDGE_COLORS = {
    SHARED_BANK:  '#ce93d8',
    SHARED_PHONE: '#00ff41',
    SUBMITTED:    '#888888',
    TREATED_AT:   '#4fc3f7',
    PAID_TO:      '#ce93d8',
    EXAMINED_BY:  '#00e5ff',
    HAS_EXPENSE:  '#ff8c00',
    HANDLED_BY:   '#90ee90',
};

const TYPE_LABELS = {
    Person: 'Người bệnh',
    Bank: 'Tài khoản Ngân hàng',
    Phone: 'Số điện thoại',
    Hospital: 'Cơ sở Y tế',
    Claim: 'Hồ sơ Claim',
    Doctor: 'Bác sĩ',
    Expense: 'Chi phí (Thuốc/DV)',
    Insurer: 'Công ty Bảo hiểm',
    SHARED_BANK: 'Chung TK Ngân hàng',
    SHARED_PHONE: 'Chung SĐT',
    SUBMITTED: 'Nộp hồ sơ',
    TREATED_AT: 'Khám tại',
    PAID_TO: 'Thanh toán về',
    EXAMINED_BY: 'Bác sĩ khám',
    HAS_EXPENSE: 'Chi phí',
    HANDLED_BY: 'Xử lý bởi',
};

function initCytoscape(container, elements) {
    if (cy) cy.destroy();
    // Reset expand tree on new graph
    Object.keys(_expandTree).forEach(k => delete _expandTree[k]);
    _selectedEle = null;
    closeInspector();

    cy = cytoscape({
        container: container,
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'font-size': '9px',
                    'font-family': '"JetBrains Mono", monospace',
                    'color': '#e0e0e0',
                    'text-outline-color': '#0a0a0a',
                    'text-outline-width': 2,
                    'text-valign': 'bottom',
                    'text-margin-y': 5,
                    'background-color': function(ele) {
                        return NODE_COLORS[ele.data('type')] || '#888';
                    },
                    'shape': function(ele) {
                        return NODE_SHAPES[ele.data('type')] || 'ellipse';
                    },
                    'width': function(ele) {
                        return ele.data('type') === 'Person' ? 25 : 18;
                    },
                    'height': function(ele) {
                        return ele.data('type') === 'Person' ? 25 : 18;
                    },
                    'border-width': 2,
                    'border-color': '#0a0a0a',
                },
            },
            {
                selector: 'node:selected',
                style: {
                    'border-color': '#00ff41',
                    'border-width': 3,
                    'overlay-color': '#00ff41',
                    'overlay-opacity': 0.15,
                },
            },
            {
                selector: 'node.expanded',
                style: {
                    'border-color': '#00e5ff',
                    'border-width': 3,
                    'border-style': 'double',
                },
            },
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': function(ele) {
                        return EDGE_COLORS[ele.data('type')] || '#444';
                    },
                    'line-style': function(ele) {
                        return ele.data('type') === 'SHARED_PHONE' ? 'dashed' : 'solid';
                    },
                    'curve-style': 'bezier',
                    'opacity': 0.7,
                    'target-arrow-shape': function(ele) {
                        const t = ele.data('type');
                        return (t === 'SHARED_BANK' || t === 'SHARED_PHONE') ? 'none' : 'triangle';
                    },
                    'target-arrow-color': function(ele) {
                        return EDGE_COLORS[ele.data('type')] || '#444';
                    },
                    'arrow-scale': 0.8,
                },
            },
            {
                selector: 'edge:selected',
                style: {
                    'width': 3,
                    'opacity': 1,
                    'overlay-color': '#00ff41',
                    'overlay-opacity': 0.1,
                },
            },
        ],
        layout: {
            name: 'cose',
            nodeRepulsion: function() { return 8000; },
            idealEdgeLength: function() { return 80; },
            edgeElasticity: function() { return 100; },
            gravity: 0.3,
            numIter: 500,
            animate: true,
            animationDuration: 800,
        },
        minZoom: 0.2,
        maxZoom: 5,
    });

    // ── Tap on Node → show inspector ──
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        _selectedEle = node;
        showNodeInspector(node);
    });

    // ── Tap on Edge → show inspector ──
    cy.on('tap', 'edge', function(evt) {
        const edge = evt.target;
        _selectedEle = edge;
        showEdgeInspector(edge);
    });

    // ── Tap on background → close inspector ──
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            _selectedEle = null;
            closeInspector();
        }
    });

    return cy;
}

// ── Inspector: Show Node Properties ──────────────────────────
function showNodeInspector(node) {
    const panel = document.getElementById('inspector-panel');
    const typeEl = document.getElementById('inspector-type');
    const bodyEl = document.getElementById('inspector-body');
    const actionsEl = document.getElementById('inspector-actions');
    if (!panel) return;

    const data = node.data();
    const nodeType = data.type || 'Unknown';
    const color = NODE_COLORS[nodeType] || '#888';

    // Type badge
    typeEl.innerHTML = `<span class="type-badge" style="background:${color}22;color:${color};border:1px solid ${color}">${TYPE_LABELS[nodeType] || nodeType}</span>`;

    // Properties table
    const props = buildNodeProps(data);
    let html = '<table>';
    props.forEach(([key, val]) => {
        html += `<tr><td>${key}</td><td>${val}</td></tr>`;
    });

    // Connected edges summary
    const connEdges = node.connectedEdges();
    const neighbors = node.neighborhood().nodes();
    html += `<tr><td>Kết nối</td><td>${connEdges.length} cạnh, ${neighbors.length} nút</td></tr>`;
    html += '</table>';

    bodyEl.innerHTML = html;

    // Show actions
    actionsEl.style.display = 'flex';

    // Load radar for Hospital/Doctor
    const radarEl = document.getElementById('inspector-radar');
    if (radarEl) {
        if (nodeType === 'Hospital') {
            radarEl.style.display = 'block';
            const code = (data.id || '').replace('H:', '');
            fetchAPI(`/api/hospital-risk-radar/${encodeURIComponent(code)}`).then(res => {
                if (res && window.renderEntityRadar) {
                    renderEntityRadar('inspector-radar', '🏥 Radar CSYT', res.labels, res.data, '#ff8c00');
                }
            });
        } else if (nodeType === 'Doctor') {
            radarEl.style.display = 'block';
            const name = data.label || '';
            fetchAPI(`/api/doctor-risk-radar/${encodeURIComponent(name)}`).then(res => {
                if (res && window.renderEntityRadar) {
                    renderEntityRadar('inspector-radar', '🧑‍⚕️ Radar Bác sĩ', res.labels, res.data, '#ff4444');
                }
            });
        } else {
            radarEl.style.display = 'none';
        }
    }

    panel.classList.add('open');
}

function buildNodeProps(data) {
    const props = [];
    props.push(['ID', data.id || '--']);
    if (data.label) props.push(['Nhãn', data.label]);
    if (data.type) props.push(['Loại', TYPE_LABELS[data.type] || data.type]);
    if (data.amount != null) props.push(['Số tiền', Number(data.amount).toLocaleString('vi-VN') + ' đ']);
    if (data.diagnosis) props.push(['Chẩn đoán', data.diagnosis]);
    if (data.claim_date) props.push(['Ngày claim', data.claim_date]);
    // Show all other data keys
    const skip = new Set(['id', 'label', 'type', 'amount', 'diagnosis', 'claim_date']);
    Object.keys(data).forEach(k => {
        if (!skip.has(k) && data[k] != null && data[k] !== '') {
            const val = typeof data[k] === 'number' ? Number(data[k]).toLocaleString('vi-VN') : data[k];
            props.push([k, val]);
        }
    });
    return props;
}

// ── Inspector: Show Edge Properties ──────────────────────────
function showEdgeInspector(edge) {
    const panel = document.getElementById('inspector-panel');
    const typeEl = document.getElementById('inspector-type');
    const bodyEl = document.getElementById('inspector-body');
    const actionsEl = document.getElementById('inspector-actions');
    if (!panel) return;

    const data = edge.data();
    const edgeType = data.type || 'UNKNOWN';
    const color = EDGE_COLORS[edgeType] || '#444';

    typeEl.innerHTML = `<span class="type-badge" style="background:${color}22;color:${color};border:1px solid ${color}">Cạnh: ${TYPE_LABELS[edgeType] || edgeType}</span>`;

    const srcNode = edge.source();
    const tgtNode = edge.target();

    let html = '<table>';
    html += `<tr><td>Loại</td><td>${TYPE_LABELS[edgeType] || edgeType}</td></tr>`;
    html += `<tr><td>Từ</td><td>${srcNode.data('label') || srcNode.id()} <span style="color:${NODE_COLORS[srcNode.data('type')] || '#888'}">(${TYPE_LABELS[srcNode.data('type')] || srcNode.data('type')})</span></td></tr>`;
    html += `<tr><td>Đến</td><td>${tgtNode.data('label') || tgtNode.id()} <span style="color:${NODE_COLORS[tgtNode.data('type')] || '#888'}">(${TYPE_LABELS[tgtNode.data('type')] || tgtNode.data('type')})</span></td></tr>`;
    html += '</table>';

    bodyEl.innerHTML = html;

    // Hide node-specific actions for edges
    actionsEl.style.display = 'none';

    panel.classList.add('open');
}

// ── Close Inspector ──────────────────────────────────────────
function closeInspector() {
    const panel = document.getElementById('inspector-panel');
    if (panel) panel.classList.remove('open');
}

// ── Expand Node: fetch neighbors and add to graph ────────────
async function expandNode(nodeId) {
    if (!cy) return;

    const node = cy.getElementById(nodeId);
    if (node.empty()) return;

    // Mark as expanded
    node.addClass('expanded');

    const data = await fetchAPI(`/api/node-neighbors/${encodeURIComponent(nodeId)}`);
    if (!data || (!data.nodes.length && !data.edges.length)) return;

    const addedIds = new Set();

    // Add new nodes
    data.nodes.forEach(n => {
        if (cy.getElementById(n.id).empty()) {
            cy.add({
                group: 'nodes',
                data: {
                    id: n.id,
                    label: truncate(n.label, 25),
                    type: n.type,
                    amount: n.amount,
                    diagnosis: n.diagnosis,
                    claim_date: n.claim_date,
                },
            });
            addedIds.add(n.id);
        }
    });

    // Add new edges
    data.edges.forEach(e => {
        const edgeId = `${e.source}-${e.type}-${e.target}`;
        if (cy.getElementById(edgeId).empty()) {
            // Only add edge if both source and target exist
            if (!cy.getElementById(e.source).empty() && !cy.getElementById(e.target).empty()) {
                cy.add({
                    group: 'edges',
                    data: {
                        id: edgeId,
                        source: e.source,
                        target: e.target,
                        type: e.type,
                    },
                });
            }
        }
    });

    // Record expand tree for cascading hide
    if (!_expandTree[nodeId]) _expandTree[nodeId] = new Set();
    addedIds.forEach(id => _expandTree[nodeId].add(id));

    // Re-layout only the new nodes around the expanded node
    if (addedIds.size > 0) {
        const pos = node.position();
        // Position new nodes around parent first
        const newNodes = cy.collection();
        addedIds.forEach(id => {
            const n = cy.getElementById(id);
            if (!n.empty()) newNodes.merge(n);
        });

        // Run incremental layout on new nodes
        const layout = newNodes.layout({
            name: 'concentric',
            boundingBox: {
                x1: pos.x - 150,
                y1: pos.y - 150,
                x2: pos.x + 150,
                y2: pos.y + 150,
            },
            animate: true,
            animationDuration: 400,
            fit: false,
        });
        layout.run();
    }
}

// ── Hide Node: cascading removal of all descendants ──────────
function hideNode(nodeId) {
    if (!cy) return;

    // Collect all descendant IDs recursively
    const toRemove = new Set();
    collectDescendants(nodeId, toRemove);

    // Remove descendants first (deepest first via the set)
    toRemove.forEach(id => {
        const ele = cy.getElementById(id);
        if (!ele.empty()) {
            cy.remove(ele);
        }
        // Clean up expand tree entries
        delete _expandTree[id];
    });

    // Remove the node itself
    const node = cy.getElementById(nodeId);
    if (!node.empty()) {
        cy.remove(node);
    }
    delete _expandTree[nodeId];

    // Also clean references from parent expand trees
    Object.values(_expandTree).forEach(childSet => {
        childSet.delete(nodeId);
    });

    // Close inspector
    _selectedEle = null;
    closeInspector();
}

function collectDescendants(nodeId, result) {
    const children = _expandTree[nodeId];
    if (!children) return;
    children.forEach(childId => {
        if (!result.has(childId)) {
            result.add(childId);
            collectDescendants(childId, result);
        }
    });
}


// ── Wire up Inspector buttons ────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const btnExpand = document.getElementById('btn-expand');
    const btnHide = document.getElementById('btn-hide');
    const btnClose = document.getElementById('inspector-close');

    if (btnExpand) {
        btnExpand.addEventListener('click', () => {
            if (_selectedEle && _selectedEle.isNode()) {
                expandNode(_selectedEle.id());
            }
        });
    }

    if (btnHide) {
        btnHide.addEventListener('click', () => {
            if (_selectedEle && _selectedEle.isNode()) {
                hideNode(_selectedEle.id());
            }
        });
    }

    if (btnClose) {
        btnClose.addEventListener('click', () => {
            _selectedEle = null;
            closeInspector();
            if (cy) cy.$(':selected').unselect();
        });
    }
});


// ── Existing functions (loadNetwork, loadEgoNetwork, etc.) ───

async function loadNetwork() {
    const loading = document.getElementById('graph-loading');
    if (loading) loading.style.display = 'flex';

    const data = await fetchAPI('/api/syndicates');
    if (loading) loading.style.display = 'none';

    if (!data || !data.nodes.length) {
        document.getElementById('cy-container').innerHTML =
            '<div class="loading">No syndicate data available</div>';
        return;
    }

    const elements = [];

    data.nodes.forEach(n => {
        elements.push({
            data: {
                id: n.id,
                label: truncate(n.label, 20),
                type: n.type,
            },
        });
    });

    data.edges.forEach(e => {
        elements.push({
            data: {
                source: e.source,
                target: e.target,
                type: e.type,
            },
        });
    });

    initCytoscape(document.getElementById('cy-container'), elements);
}

async function loadEgoNetwork(userId) {
    const loading = document.getElementById('graph-loading');
    if (loading) {
        loading.style.display = 'flex';
        loading.querySelector('div:last-child') &&
            (loading.lastElementChild.textContent = `Đang tải mạng lưới cho ${userId}...`);
    }

    const data = await fetchAPI(`/api/network/${userId}`);
    if (loading) loading.style.display = 'none';

    if (!data || !data.nodes.length) return;

    const elements = [];

    data.nodes.forEach(n => {
        elements.push({
            data: {
                id: n.id,
                label: truncate(n.label, 25),
                type: n.type,
                amount: n.amount,
                diagnosis: n.diagnosis,
            },
        });
    });

    data.edges.forEach(e => {
        elements.push({
            data: {
                source: e.source,
                target: e.target,
                type: e.type,
            },
        });
    });

    initCytoscape(document.getElementById('cy-container'), elements);
}

function truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.slice(0, len) + '...' : str;
}

async function loadPhoneNetwork(phone) {
    const el = document.getElementById('graph-loading');
    el.style.display = 'flex';
    el.innerHTML = `<div class="spinner"></div> Đang tải mạng lưới cho SĐT: ${phone}...`;

    const data = await fetchAPI(`/api/network/phone/${phone}`);
    el.style.display = 'none';
    if (!data || !data.nodes || !data.nodes.length) return;

    const elements = [];
    data.nodes.forEach(n => {
        elements.push({
            data: {
                id: n.id,
                label: truncate(n.label, 25),
                type: n.type,
                amount: n.amount,
            },
        });
    });
    data.edges.forEach(e => {
        elements.push({
            data: {
                source: e.source,
                target: e.target,
                type: e.type,
            },
        });
    });

    initCytoscape(document.getElementById('cy-container'), elements);
}

window.loadPhoneNetwork = loadPhoneNetwork;
