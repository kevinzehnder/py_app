import { useLocation, Link, useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Divider,
  Button,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory2';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useUIStore } from '../stores/ui';
import { useAuthStore } from '../stores/auth';

const DRAWER_WIDTH = 240;

interface Props {
  dark: boolean;
  onToggleTheme: () => void;
  children: React.ReactNode;
}

const navItems = [
  { label: 'Dashboard', icon: <DashboardIcon fontSize="small" />, href: '/' },
  { label: 'Items', icon: <InventoryIcon fontSize="small" />, href: '/items', auth: true },
  { label: 'Settings', icon: <SettingsIcon fontSize="small" />, href: '/settings', auth: true },
];

export default function Layout({ dark, onToggleTheme, children }: Props) {
  const location = useLocation();
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const token = useAuthStore((s) => s.bearerToken);
  const me = useAuthStore((s) => s.me);
  const clearToken = useAuthStore((s) => s.clearBearerToken);
  const navigate = useNavigate();

  function signOut() {
    clearToken();
    navigate('/login');
  }

  const visibleItems = navItems.filter((item) => {
    if (item.auth && !token) return false;
    return true;
  });

  const activeLabel =
    visibleItems.find((item) =>
      item.href === '/'
        ? location.pathname === '/'
        : location.pathname.startsWith(item.href),
    )?.label ?? 'Dashboard';

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: sidebarOpen ? `${DRAWER_WIDTH}px 1fr` : '0px 1fr',
        gridTemplateRows: '1fr',
        height: '100vh',
        overflow: 'hidden',
        transition: 'grid-template-columns 0.2s',
      }}
    >
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1, width: '100%' }}>
        <Toolbar
          variant="dense"
          sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', alignItems: 'center', gap: 0.5 }}
        >
          <IconButton edge="start" onClick={toggleSidebar} color="inherit">
            <MenuIcon />
          </IconButton>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {activeLabel}
          </Typography>
          <Box sx={{ display: 'grid', gridAutoFlow: 'column', alignItems: 'center', gap: 0.5 }}>
            {token ? (
              <>
                <Typography variant="caption" sx={{ color: 'inherit', opacity: 0.7, mr: 0.5 }}>
                  {me?.email ?? 'Signed in'}
                </Typography>
                <IconButton color="inherit">
                  <AccountCircleIcon fontSize="small" />
                </IconButton>
              </>
            ) : (
              <Button
                color="inherit"
                size="small"
                startIcon={<LoginIcon fontSize="small" />}
                onClick={() => navigate('/login')}
                sx={{ textTransform: 'none' }}
              >
                Sign in
              </Button>
            )}
            <IconButton onClick={onToggleTheme} color="inherit">
              {dark ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          overflow: 'hidden',
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            position: 'relative',
            height: '100vh',
            overflow: 'hidden',
            boxSizing: 'border-box',
          },
        }}
      >
        <Box
          sx={{
            display: 'grid',
            gridTemplateRows: 'auto auto 1fr auto',
            height: '100%',
            overflow: 'hidden',
          }}
        >
          <Toolbar variant="dense" />

          {token && me ? (
            <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    bgcolor: 'primary.main',
                    boxShadow: (t) => `0 0 8px ${t.palette.primary.main}`,
                  }}
                />
                <Typography variant="body2" sx={{ fontWeight: 700, letterSpacing: '0.05em' }}>
                  {me.name || me.email}
                </Typography>
              </Box>
            </Box>
          ) : null}

          <List sx={{ py: 1, overflowY: 'auto' }}>
            {visibleItems.map((item) => (
              <ListItem key={item.label} disablePadding sx={{ px: 1, mb: 0.25 }}>
                <ListItemButton
                  component={Link}
                  to={item.href}
                  selected={activeLabel === item.label}
                  sx={{ borderRadius: 2, py: 0.75 }}
                >
                  <ListItemIcon sx={{ minWidth: 36, color: 'inherit' }}>{item.icon}</ListItemIcon>
                  <ListItemText
                    primary={item.label}
                    primaryTypographyProps={{ fontSize: '0.875rem' }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          {token ? (
            <Box>
              <Divider />
              <List sx={{ py: 1 }}>
                <ListItem disablePadding sx={{ px: 1 }}>
                  <ListItemButton sx={{ borderRadius: 2, py: 0.75 }} onClick={signOut}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Sign out" primaryTypographyProps={{ fontSize: '0.875rem' }} />
                  </ListItemButton>
                </ListItem>
              </List>
            </Box>
          ) : null}
        </Box>
      </Drawer>

      <Box
        component="main"
        sx={{
          display: 'grid',
          gridTemplateRows: 'auto 1fr',
          overflow: 'hidden',
          minWidth: 0,
        }}
      >
        <Toolbar variant="dense" />
        <Box sx={{ overflowY: 'auto', p: { xs: 2, md: 3 } }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
