import { Injectable, signal, computed } from '@angular/core';
import { createClient, SupabaseClient, User, Session } from '@supabase/supabase-js';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private supabaseUrl = 'https://herwthbqakaupwatlxbh.supabase.co';
  private supabaseKey = (typeof window !== 'undefined' && (window as any).__SUPABASE_KEY__)
    ? (window as any).__SUPABASE_KEY__
    : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhlcnd0aGJxYWthdXB3YXRseGJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3Nzk2MDksImV4cCI6MjEwMTM1NTYwOX0.U_U6c6MxwumhzZ75vui2rqPoIUNa2-d6vHmK38XS7s8';
  private supabase: SupabaseClient;

  // Reactive State Signals
  session = signal<Session | null>(null);
  user = signal<User | null>(null);
  isAuthenticated = computed(() => !!this.session());

  isLoading = signal<boolean>(true);
  authError = signal<string | null>(null);

  constructor() {
    this.supabase = createClient(this.supabaseUrl, this.supabaseKey);
    this.initAuth();
  }

  private async initAuth() {
    try {
      const { data } = await this.supabase.auth.getSession();
      this.session.set(data.session);
      this.user.set(data.session?.user ?? null);

      this.supabase.auth.onAuthStateChange((_event, session) => {
        this.session.set(session);
        this.user.set(session?.user ?? null);
      });
    } catch (err) {
      console.error('Failed to initialize Supabase auth:', err);
    } finally {
      this.isLoading.set(false);
    }
  }

  async signUp(email: string, pass: string) {
    this.authError.set(null);
    const { data, error } = await this.supabase.auth.signUp({
      email,
      password: pass
    });
    if (error) {
      this.authError.set(error.message);
      throw error;
    }
    return data;
  }

  async signIn(email: string, pass: string) {
    this.authError.set(null);
    const { data, error } = await this.supabase.auth.signInWithPassword({
      email,
      password: pass
    });
    if (error) {
      this.authError.set(error.message);
      throw error;
    }
    return data;
  }

  async signOut() {
    await this.supabase.auth.signOut();
    this.session.set(null);
    this.user.set(null);
  }

  getToken(): string | null {
    return this.session()?.access_token || null;
  }
}
