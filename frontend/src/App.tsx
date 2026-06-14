import { useEffect } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { darkTheme, lightTheme } from './theme';
import { useUIStore } from './stores/ui';
import { useAuthStore } from './stores/auth';
import Layout from './components/Layout';
import RequireAuth from './components/RequireAuth';
import LoginPage from './components/LoginPage';
import Dashboard from './pages/Dashboard';
import Items from './pages/Items';
import Settings from './pages/Settings';

export default function App() {
  const darkMode = useUIStore((s) => s.darkMode);
  const toggleDarkMode = useUIStore((s) => s.toggleDarkMode);
  const refresh = useAuthStore((s) => s.refresh);
  const bearerToken = useAuthStore((s) => s.bearerToken);

  // Hydrate auth on mount if token exists
  useEffect(() => {
    if (bearerToken) {
      void refresh();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <Layout dark={darkMode} onToggleTheme={toggleDarkMode}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/items" element={<RequireAuth><Items /></RequireAuth>} />
                  <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
