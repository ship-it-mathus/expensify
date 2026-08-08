/* ==========================================================================
   Expensify Mobile Dashboard Single Page Application Logic
   ========================================================================== */

const API_BASE = '/api/v1';

// App State
const state = {
  activeTab: 'overview',
  summary: null,
  accounts: [],
  transactions: [],
  categories: [],
  analytics: null
};

// ==========================================
// API Client Layer
// ==========================================
async function apiFetch(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(errData.detail || `HTTP Error ${res.status}`);
    }
    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    showToast(`❌ ${err.message}`, 'error');
    throw err;
  }
}

// ==========================================
// Toast Notification Utility
// ==========================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==========================================
// Data Fetching & Sync
// ==========================================
async function refreshAppData() {
  try {
    const [summary, accounts, transactions, categories, analytics] = await Promise.all([
      apiFetch('/summary'),
      apiFetch('/accounts'),
      apiFetch('/transactions'),
      apiFetch('/categories'),
      apiFetch('/analytics/monthly')
    ]);

    state.summary = summary;
    state.accounts = accounts;
    state.transactions = transactions;
    state.categories = categories;
    state.analytics = analytics;

    renderAllViews();
    populateSelectDropdowns();
  } catch (e) {
    console.error('Failed to sync app data:', e);
  }
}

// ==========================================
// UI Render Functions
// ==========================================
function renderAllViews() {
  renderNetWorthHero();
  renderAccountsList();
  renderTransactionsList();
  renderAnalyticsView();
}

function formatCurrency(amount, currency = 'INR') {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 2
  }).format(amount);
}

function renderNetWorthHero() {
  if (!state.summary) return;
  const s = state.summary;
  
  const heroAmount = document.getElementById('hero-networth-amount');
  const totalBank = document.getElementById('hero-total-bank');
  const totalDues = document.getElementById('hero-total-dues');
  const counts = document.getElementById('hero-account-counts');

  if (heroAmount) heroAmount.textContent = formatCurrency(s.actual_liquid_money, s.currency);
  if (totalBank) totalBank.textContent = formatCurrency(s.total_bank_balance, s.currency);
  if (totalDues) totalDues.textContent = formatCurrency(s.total_credit_card_dues, s.currency);
  if (counts) counts.textContent = `${s.included_accounts_count} Included • ${s.excluded_accounts_count} Hidden`;
}

