"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { CheckCircle2, KeyRound, Landmark, LoaderCircle, Lock, ShieldAlert } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  async function handleUpdatePassword(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setErrorMsg("Password must be at least 6 characters long.");
      return;
    }

    setLoading(true);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;

      setSuccessMsg("Your password has been successfully updated! Redirecting to assistant…");
      setTimeout(() => {
        router.push("/");
        router.refresh();
      }, 2000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update password. Your recovery link may have expired.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <header className="auth-header">
        <Link href="/" className="auth-brand" aria-label="Sahayaka Home">
          <span className="brand-mark">
            <Landmark size={20} strokeWidth={1.8} />
          </span>
          <span className="brand-word">
            sahayaka<span>.</span>
          </span>
        </Link>
      </header>

      <main className="auth-main">
        <div className="auth-card">
          <div className="auth-card-head">
            <div className="auth-icon-badge">
              <KeyRound size={20} />
            </div>
            <h1>Set New Password</h1>
            <p>Please enter your new password to regain access to your Sahayaka account.</p>
          </div>

          {errorMsg && (
            <div className="auth-alert error" role="alert">
              <ShieldAlert size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="auth-alert success" role="status">
              <CheckCircle2 size={16} />
              <span>{successMsg}</span>
            </div>
          )}

          <form className="auth-form" onSubmit={handleUpdatePassword}>
            <div className="auth-field">
              <label htmlFor="new-password">New Password</label>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  id="new-password"
                  type="password"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="confirm-new-password">Confirm New Password</label>
              <div className="auth-input-wrap">
                <Lock size={16} className="auth-input-icon" />
                <input
                  id="confirm-new-password"
                  type="password"
                  required
                  minLength={6}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your new password"
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? (
                <span className="auth-btn-loading">
                  <LoaderCircle size={16} className="spin" />
                  <span>Updating…</span>
                </span>
              ) : (
                "Update Password"
              )}
            </button>
          </form>

          <div className="auth-card-footer">
            <p>
              <Link href="/login" className="auth-link-btn">
                ← Back to Sign In
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

