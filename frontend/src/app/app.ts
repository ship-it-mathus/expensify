import { Component, OnInit, inject, signal } from '@angular/core';
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

  ngOnInit() {
    this.api.refreshAll();
  }

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

  async handleGoogleLogin() {
    await this.auth.signInWithGoogle();
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
  }

  setTab(tab: 'overview' | 'settings' | 'history' | 'analytics' | 'new-transaction') {
    this.activeTab.set(tab);
    if (tab === 'new-transaction') {
      if (this.api.accounts().length > 0 && !this.newTxAccountId) {
        this.newTxAccountId = this.api.accounts()[0].id;
      }
    } else {
      this.resetTxForm();
    }
  }

  openModal(type: 'tx' | 'transfer') {
    if (type === 'tx') {
      this.resetTxForm();
      this.setTab('new-transaction');
    }
    if (type === 'transfer') this.isTransferModalOpen.set(true);
  }

  closeModals() {
    this.isTransferModalOpen.set(false);
  }

  selectCategory(categoryName: string) {
    this.newTxCategory = categoryName;
  }

  selectAccount(accountId: string) {
    this.newTxAccountId = accountId;
  }

  async handleToggleExclusion(accId: string, currentStatus: boolean) {
    await this.api.updateAccount(accId, { include_in_net_worth: !currentStatus });
  }

  async handleDeleteAccount(accId: string) {
    if (!confirm('Delete this account?')) return;
    await this.api.deleteAccount(accId);
  }

  async handleCreateTransaction() {
    if (!this.newTxAccountId || !this.newTxAmount || this.newTxAmount <= 0) return;
    
    const txPayload = {
      account_id: this.newTxAccountId,
      transaction_type: this.newTxType,
      amount: this.newTxAmount,
      category: this.newTxCategory || 'General',
      description: this.newTxDescription
    };

    if (this.editingTxId()) {
      await this.api.updateTransaction(this.editingTxId()!, txPayload);
    } else {
      await this.api.createTransaction(txPayload);
    }

    this.resetTxForm();
    this.setTab('overview');
  }

  async handleDeleteTx(txId: string) {
    if (!confirm('Delete transaction?')) return;
    await this.api.deleteTransaction(txId);
  }

  async handleCreateTransfer() {
    if (!this.transferFromId || !this.transferToId || this.transferAmount <= 0) return;
    await this.api.createTransfer({
      from_account_id: this.transferFromId,
      to_account_id: this.transferToId,
      amount: this.transferAmount,
      description: this.transferDescription
    });
    this.closeModals();
    this.transferAmount = 0;
    this.transferDescription = '';
  }
}
