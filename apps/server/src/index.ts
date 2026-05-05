import express from 'express';
import { clamp, randomId } from '@ai-test/utils';

const app = express();
const PORT = process.env.PORT ?? 3000;

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/api/id', (_req, res) => {
  res.json({ id: randomId(16) });
});

app.get('/api/clamp', (req, res) => {
  const value = parseFloat(req.query.value as string) ?? 0;
  const min = parseFloat(req.query.min as string) ?? 0;
  const max = parseFloat(req.query.max as string) ?? 100;
  res.json({ value, min, max, result: clamp(value, min, max) });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
