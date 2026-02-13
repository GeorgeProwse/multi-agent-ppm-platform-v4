import { Navigate, Outlet } from 'react-router-dom';
import { useAppStore } from '@/store';

export function RequireAuth() {
  const { session } = useAppStore();

  if (session.loading) {
    return <div aria-live="polite">Loading session…</div>;
  }

  if (!session.authenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export function RequireTenantContext() {
  const { tenantContext } = useAppStore();

  if (!tenantContext.tenantId) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export function RequireAdminRole() {
  const { session } = useAppStore();
  const isAdmin = session.user?.roles?.includes('admin') || session.user?.permissions?.includes('admin:access');

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
