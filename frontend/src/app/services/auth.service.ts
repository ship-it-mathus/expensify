import { Injectable, signal, computed } from '@angular/core';
import { createClient, SupabaseClient, User, Session } from '@supabase/supabase-js';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private supabaseUrl = 'https://herwthbqakaupwatlxbh.supabase.co';
  private supabaseKey = (typeof window !== 'undefined' && (window as any).__SUPABASE_KEY__)
    ? (window as any).__SUPABASE_KEY__
    : 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhlcnd0aGJxYWthdXB3YXRseGJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3Nzk2MDksImV4cCI6MjEwMTM1NTYwOX0.U_U6c6MxwumhzZ75vui2rqPoIUNa2-d6vHmK38XS7s8';
  private supabase: SupabaseClient;

  // Core auth signals
  session = signal<Session | null>(null);
  user = signal<User | null>(null);
  isAuthenticated = computed(() => !!this.session());
  isLoading = signal<boolean>(true);
  authError = signal<string | null>(null);

  // Email confirmation flow
  pendingConfirmation = signal<boolean>(false);
  pendingEmail = signal<string>('');
  resendSuccess = signal<boolean>(false);
  isResending = signal<boolean>(false);

  constructor() {
    this.supabase = createClient(this.supabaseUrl, this.supabaseKey);
    this.initAuth();
  }

  private async initAuth() {
    try {
      // Step 1: Exchange tokens from the confirmation link URL before anything else
      await this.handleAuthCallback();

      // Step 2: Restore existing session
      const { data } = await this.supabase.auth.getSession();
      this.session.set(data.session);
      this.user.set(data.session?.user ?? null);

      // Step 3: React to future auth state changes (login, logout, token refresh)
      this.supabase.auth.onAuthStateChange((_event, session) => {
        this.session.set(session);
        this.user.set(session?.user ?? null);
        // If we get a real session, the user confirmed their email — clear pending state
        if (session) {
          this.pendingConfirmation.set(false);
          this.pendingEmail.set('');
        }
      });
    } catch (err) {
      console.error('Failed to initialize Supabase auth:', err);
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Handles Supabase email confirmation redirects.
   *
   * When a user clicks the confirmation link, Supabase redirects them back to the app with
   * tokens in the URL. Two possible formats:
   *   - PKCE flow:     ?code=abc123
   *   - Implicit flow: #access_token=...&refresh_token=...&type=signup
   *
   * We exchange/apply those tokens here so the user is automatically signed in.
   */
  private async handleAuthCallback() {
    if (typeof window === 'undefined') return;

    const hash = window.location.hash;
    const search = window.location.search;

    // PKCE flow: ?code=...
    const code = new URLSearchParams(search).get('code');
    if (code) {
      try {
        await this.supabase.auth.exchangeCodeForSession(code);
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch (err) {
        console.error('Failed to exchange auth code:', err);
      }
      return;
    }

    // Implicit flow: #access_token=...&refresh_token=...
    if (hash && hash.includes('access_token')) {
      try {
        const params = new URLSearchParams(hash.substring(1));
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        if (accessToken && refreshToken) {
          await this.supabase.auth.setSession({ access_token: accessToken, refresh_token: refreshToken });
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      } catch (err) {
        console.error('Failed to restore session from URL hash:', err);
      }
    }
  }

  async signUp(email: string, pass: string) {
    this.authError.set(null);
    this.resendSuccess.set(false);
    const { data, error } = await this.supabase.auth.signUp({ email, password: pass });
    if (error) {
      this.authError.set(error.message);
      throw error;
    }
    // Supabase returns a user but NO session when email confirmation is required.
    // Show the "check your inbox" screen.
    if (!data.session) {
      this.pendingConfirmation.set(true);
      this.pendingEmail.set(email);
    }
    return data;
  }

  async signIn(email: string, pass: string) {
    this.authError.set(null);
    const { data, error } = await this.supabase.auth.signInWithPassword({ email, password: pass });
    if (error) {
      this.authError.set(error.message);
      throw error;
    }
    return data;
  }

  async resendConfirmationEmail() {
    const email = this.pendingEmail();
    if (!email) return;
    this.isResending.set(true);
    this.authError.set(null);
    this.resendSuccess.set(false);
    try {
      const { error } = await this.supabase.auth.resend({ type: 'signup', email });
      if (error) {
        this.authError.set(error.message);
        throw error;
      }
      this.resendSuccess.set(true);
      // Auto-clear success banner after 4s
      setTimeout(() => this.resendSuccess.set(false), 4000);
    } finally {
      this.isResending.set(false);
    }
  }

  cancelConfirmation() {
    this.pendingConfirmation.set(false);
    this.pendingEmail.set('');
    this.authError.set(null);
    this.resendSuccess.set(false);
  }

  async signOut() {
    await this.supabase.auth.signOut();
    this.session.set(null);
    this.user.set(null);
    this.pendingConfirmation.set(false);
    this.pendingEmail.set('');
  }

  getToken(): string | null {
    return this.session()?.access_token || null;
  }
}
