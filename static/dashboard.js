async function loadLeads() {
  const res = await fetch('/api/leads');
  const data = await res.json();
  const leads = data.leads || [];

  const tbody = document.getElementById('leads-body');
  tbody.innerHTML = '';

  let qualified = 0;
  let review = 0;
  let newCount = 0;

  if (leads.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty">No leads yet. <a href="/">Submit one</a>.</td></tr>';
  }

  for (const lead of leads) {
    if (lead.qualified) qualified++;
    if (lead.status === 'needs_review') review++;
    if (lead.status === 'new') newCount++;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${lead.id}</td>
      <td>${escapeHtml(lead.name)}</td>
      <td>${escapeHtml(lead.agency || '-')}</td>
      <td>${escapeHtml(lead.role || '-')}</td>
      <td><span class="badge ${lead.status}">${lead.status.replace('_', ' ')}</span></td>
      <td>${lead.qualified ? '✅' : '—'}</td>
      <td class="summary-cell" title="${escapeHtml(lead.notes || '')}">${escapeHtml(lead.notes || '-')}</td>
      <td>${formatDate(lead.created_at)}</td>
      <td><button class="button" onclick="viewLead(${lead.id})">View</button></td>
    `;
    tbody.appendChild(tr);
  }

  document.getElementById('stat-total').textContent = leads.length;
  document.getElementById('stat-qualified').textContent = qualified;
  document.getElementById('stat-review').textContent = review;
  document.getElementById('stat-new').textContent = newCount;
}

async function viewLead(leadId) {
  const res = await fetch(`/api/leads/${leadId}`);
  const data = await res.json();
  const lead = data.lead;
  const calls = data.calls || [];

  const detail = document.getElementById('lead-detail');
  const content = document.getElementById('detail-content');
  detail.classList.remove('hidden');

  let callsHtml = '';
  if (calls.length > 0) {
    callsHtml = `<h3>AI Calls</h3>` + calls.map(call => `
      <div class="card" style="margin-bottom:12px;">
        <p><strong>Status:</strong> ${call.status} · <strong>Outcome:</strong> ${call.outcome || '-'}</p>
        <p><strong>Summary:</strong> ${call.summary || '-'}</p>
        <pre>${escapeHtml(call.transcript || 'No transcript')}</pre>
      </div>
    `).join('');
  } else {
    callsHtml = `<p>No AI calls yet. <a href="/">Run one now</a>.</p>`;
  }

  content.innerHTML = `
    <dl class="detail-grid">
      <div class="detail-item"><dt>Name</dt><dd>${escapeHtml(lead.name)}</dd></div>
      <div class="detail-item"><dt>Phone</dt><dd>${escapeHtml(lead.phone)}</dd></div>
      <div class="detail-item"><dt>Email</dt><dd>${escapeHtml(lead.email || '-')}</dd></div>
      <div class="detail-item"><dt>Agency</dt><dd>${escapeHtml(lead.agency || '-')}</dd></div>
      <div class="detail-item"><dt>Role</dt><dd>${escapeHtml(lead.role || '-')}</dd></div>
      <div class="detail-item"><dt>Status</dt><dd><span class="badge ${lead.status}">${lead.status.replace('_', ' ')}</span></dd></div>
      <div class="detail-item"><dt>Qualified</dt><dd>${lead.qualified ? '✅ Yes' : '—'}</dd></div>
      <div class="detail-item"><dt>Created</dt><dd>${formatDate(lead.created_at)}</dd></div>
    </dl>
    <p><strong>Interest / Challenge:</strong> ${escapeHtml(lead.interest || '-')}</p>
    <p><strong>AI Summary:</strong> ${escapeHtml(lead.notes || '-')}</p>
    <button class="button" onclick="runCall(${lead.id})">Run AI Qualification Call</button>
    ${callsHtml}
  `;

  detail.scrollIntoView({ behavior: 'smooth' });
}

async function runCall(leadId) {
  const btn = document.querySelector('#detail-content button');
  if (btn) btn.disabled = true;
  await fetch(`/api/leads/${leadId}/call`, { method: 'POST' });
  await viewLead(leadId);
  await loadLeads();
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(&/g, '&amp;')
    .replace(</g, '&lt;')
    .replace(>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatDate(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

loadLeads();