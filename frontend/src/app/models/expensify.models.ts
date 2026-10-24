export enum AccountType {
  BANK = 'bank',
  CREDIT_CARD = 'credit_card',
  INVESTMENT = 'investment'
}

export type AssetClass = 'mutualFunds' | 'gold' | 'stocks' | 'bonds' | 'crypto' | 'other';

export const ASSET_CLASS_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  mutualFunds: { label: 'Mutual Funds', icon: 'pie_chart', color: '#10b981' },
  gold: { label: 'Gold', icon: 'monetization_on', color: '#f59e0b' },
  stocks: { label: 'Stocks', icon: 'trending_up', color: '#38bdf8' },
  bonds: { label: 'Bonds', icon: 'account_balance', color: '#8b5cf6' },
  crypto: { label: 'Crypto', icon: 'currency_bitcoin', color: '#ec4899' },
  other: { label: 'Other', icon: 'category', color: '#64748b' }
};

export enum TransactionType {
  INCOME = 'income',
  EXPENSE = 'expense'
}

export interface Account {
  id: string;
  name: string;
  account_type: AccountType;
  balance: number;
  include_in_net_worth: boolean;
  asset_class?: string;
  currency: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  name: string;
  account_type: AccountType;
  balance: number;
  asset_class?: string;
  currency?: string;
  notes?: string;
}

export interface AccountUpdate {
  name?: string;
  account_type?: AccountType;
  balance?: number;
  asset_class?: string;
  include_in_net_worth?: boolean;
  notes?: string;
}

export interface NetWorthSummary {
  total_bank_balance: number;
  total_credit_card_dues: number;
  total_investment_balance: number;
  actual_liquid_money: number;
  total_portfolio_wealth?: number;
  included_accounts_count: number;
  excluded_accounts_count: number;
  currency: string;
}

export interface Category {
  id: string;
  name: string;
  category_type: TransactionType;
  icon?: string;
  is_default: boolean;
  created_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  transaction_type: TransactionType;
  amount: number;
  category: string;
  description?: string;
  is_transfer?: boolean;
  transfer_destination_account_id?: string;
  date: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: string;
  transaction_type: TransactionType;
  amount: number;
  category: string;
  description?: string;
  is_transfer?: boolean;
  transfer_destination_account_id?: string;
}

export interface TransferCreate {
  from_account_id: string;
  to_account_id: string;
  amount: number;
  description?: string;
}

export interface TransferResponse {
  message: string;
  amount: number;
  transfer_tag: string;
  from_account_id: string;
  from_account_name: string;
  from_account_new_balance: number;
  to_account_id: string;
  to_account_name: string;
  to_account_new_balance: number;
  outflow_transaction_id: string;
  inflow_transaction_id: string;
  date: string;
}

export interface CategoryItem {
  category: string;
  total_amount: number;
  percentage: number;
}

export interface MonthlyAnalytics {
  scope?: string;
  year: number;
  month: number;
  day?: number;
  total_income: number;
  total_expense: number;
  net_savings: number;
  savings_rate_percentage: number;
  categories: CategoryItem[];
}

export interface AssetAllocationSlice {
  asset_class: string;
  amount: number;
  percentage: number;
}

export interface InvestmentAnalytics {
  year: number;
  month: number;
  total_invested: number;
  total_income: number;
  pct_income_invested: number;
  total_investment_balance: number;
  total_portfolio_wealth?: number;
  asset_allocation?: AssetAllocationSlice[];
}

/** A single computed insight card shown in the rotating insights strip. */
export interface InsightCard {
  id: string;
  label: string;
  sublabel: string;
  icon: string;
  color: string;         // CSS color string
  value: number | null;  // null = no data
  format: 'currency' | 'percent';
}
