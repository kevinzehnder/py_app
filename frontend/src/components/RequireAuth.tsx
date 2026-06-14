import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

interface Props {
  children: React.ReactNode;
}

export default function RequireAuth({ children }: Props) {
  const token = useAuthStore((s) => s.bearerToken);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate('/login', { state: { from: location.pathname }, replace: true });
    }
  }, [token, navigate, location.pathname]);

  if (!token) {
    return null;
  }

  return <>{children}</>;
}
