import { createTheme } from '@mui/material/styles';

const sharedShape = { borderRadius: 10 };
const sharedTypography = { fontFamily: 'Inter, system-ui, -apple-system, sans-serif' };

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#818cf8', contrastText: '#1e1b4b' },
    secondary: { main: '#34d399', contrastText: '#064e3b' },
    error: { main: '#f87171' },
    background: { default: '#0f1117', paper: '#1a2030' },
    text: { primary: '#e2e8f0', secondary: '#94a3b8', disabled: '#475569' },
    divider: 'rgba(255,255,255,0.07)',
  },
  shape: sharedShape,
  typography: sharedTypography,
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255,255,255,0.07)',
          boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
          backgroundColor: '#1e2640',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: { paper: { backgroundColor: '#151b2b', borderRight: '1px solid rgba(255,255,255,0.07)' } },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#151b2b',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          boxShadow: 'none',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: { root: { borderBottomColor: 'rgba(255,255,255,0.07)' } },
    },
  },
});

// Catppuccin Latte — https://github.com/catppuccin/catppuccin
const latte = {
  base: '#eff1f5',
  mantle: '#e6e9ef',
  crust: '#dce0e8',
  surface0: '#ccd0da',
  surface1: '#bcc0cc',
  subtext0: '#6c6f85',
  text: '#4c4f69',
  lavender: '#7287fd',
  teal: '#179299',
  red: '#d20f39',
};

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: latte.lavender, contrastText: '#fff' },
    secondary: { main: latte.teal, contrastText: '#fff' },
    error: { main: latte.red },
    background: { default: latte.base, paper: latte.mantle },
    text: { primary: latte.text, secondary: latte.subtext0, disabled: latte.surface1 },
    divider: latte.surface0,
  },
  shape: sharedShape,
  typography: sharedTypography,
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: latte.mantle,
          border: `1px solid ${latte.surface0}`,
          boxShadow: `0 4px 16px rgba(76,79,105,0.08)`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: { paper: { backgroundColor: latte.crust, borderRight: `1px solid ${latte.surface0}` } },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: latte.crust,
          borderBottom: `1px solid ${latte.surface0}`,
          boxShadow: 'none',
          color: latte.text,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: { root: { borderBottomColor: latte.surface0 } },
    },
    MuiInputBase: {
      styleOverrides: { root: { color: latte.text } },
    },
  },
});
