import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import {
  Account,
  AccountCreate,
  AccountUpdate,
  Category,
  MonthlyAnalytics,
  NetWorthSummary,
  Transaction,
  TransactionCreate,
  TransferCreate,
  TransferResponse
} from '../models/expensify.models';

@Injectable({ providedIn: 'root' })
export class ExpensifyApiService {
  private http = inject(HttpClient);
  private baseUrl = (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';

  // Reactive State Signals
  summary = signal<NetWorthSummary | null>(null);
  accounts = signal<Account[]>([]);
  transactions = signal<Transaction[]>([]);
  categories = signal<Category[]>([]);
  analytics = signal<MonthlyAnalytics | null>(null);

  isLoading = signal<boolean>(false);

  /**
   * Sync all app data from backend in parallel
   */
  async refreshAll() {
    this.isLoading.set(true);
    try {
      const [sum, accs, txs, cats, ana] = await Promise.all([
        firstValueFrom(this.http.get<NetWorthSummary>(`${this.baseUrl}/summary`)),
        firstValueFrom(this.http.get<Account[]>(`${this.baseUrl}/accounts`)),
        firstValueFrom(this.http.get<Transaction[]>(`${this.baseUrl}/transactions`)),
        firstValueFrom(this.http.get<Category[]>(`${this.baseUrl}/categories`)),
        firstValueFrom(this.http.get<MonthlyAnalytics>(`${this.baseUrl}/analytics/monthly`))
      ]);

      this.summary.set(sum);
      this.accounts.set(accs);
      this.transactions.set(txs);
      this.categories.set(cats);
      this.analytics.set(ana);
    } catch (err) {
      console.error('Failed to sync Expensify API data:', err);
    } finally {
      this.isLoading.set(false);
    }
  }

  async createAccount(accountIn: AccountCreate): Promise<Account> {
    const acc = await firstValueFrom(this.http.post<Account>(`${this.baseUrl}/accounts`, accountIn));
    await this.refreshAll();
    return acc;
  }

  async updateAccount(id: string, updateIn: AccountUpdate): Promise<Account> {
    const acc = await firstValueFrom(this.http.patch<Account>(`${this.baseUrl}/accounts/${id}`, updateIn));
    await this.refreshAll();
    return acc;
  }

  async deleteAccount(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.baseUrl}/accounts/${id}`));
    await this.refreshAll();
  }

  async createTransaction(txIn: TransactionCreate): Promise<Transaction> {
    const tx = await firstValueFrom(this.http.post<Transaction>(`${this.baseUrl}/transactions`, txIn));
    await this.refreshAll();
    return tx;
  }

  async updateTransaction(id: string, updateIn: Partial<TransactionCreate>): Promise<Transaction> {
    const tx = await firstValueFrom(this.http.patch<Transaction>(`${this.baseUrl}/transactions/${id}`, updateIn));
    await this.refreshAll();
    return tx;
  }

  async deleteTransaction(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.baseUrl}/transactions/${id}`));
    await this.refreshAll();
  }

  async createTransfer(transferIn: TransferCreate): Promise<TransferResponse> {
    const res = await firstValueFrom(this.http.post<TransferResponse>(`${this.baseUrl}/transfers`, transferIn));
    await this.refreshAll();
    return res;
  }
}
