import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputBase,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import InventoryIcon from '@mui/icons-material/Inventory2';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { listItems, createItem, deleteItem, type Item, type ItemCreate } from '../lib/items';

export default function Items() {
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState<ItemCreate>({ name: '', description: '', active: true });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    void listItems()
      .then(({ items, total }) => {
        setItems(items);
        setTotal(total);
      })
      .catch(() => setError('Unable to load items.'));
  }, []);

  const filtered = useMemo(
    () => items.filter((i) =>
      i.name.toLowerCase().includes(search.toLowerCase()) ||
      i.description.toLowerCase().includes(search.toLowerCase()),
    ),
    [search, items],
  );

  const activeCount = items.filter((i) => i.active).length;

  async function handleCreate() {
    if (!form.name.trim()) return;
    setCreating(true);
    try {
      const created = await createItem(form);
      setItems((curr) => [created, ...curr]);
      setTotal((t) => t + 1);
      setCreateOpen(false);
      setForm({ name: '', description: '', active: true });
    } catch {
      setError('Unable to create item.');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    const previous = items;
    setItems((curr) => curr.filter((i) => i.id !== id));
    setTotal((t) => t - 1);
    try {
      await deleteItem(id);
    } catch {
      setItems(previous);
      setTotal((t) => t + 1);
      setError('Unable to delete item.');
    }
  }

  return (
    <>
      {error !== '' ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 2, mb: 3 }}>
        {[
          { label: 'Total Items', value: `${total}`, icon: <InventoryIcon />, sub: 'All items' },
          { label: 'Active', value: `${activeCount}`, icon: <CheckCircleIcon />, sub: 'Currently active' },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'text.secondary' }}>
                  {stat.label}
                </Typography>
                <Box sx={{ color: 'primary.main', opacity: 0.8, lineHeight: 0 }}>{stat.icon}</Box>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, letterSpacing: '-0.02em', mb: 0.25 }}>{stat.value}</Typography>
              <Typography variant="caption" sx={{ color: 'text.disabled' }}>{stat.sub}</Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Card>
        <CardContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto auto', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="overline" sx={{ fontWeight: 600, color: 'text.secondary' }}>Items</Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'auto 1fr', alignItems: 'center', gap: 0.5, bgcolor: 'rgba(255,255,255,0.04)', border: '1px solid', borderColor: 'divider', borderRadius: 2, px: 1, py: 0.5 }}>
              <SearchIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
              <InputBase
                placeholder="Search items…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                sx={{ fontSize: '0.875rem', width: 160 }}
              />
            </Box>
            <Button
              size="small"
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateOpen(true)}
              sx={{ textTransform: 'none' }}
            >
              New item
            </Button>
          </Box>

          <Table size="small">
            <TableHead>
              <TableRow>
                {['Name', 'Description', 'Status', ''].map((h, i) => (
                  <TableCell key={i} sx={{ fontWeight: 600, fontSize: '0.72rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'text.secondary' }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((item) => (
                <TableRow key={item.id} sx={{ '&:last-child td': { border: 0 } }}>
                  <TableCell sx={{ fontWeight: 500 }}>{item.name}</TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>{item.description || '—'}</TableCell>
                  <TableCell>
                    <Chip
                      label={item.active ? 'Active' : 'Inactive'}
                      size="small"
                      sx={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        bgcolor: item.active ? 'rgba(52,211,153,0.15)' : 'rgba(148,163,184,0.1)',
                        color: item.active ? '#34d399' : '#94a3b8',
                        border: 'none',
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => void handleDelete(item.id)} color="error">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ color: 'text.disabled', py: 4 }}>
                    No items found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Item</DialogTitle>
        <DialogContent sx={{ display: 'grid', gap: 2, pt: 1 }}>
          <TextField
            label="Name"
            fullWidth
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            autoFocus
            required
          />
          <TextField
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => void handleCreate()} disabled={creating || !form.name.trim()}>
            {creating ? 'Creating…' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
