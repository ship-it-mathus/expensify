import { Component, OnInit, inject, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExpensifyApiService } from './services/api.service';
import { AccountType, Transaction, TransactionType } from './models/expensify.models';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

  // Form Models
  newTxAccountId = '';
  newTxType: TransactionType = TransactionType.EXPENSE;
  newTxAmount: number | null = null;
  newTxCategory = '';
  newTxDescription = '';

  transferFromId = '';
  transferToId = '';
  transferAmount = 0;
  transferDescription = '';

  ngOnInit() {}

  async handleAuthSubmit() {
    if (!this.authEmail || !this.authPassword) return;
    this.isAuthSubmitting.set(true);
    try {
      if (this.authMode === 'signup') {
        await this.auth.signUp(this.authEmail, this.authPassword);
      } else {
        await this.auth.signIn(this.authEmail, this.authPassword);
      }
      await this.api.refreshAll();
    } catch (err) {
      console.error('Auth error:', err);
    } finally {
      this.isAuthSubmitting.set(false);
    }
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

  openModal(modal: 'transfer') {
    if (modal === 'transfer') this.isTransferModalOpen.set(true);
  }

  closeModals() {
    this.isTransferModalOpen.set(false);
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
