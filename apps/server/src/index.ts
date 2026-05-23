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
  const rawValue = parseFloat(req.query.value as string);
  const rawMin = parseFloat(req.query.min as string);
  const rawMax = parseFloat(req.query.max as string);
  const value = isNaN(rawValue) ? 0 : rawValue;
  const min = isNaN(rawMin) ? 0 : rawMin;
  const max = isNaN(rawMax) ? 100 : rawMax;
  res.json({ value, min, max, result: clamp(value, min, max) });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
