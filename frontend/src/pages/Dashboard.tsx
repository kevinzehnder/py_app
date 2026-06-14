import { Box, Card, CardContent, Typography, Table, TableHead, TableBody, TableRow, TableCell } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import TimelineIcon from '@mui/icons-material/Timeline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const stats = [
  { label: 'Total Users', value: '12,543', icon: <PeopleIcon />, change: '+12.4%', positive: true, sub: 'vs last month' },
  { label: 'Revenue', value: '$48,295', icon: <AttachMoneyIcon />, change: '+8.1%', positive: true, sub: 'vs last month' },
  { label: 'Active Sessions', value: '1,429', icon: <TimelineIcon />, change: '+3.4%', positive: true, sub: 'right now' },
  { label: 'Error Rate', value: '0.24%', icon: <ErrorOutlineIcon />, change: '-0.05%', positive: true, sub: 'vs last week' },
];

const activity = [
  { user: 'alice@example.com', action: 'Created account', time: '2m ago', status: 'success' },
  { user: 'bob@example.com', action: 'Updated profile', time: '14m ago', status: 'success' },
  { user: 'carol@example.com', action: 'Password reset', time: '1h ago', status: 'warning' },
  { user: 'dave@example.com', action: 'Login failed', time: '2h ago', status: 'error' },
  { user: 'eve@example.com', action: 'Exported data', time: '3h ago', status: 'success' },
  { user: 'frank@example.com', action: 'Deleted account', time: '5h ago', status: 'error' },
];

const statusColors: Record<string, string> = {
  success: '#34d399',
  warning: '#fbbf24',
  error: '#f87171',
};

export default function Dashboard() {
  return (
    <>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 2, mb: 3 }}>
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'text.secondary' }}>
                  {stat.label}
                </Typography>
                <Box sx={{ color: 'primary.main', opacity: 0.8, lineHeight: 0 }}>{stat.icon}</Box>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em', mb: 0.5 }}>
                {stat.value}
              </Typography>
              <Box sx={{ display: 'grid', gridAutoFlow: 'column', justifyContent: 'start', alignItems: 'center', gap: 0.5 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: stat.positive ? '#34d399' : '#f87171' }}>
                  {stat.change}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.disabled' }}>{stat.sub}</Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Card>
        <CardContent>
          <Typography variant="overline" sx={{ fontWeight: 600, color: 'text.secondary', display: 'block', mb: 2 }}>
            Recent Activity
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                {['User', 'Action', 'Status', 'Time'].map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 600, fontSize: '0.72rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'text.secondary' }}>
                    {h}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {activity.map((row, i) => (
                <TableRow key={i} sx={{ '&:last-child td': { border: 0 } }}>
                  <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'text.secondary' }}>{row.user}</TableCell>
                  <TableCell sx={{ fontSize: '0.875rem' }}>{row.action}</TableCell>
                  <TableCell>
                    <Typography variant="caption" sx={{ fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: statusColors[row.status] }}>
                      {row.status}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ color: 'text.disabled', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>{row.time}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  );
}