function renderAccountsList() {
  const container = document.getElementById('accounts-tab-container');
  if (!container) return;


  if (state.accounts.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 24px; color: var(--text-muted);">
        No accounts created yet. Click "+ New Account" above to get started!
      </div>
    `;
    return;
  }

  container.innerHTML = state.accounts.map(acc => {
    const isBank = acc.account_type === 'bank';
    const icon = isBank ? 'account_balance' : 'credit_card';
    const typeClass = isBank ? 'bank' : 'credit_card';
    const typeLabel = isBank ? 'Bank Account' : 'Credit Card Due';
    const exclusionBadge = !acc.include_in_net_worth 
      ? `<span class="exclusion-badge">Excluded</span>` 
      : '';

    return `
      <div class="account-card" id="account-${acc.id}">
        <div class="account-info">
          <div class="account-type-icon ${typeClass}">
            <span class="material-symbols-outlined">${icon}</span>
          </div>
          <div class="account-details">
            <div class="name">${acc.name} ${exclusionBadge}</div>
            <div class="meta">${typeLabel} • ${acc.currency}</div>
          </div>
        </div>
        <div class="account-balance-area">
          <div class="amount ${typeClass}">${formatCurrency(acc.balance, acc.currency)}</div>
          <button class="btn-icon" onclick="toggleAccountExclusion('${acc.id}', ${!acc.include_in_net_worth})" title="Toggle Net Worth Inclusion" style="margin-top: 4px; width: 28px; height: 28px; font-size: 0.75rem;">
            <span class="material-symbols-outlined" style="font-size: 1rem;">${acc.include_in_net_worth ? 'visibility' : 'visibility_off'}</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function renderTransactionsList() {
  const containers = [
    document.getElementById('transactions-list-container'),
    document.getElementById('full-transactions-container')
  ];

  containers.forEach(container => {
    if (!container) return;

    if (state.transactions.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 24px; color: var(--text-muted);">
          No transactions recorded yet.
        </div>
      `;
      return;
    }

    container.innerHTML = state.transactions.map(tx => {
      const isExpense = tx.transaction_type === 'expense';
      const icon = isExpense ? 'call_made' : 'call_received';
      const typeClass = isExpense ? 'expense' : 'income';
      const sign = isExpense ? '-' : '+';
      const txDate = new Date(tx.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });

      return `
        <div class="tx-card">
          <div class="tx-icon ${typeClass}">
            <span class="material-symbols-outlined">${icon}</span>
          </div>
          <div class="tx-details">
            <div class="desc">${tx.description || tx.category}</div>
            <div class="sub">${tx.category.toUpperCase()} • ${txDate}</div>
          </div>
          <div class="tx-amount ${typeClass}">${sign}${formatCurrency(tx.amount)}</div>
          <button class="btn-icon" onclick="deleteTx('${tx.id}')" title="Delete Transaction" style="margin-left: 8px; width: 28px; height: 28px;">
            <span class="material-symbols-outlined" style="font-size: 0.9rem; color: var(--danger);">delete</span>
          </button>
        </div>
      `;
    }).join('');
  });
}


function renderAnalyticsView() {
  if (!state.analytics) return;
  const a = state.analytics;

  const incomeEl = document.getElementById('analytics-total-income');
  const expenseEl = document.getElementById('analytics-total-expense');
  const savingsEl = document.getElementById('analytics-net-savings');
  const rateEl = document.getElementById('analytics-savings-rate');
  const catContainer = document.getElementById('analytics-categories-container');

  if (incomeEl) incomeEl.textContent = formatCurrency(a.total_income);
  if (expenseEl) expenseEl.textContent = formatCurrency(a.total_expense);
  if (savingsEl) savingsEl.textContent = formatCurrency(a.net_savings);
  if (rateEl) rateEl.textContent = `${a.savings_rate_percentage}% Savings Rate`;

  if (catContainer) {
    if (a.categories.length === 0) {
      catContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted);">No expense category data for this month.</div>`;
      return;
    }

    catContainer.innerHTML = a.categories.map(c => `
      <div class="category-progress-item">
        <div class="cat-header">
          <span>${c.category.toUpperCase()}</span>
          <span>${formatCurrency(c.total_amount)} (${c.percentage}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${c.percentage}%;"></div>
        </div>
      </div>
    `).join('');
  }
}

function populateSelectDropdowns() {
  const accountSelects = [
    document.getElementById('tx-account-select'),
    document.getElementById('transfer-from-select'),
    document.getElementById('transfer-to-select')
  ];

  accountSelects.forEach(select => {
    if (!select) return;
    select.innerHTML = state.accounts.map(acc => `
      <option value="${acc.id}">${acc.name} (${acc.account_type.toUpperCase()} - ${formatCurrency(acc.balance)})</option>
    `).join('');
  });

  const catSelect = document.getElementById('tx-category-select');
  if (catSelect) {
    catSelect.innerHTML = state.categories.map(cat => `
      <option value="${cat.name.toLowerCase()}">${cat.name} (${cat.category_type.toUpperCase()})</option>
    `).join('');
  }
}

// ==========================================
// Modal Handlers
// ==========================================
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('active');
}

async function toggleAccountExclusion(accountId, newStatus) {
  try {
    await apiFetch(`/accounts/${accountId}`, {
      method: 'PATCH',
      body: JSON.stringify({ include_in_net_worth: newStatus })
    });
    showToast('Updated account inclusion preference');
    await refreshAppData();
  } catch (e) {
    console.error(e);
  }
}

async function deleteTx(txId) {
  if (!confirm('Are you sure you want to delete this transaction?')) return;
  try {
    await apiFetch(`/transactions/${txId}`, { method: 'DELETE' });
    showToast('Transaction deleted');
    await refreshAppData();
  } catch (e) {
    console.error(e);
  }
}

// ==========================================
// Form Submission Listeners
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  refreshAppData();

  // Tab Navigation
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tabTarget = btn.getAttribute('data-tab');
      state.activeTab = tabTarget;

      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(`tab-${tabTarget}`);
      if (targetContent) targetContent.classList.add('active');
    });
  });

  // Account Form
  const accountForm = document.getElementById('form-create-account');
  if (accountForm) {
    accountForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('acc-name').value,
        account_type: document.getElementById('acc-type').value,
        balance: parseFloat(document.getElementById('acc-balance').value || 0),
        currency: 'INR'
      };
      await apiFetch('/accounts', { method: 'POST', body: JSON.stringify(payload) });
      showToast('🎉 Account created successfully!');
      closeModal('modal-account');
      accountForm.reset();
      await refreshAppData();
    });
  }

  // Transaction Form
  const txForm = document.getElementById('form-create-tx');
  if (txForm) {
    txForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        account_id: document.getElementById('tx-account-select').value,
        transaction_type: document.getElementById('tx-type-select').value,
        amount: parseFloat(document.getElementById('tx-amount').value),
        category: document.getElementById('tx-category-select').value,
        description: document.getElementById('tx-desc').value
      };
      await apiFetch('/transactions', { method: 'POST', body: JSON.stringify(payload) });
      showToast('✅ Transaction logged!');
      closeModal('modal-transaction');
      txForm.reset();
      await refreshAppData();
    });
  }

  // Transfer Form
  const transferForm = document.getElementById('form-create-transfer');
  if (transferForm) {
    transferForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        from_account_id: document.getElementById('transfer-from-select').value,
        to_account_id: document.getElementById('transfer-to-select').value,
        amount: parseFloat(document.getElementById('transfer-amount').value),
        description: document.getElementById('transfer-desc').value
      };
      const res = await apiFetch('/transfers', { method: 'POST', body: JSON.stringify(payload) });
      showToast(`🔄 [${res.transfer_tag}] Transfer complete!`);
      closeModal('modal-transfer');
      transferForm.reset();
      await refreshAppData();
    });
  }
});

// Register PWA Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed:', err));
  });
}
