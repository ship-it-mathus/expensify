export enum AccountType {
  BANK = 'bank',
  CREDIT_CARD = 'credit_card'
}

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
  currency: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}


export interface AccountCreate {
  name: string;
  account_type: AccountType;
  balance: number;
  currency?: string;
  notes?: string;
}

export interface AccountUpdate {
  name?: string;
  account_type?: AccountType;
  balance?: number;
  include_in_net_worth?: boolean;
  notes?: string;
}

export interface NetWorthSummary {
  total_bank_balance: number;
  total_credit_card_dues: number;
  actual_liquid_money: number;
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
  year: number;
  month: number;
  total_income: number;
  total_expense: number;
  net_savings: number;
  savings_rate_percentage: number;
  categories: CategoryItem[];
}
