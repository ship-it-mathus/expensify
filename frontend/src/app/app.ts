import { Component, OnInit, inject, signal, effect } from '@angular/core';
import { CommonModule, CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExpensifyApiService } from './services/api.service';
import { AccountType, InsightCard, Transaction, TransactionType } from './models/expensify.models';
import { AuthService } from './services/auth.service';
import { DonutChartComponent, BarChartComponent, InsightsCarouselComponent } from './components/charts.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, DonutChartComponent, BarChartComponent, InsightsCarouselComponent, CurrencyPipe],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  api = inject(ExpensifyApiService);
  auth = inject(AuthService);
  TxType = TransactionType;

  constructor() {
    // Reactively load data whenever auth state changes (handles page reload with existing session)
    effect(() => {
      if (this.auth.isAuthenticated()) {
        this.api.refreshAll();
      }
    });
  }

  // Active Tab Signal
  activeTab = signal<'overview' | 'settings' | 'history' | 'analytics' | 'new-transaction'>('overview');

  // Auth Form Models
  authEmail = '';
  authPassword = '';
  authMode: 'login' | 'signup' = 'login';
  isAuthSubmitting = signal<boolean>(false);

  // Modal Signals
  isTransferModalOpen = signal<boolean>(false);
  isAddAccountModalOpen = signal<boolean>(false);

  // Form Models
  newTxAccountId = '';
  newTxType: TransactionType = TransactionType.EXPENSE;
  newTxAmount: number | null = null;
  newTxCategory = '';
  newTxDescription = '';

  newAccName = '';
  newAccType: AccountType = AccountType.BANK;
  newAccBalance: number | null = null;
  newAccNotes = '';

  transferFromId = '';
  transferToId = '';
  transferAmount = 0;
  transferDescription = '';

  // ── Chart Data Getters ──────────────────────────────
  get donutLabels(): string[] {
    return (this.api.analytics()?.categories ?? []).map(c =>
      c.category.charAt(0).toUpperCase() + c.category.slice(1)
    );
  }

  get donutValues(): number[] {
    return (this.api.analytics()?.categories ?? []).map(c => c.total_amount);
  }

  get currentMonthLabel(): string {
    const now = new Date();
    return now.toLocaleString('default', { month: 'long', year: 'numeric' });
  }

  /**
   * Computes all rotating insight cards from in-memory transactions.
   * Most insights are computed client-side to avoid extra API calls.
   * % invested comes from the investment analytics signal.
   */
  get insightCards(): InsightCard[] {
    const txs = this.api.transactions();
    const inv = this.api.investmentAnalytics();
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    const thisYear = now.getFullYear();
    const thisMonth = now.getMonth() + 1;

    const sumExpense = (category: string, dateFilter: 'today' | 'month') => {
      return txs
        .filter(tx => {
          if (tx.transaction_type !== TransactionType.EXPENSE) return false;
          if (tx.category.toLowerCase() !== category.toLowerCase()) return false;
          const txDate = new Date(tx.date);
          if (dateFilter === 'today') return tx.date.slice(0, 10) === todayStr;
          return txDate.getFullYear() === thisYear && txDate.getMonth() + 1 === thisMonth;
        })
        .reduce((sum, tx) => sum + tx.amount, 0);
    };

    const card = (id: string, label: string, sublabel: string, icon: string, color: string, value: number, format: 'currency' | 'percent' = 'currency'): InsightCard =>
      ({ id, label, sublabel, icon, color, value: value > 0 ? value : null, format });

    const monthLabel = `in ${this.currentMonthLabel}`;

    return [
      card('food-today',    'Food today',          'Restaurants, groceries, etc.',    'restaurant',        '#f59e0b', sumExpense('food',          'today')),
      card('food-month',    'Food this month',     monthLabel,                         'restaurant',        '#f59e0b', sumExpense('food',          'month')),
      card('fuel-month',    'Fuel this month',     monthLabel,                         'local_gas_station', '#ef4444', sumExpense('fuel',          'month')),
      card('rent-month',    'Rent this month',     monthLabel,                         'home',              '#8b5cf6', sumExpense('rent',          'month')),
      card('shopping-month','Shopping this month', monthLabel,                         'shopping_bag',      '#ec4899', sumExpense('shopping',      'month')),
      card('entertain-month','Entertainment',      monthLabel,                         'movie',             '#06b6d4', sumExpense('entertainment', 'month')),
      card('health-month',  'Health this month',   monthLabel,                         'medical_services',  '#10b981', sumExpense('health',        'month')),
      card('transport-month','Transport this month',monthLabel,                        'directions_bus',    '#3b82f6', sumExpense('transport',     'month')),
      {
        id: 'pct-invested',
        label: '% income invested',
        sublabel: inv ? `₹${inv.total_invested.toLocaleString('en-IN')} of ₹${inv.total_income.toLocaleString('en-IN')} · ${monthLabel}` : monthLabel,
        icon: 'trending_up',
        color: '#6366f1',
        value: inv?.pct_income_invested ?? null,
        format: 'percent'
      }
    ].filter(c => c.value !== null) as InsightCard[];
  }

  ngOnInit() {}

  async handleAuthSubmit() {
    if (!this.authEmail || !this.authPassword) return;
    this.isAuthSubmitting.set(true);
    try {
      if (this.authMode === 'signup') {
        await this.auth.signUp(this.authEmail, this.authPassword);
        // If email confirmation is required, pendingConfirmation signal is now true.
        // Do NOT call refreshAll() — there is no session yet.
      } else {
        await this.auth.signIn(this.authEmail, this.authPassword);
        await this.api.refreshAll();
      }
    } catch (err) {
      console.error('Auth error:', err);
    } finally {
      this.isAuthSubmitting.set(false);
    }
  }

  async handleResendConfirmation() {
    try {
      await this.auth.resendConfirmationEmail();
    } catch (err) {
      console.error('Resend error:', err);
    }
  }

  handleCancelConfirmation() {
    this.auth.cancelConfirmation();
    this.authMode = 'login';
    this.authPassword = '';
  }

  async handleSignOut() {
    await this.auth.signOut();
    this.api.refreshAll();
  }

  setTxType(type: TransactionType) {
    this.newTxType = type;
    this.newTxCategory = '';
  }

  // Transaction Editing State
  editingTxId = signal<string | null>(null);

  editTransaction(tx: Transaction) {
    this.editingTxId.set(tx.id);
    this.newTxAccountId = tx.account_id;
    this.newTxType = tx.transaction_type;
    this.newTxAmount = tx.amount;
    this.newTxCategory = tx.category;
    this.newTxDescription = tx.description || '';
    this.setTab('new-transaction');
  }

  resetTxForm() {
    this.editingTxId.set(null);
    this.newTxAmount = null;
    this.newTxDescription = '';
    this.newTxCategory = '';
    this.newTxType = TransactionType.EXPENSE;
  }

  setTab(tab: 'overview' | 'settings' | 'history' | 'analytics' | 'new-transaction') {
    if (tab !== 'new-transaction') {
      this.resetTxForm();
    }
    this.activeTab.set(tab);
  }

  selectCategory(categoryName: string) {
    this.newTxCategory = categoryName;
  }

  selectAccount(accountId: string) {
    this.newTxAccountId = accountId;
  }

  async handleCreateTransaction() {
    if (!this.newTxAccountId || !this.newTxAmount || this.newTxAmount <= 0 || !this.newTxCategory) return;
    
    try {
      const payload = {
        account_id: this.newTxAccountId,
        transaction_type: this.newTxType,
        amount: Number(this.newTxAmount),
        category: this.newTxCategory,
        description: this.newTxDescription || undefined
      };

      if (this.editingTxId()) {
        await this.api.updateTransaction(this.editingTxId()!, payload);
        this.setTab('history');
      } else {
        await this.api.createTransaction(payload);
        this.setTab('overview');
      }
      this.resetTxForm();
    } catch (err) {
      console.error('Error logging transaction:', err);
    }
  }

  async handleDeleteTx(id: string) {
    if (confirm('Are you sure you want to delete this transaction? Account balances will adjust automatically.')) {
      await this.api.deleteTransaction(id);
    }
  }

  async handleToggleExclusion(id: string, current: boolean) {
    try {
      await this.api.updateAccount(id, { include_in_net_worth: !current });
    } catch (err) {
      console.error('Error toggling account exclusion:', err);
    }
  }

  openModal(modal: 'transfer' | 'account') {
    if (modal === 'transfer') this.isTransferModalOpen.set(true);
    if (modal === 'account') this.isAddAccountModalOpen.set(true);
  }

  closeModals() {
    this.isTransferModalOpen.set(false);
    this.isAddAccountModalOpen.set(false);
  }

  async handleCreateAccount() {
    if (!this.newAccName || this.newAccBalance === null) return;
    try {
      await this.api.createAccount({
        name: this.newAccName,
        account_type: this.newAccType,
        balance: Number(this.newAccBalance),
        notes: this.newAccNotes || undefined
      });
      this.newAccName = '';
      this.newAccType = AccountType.BANK;
      this.newAccBalance = null;
      this.newAccNotes = '';
      this.closeModals();
    } catch (err) {
      console.error('Error creating account:', err);
    }
  }

  async handleCreateTransfer() {
    if (!this.transferFromId || !this.transferToId || !this.transferAmount || this.transferAmount <= 0) return;
    try {
      await this.api.createTransfer({
        from_account_id: this.transferFromId,
        to_account_id: this.transferToId,
        amount: Number(this.transferAmount),
        description: this.transferDescription || undefined
      });
      this.closeModals();
    } catch (err) {
      console.error('Error executing transfer:', err);
    }
  }
}
