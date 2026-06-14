import { Alert, Box, Card, CardContent, Divider, Typography } from '@mui/material';
import { useAuthStore } from '../stores/auth';

export default function Settings() {
  const me = useAuthStore((s) => s.me);

  if (!me) {
    return <Alert severity="error">Unable to load settings.</Alert>;
  }

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, alignItems: 'start' }}>
      <Card>
        <CardContent>
          <Typography variant="overline" sx={{ fontWeight: 600, color: 'text.secondary', display: 'block', mb: 2 }}>
            My Account
          </Typography>
          <Box sx={{ display: 'grid', gap: 1 }}>
            <Typography variant="caption" sx={{ color: 'text.disabled' }}>Name</Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>{me.name || '—'}</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="caption" sx={{ color: 'text.disabled' }}>Email</Typography>
            <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>{me.email || '—'}</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="caption" sx={{ color: 'text.disabled' }}>Role</Typography>
            <Typography variant="body1" sx={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>{me.role || '—'}</Typography>
            <Divider sx={{ my: 1 }} />
            <Typography variant="caption" sx={{ color: 'text.disabled' }}>Subject</Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{me.subject || '—'}</Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
