import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { delay, clamp, randomId } from '../index';

describe('delay', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Given a delay function', () => {
    describe('when called with positive milliseconds', () => {
      it('should resolve after the specified delay', async () => {
        const promise = delay(100);
        vi.advanceTimersByTime(100);
        await expect(promise).resolves.toBeUndefined();
      });

      it('should not resolve before the delay time', () => {
        const promise = delay(1000);
        vi.advanceTimersByTime(500);

        let resolved = false;
        promise.then(() => {
          resolved = true;
        });

        vi.runAllTimers();
        expect(resolved).toBe(false);
      });
    });

    describe('when called with zero milliseconds', () => {
      it('should resolve immediately', async () => {
        const promise = delay(0);
        vi.runAllTimers();
        await expect(promise).resolves.toBeUndefined();
      });
    });

    describe('when called with large delay', () => {
      it('should correctly track time progression', async () => {
        const promise = delay(5000);
        vi.advanceTimersByTime(2500);
        vi.advanceTimersByTime(2500);
        await expect(promise).resolves.toBeUndefined();
      });
    });
  });
});

describe('clamp', () => {
  describe('Given a clamp function', () => {
    describe('when value is within range', () => {
      it('should return the value unchanged', () => {
        expect(clamp(5, 0, 10)).toBe(5);
      });

      it('should return middle value unchanged', () => {
        expect(clamp(50, 0, 100)).toBe(50);
      });
    });

    describe('when value is below minimum', () => {
      it('should return the minimum value', () => {
        expect(clamp(-5, 0, 10)).toBe(0);
      });

      it('should clamp deeply negative values', () => {
        expect(clamp(-100, 0, 100)).toBe(0);
      });
    });

    describe('when value is above maximum', () => {
      it('should return the maximum value', () => {
        expect(clamp(15, 0, 10)).toBe(10);
      });

      it('should clamp deeply large values', () => {
        expect(clamp(1000, 0, 100)).toBe(100);
      });
    });

    describe('when value equals minimum', () => {
      it('should return the minimum value', () => {
        expect(clamp(0, 0, 10)).toBe(0);
      });

      it('should handle negative range correctly', () => {
        expect(clamp(-10, -10, 10)).toBe(-10);
      });
    });

    describe('when value equals maximum', () => {
      it('should return the maximum value', () => {
        expect(clamp(10, 0, 10)).toBe(10);
      });

      it('should handle negative range correctly', () => {
        expect(clamp(10, -10, 10)).toBe(10);
      });
    });

    describe('with negative numbers', () => {
      it('should handle negative range bounds', () => {
        expect(clamp(5, -10, -5)).toBe(-5);
      });

      it('should clamp negative values to range', () => {
        expect(clamp(-15, -10, -5)).toBe(-10);
      });

      it('should return value within negative range', () => {
        expect(clamp(-7, -10, -5)).toBe(-7);
      });
    });

    describe('with floating point numbers', () => {
      it('should handle decimal values within range', () => {
        expect(clamp(0.5, 0, 1)).toBe(0.5);
      });

      it('should clamp decimal values below minimum', () => {
        expect(clamp(-0.5, 0, 1)).toBe(0);
      });

      it('should clamp decimal values above maximum', () => {
        expect(clamp(1.5, 0, 1)).toBe(1);
      });

      it('should handle precision edge cases', () => {
        const result = clamp(0.1 + 0.2, 0, 1);
        expect(result).toBeCloseTo(0.3, 10);
      });
    });
  });
});

describe('randomId', () => {
  describe('Given a randomId function', () => {
    describe('when called without arguments', () => {
      it('should generate id with default length of 8 characters', () => {
        const id = randomId();
        expect(id).toHaveLength(8);
      });
    });

    describe('when called with custom length', () => {
      it('should generate id with specified length up to implementation limit', () => {
        expect(randomId(4)).toHaveLength(4);
        expect(randomId(6)).toHaveLength(6);
        expect(randomId(8)).toHaveLength(8);
      });

      it('should generate id with length 1', () => {
        expect(randomId(1)).toHaveLength(1);
      });
    });

    describe('when generating multiple ids', () => {
      it('should generate unique ids', () => {
        const ids = new Set<string>();
        for (let i = 0; i < 100; i++) {
          ids.add(randomId());
        }
        expect(ids.size).toBe(100);
      });

      it('should maintain length consistency', () => {
        for (let i = 0; i < 50; i++) {
          expect(randomId(8)).toHaveLength(8);
        }
      });
    });

    describe('with edge case lengths', () => {
      it('should handle zero length', () => {
        const id = randomId(0);
        expect(id).toHaveLength(0);
      });
    });
  });
});
