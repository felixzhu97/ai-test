import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import express from 'express';
import { clamp, randomId } from '@ai-test/utils';

const app = express();
app.use(express.json());

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

describe('API Endpoints', () => {
  beforeAll(() => {
    process.env.PORT = '3000';
  });

  afterAll(() => {
    delete process.env.PORT;
  });

  describe('GET /api/health', () => {
    it('should return 200 status code', async () => {
      const response = await request(app).get('/api/health');
      expect(response.status).toBe(200);
    });

    it('should return status ok', async () => {
      const response = await request(app).get('/api/health');
      expect(response.body.status).toBe('ok');
    });

    it('should include timestamp field', async () => {
      const response = await request(app).get('/api/health');
      expect(response.body).toHaveProperty('timestamp');
    });

    it('should return valid ISO format timestamp', async () => {
      const response = await request(app).get('/api/health');
      const { timestamp } = response.body;
      const date = new Date(timestamp);
      expect(date.toISOString()).toBe(timestamp);
      expect(date.getTime()).not.toBeNaN();
    });
  });

  describe('GET /api/id', () => {
    it('should return 200 status code', async () => {
      const response = await request(app).get('/api/id');
      expect(response.status).toBe(200);
    });

    it('should include id field', async () => {
      const response = await request(app).get('/api/id');
      expect(response.body).toHaveProperty('id');
    });

    it('should return id with meaningful length (8+ chars)', async () => {
      const response = await request(app).get('/api/id');
      const id = response.body.id;
      expect(typeof id).toBe('string');
      expect(id.length).toBeGreaterThanOrEqual(8);
    });

    it('should return different IDs on multiple calls', async () => {
      const response1 = await request(app).get('/api/id');
      const response2 = await request(app).get('/api/id');
      const response3 = await request(app).get('/api/id');
      const ids = [response1.body.id, response2.body.id, response3.body.id];
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });
  });

  describe('GET /api/clamp', () => {
    it('should return 200 status code', async () => {
      const response = await request(app).get('/api/clamp');
      expect(response.status).toBe(200);
    });

    it('should return value within range when value is within min and max', async () => {
      const response = await request(app).get('/api/clamp?value=5&min=0&max=10');
      expect(response.body.result).toBe(5);
      expect(response.body.value).toBe(5);
      expect(response.body.min).toBe(0);
      expect(response.body.max).toBe(10);
    });

    it('should return min when value is less than min', async () => {
      const response = await request(app).get('/api/clamp?value=-5&min=0&max=10');
      expect(response.body.result).toBe(0);
      expect(response.body.min).toBe(0);
    });

    it('should return max when value is greater than max', async () => {
      const response = await request(app).get('/api/clamp?value=15&min=0&max=10');
      expect(response.body.result).toBe(10);
      expect(response.body.max).toBe(10);
    });

    it('should handle floating point numbers correctly', async () => {
      const response = await request(app).get('/api/clamp?value=5.5&min=0&max=10');
      expect(response.body.result).toBe(5.5);
      expect(response.body.value).toBe(5.5);
    });

    it('should use default min=0 and max=100 when only value is provided', async () => {
      const response = await request(app).get('/api/clamp?value=50');
      expect(response.body.result).toBe(50);
      expect(response.body.min).toBe(0);
      expect(response.body.max).toBe(100);
    });

    it('should handle negative range correctly', async () => {
      const response = await request(app).get('/api/clamp?value=5&min=-10&max=-5');
      expect(response.body.result).toBe(-5);
      expect(response.body.min).toBe(-10);
      expect(response.body.max).toBe(-5);
    });

    it('should use default values when parameters are missing', async () => {
      const response = await request(app).get('/api/clamp');
      expect(response.body.value).toBe(0);
      expect(response.body.min).toBe(0);
      expect(response.body.max).toBe(100);
      expect(response.body.result).toBe(0);
    });

    it('should handle invalid value parameter', async () => {
      const response = await request(app).get('/api/clamp?value=abc');
      expect(response.body.result).toBe(0);
    });
  });
});
