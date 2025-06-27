/**
 * @file Unit tests for rate limiting utilities
 */

import { describe, it, expect, beforeEach, afterEach, beforeAll, afterAll, vi } from 'vitest';
import {
  RateLimiter,
  createRateLimiter,
  RateLimitError,
  DEFAULT_RATE_LIMIT_CONFIG,
} from '../../../src/utils/rate-limit';

// Mock setImmediate for testing
const realSetImmediate = global.setImmediate;
beforeAll(() => {
  // @ts-expect-error - setImmediate is not defined in the global scope
  global.setImmediate = vi.fn((cb) => {
    cb();
    return {} as unknown as NodeJS.Immediate;
  });
});
afterAll(() => {
  global.setImmediate = realSetImmediate;
});
describe('RateLimiter', () => {
  let rateLimiter: RateLimiter;

  beforeEach(() => {
    rateLimiter = new RateLimiter();
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('constructor', () => {
    it('should use default configuration', () => {
      const limiter = new RateLimiter();
      const status = limiter.getStatus();

      expect(status.requestsRemaining).toBe(DEFAULT_RATE_LIMIT_CONFIG.maxRequests);
    });

    it('should merge custom configuration with defaults', () => {
      const customConfig = { maxRequests: 50, windowMs: 30000 };
      const limiter = new RateLimiter(customConfig);
      const status = limiter.getStatus();

      expect(status.requestsRemaining).toBe(50);
    });
  });

  describe('execute', () => {
    it('should execute function immediately when under limit', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      const result = await rateLimiter.execute(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should track request times', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      await rateLimiter.execute(mockFn);
      const status = rateLimiter.getStatus();

      expect(status.requestsRemaining).toBe(DEFAULT_RATE_LIMIT_CONFIG.maxRequests - 1);
    });

    it('should throw error when using "throw" strategy and limit exceeded', async () => {
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 60000,
        strategy: 'throw',
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // First request should succeed
      await limiter.execute(mockFn);

      // Second request should throw
      await expect(limiter.execute(mockFn)).rejects.toThrow(RateLimitError);
    });

    it('should drop requests when using "drop" strategy and limit exceeded', async () => {
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 60000,
        strategy: 'drop',
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // First request should succeed
      await limiter.execute(mockFn);

      // Second request should be dropped
      await expect(limiter.execute(mockFn)).rejects.toThrow(RateLimitError);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should queue requests when using "queue" strategy', async () => {
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 1000,
        strategy: 'queue',
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // Start multiple requests
      const promise1 = limiter.execute(mockFn);
      const promise2 = limiter.execute(mockFn);

      // First should execute immediately
      await promise1;
      expect(mockFn).toHaveBeenCalledTimes(1);

      // Advance time to allow second request
      vi.advanceTimersByTime(1001);
      await promise2;
      expect(mockFn).toHaveBeenCalledTimes(2);
    });

    it('should reject queued requests when queue is full', async () => {
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 60000,
        strategy: 'queue',
        maxQueueSize: 1,
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // Fill the quota
      await limiter.execute(mockFn);

      // Queue one request
      limiter.execute(mockFn);

      // Third request should be rejected due to full queue
      await expect(limiter.execute(mockFn)).rejects.toThrow(RateLimitError);
    });

    it('should call onRateLimitExceeded callback', async () => {
      const onRateLimitExceededMock = vi.fn();
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 60000,
        strategy: 'throw',
        onRateLimitExceeded: onRateLimitExceededMock,
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // First request succeeds
      await limiter.execute(mockFn);

      // Second request triggers callback
      try {
        await limiter.execute(mockFn);
      } catch {
        // Expected to throw
      }

      expect(onRateLimitExceededMock).toHaveBeenCalledTimes(1);
      expect(onRateLimitExceededMock).toHaveBeenCalledWith(expect.any(Number));
    });

    it('should clean old requests outside window', async () => {
      const limiter = new RateLimiter({
        maxRequests: 2,
        windowMs: 1000,
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // Make two requests
      await limiter.execute(mockFn);
      await limiter.execute(mockFn);

      let status = limiter.getStatus();
      expect(status.requestsRemaining).toBe(0);

      // Advance time past window
      vi.advanceTimersByTime(1001);

      // Should be able to make requests again
      await limiter.execute(mockFn);
      status = limiter.getStatus();
      expect(status.requestsRemaining).toBe(1);
    });
  });

  describe('getStatus', () => {
    it('should return current rate limit status', () => {
      const status = rateLimiter.getStatus();

      expect(status).toHaveProperty('requestsRemaining');
      expect(status).toHaveProperty('resetTime');
      expect(status).toHaveProperty('queueSize');
      expect(typeof status.requestsRemaining).toBe('number');
      expect(typeof status.resetTime).toBe('number');
      expect(typeof status.queueSize).toBe('number');
    });

    it('should update status after requests', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      const initialStatus = rateLimiter.getStatus();
      await rateLimiter.execute(mockFn);
      const afterStatus = rateLimiter.getStatus();

      expect(afterStatus.requestsRemaining).toBe(initialStatus.requestsRemaining - 1);
    });
  });

  describe('updateConfig', () => {
    it('should update configuration', () => {
      rateLimiter.updateConfig({ maxRequests: 50 });
      const status = rateLimiter.getStatus();

      expect(status.requestsRemaining).toBe(50);
    });
  });

  describe('reset', () => {
    it('should reset rate limiter state', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      // Make some requests
      await rateLimiter.execute(mockFn);
      await rateLimiter.execute(mockFn);

      const beforeReset = rateLimiter.getStatus();
      expect(beforeReset.requestsRemaining).toBeLessThan(DEFAULT_RATE_LIMIT_CONFIG.maxRequests);

      rateLimiter.reset();

      const afterReset = rateLimiter.getStatus();
      expect(afterReset.requestsRemaining).toBe(DEFAULT_RATE_LIMIT_CONFIG.maxRequests);
      expect(afterReset.queueSize).toBe(0);
    });

    it('should reject queued requests on reset', async () => {
      const limiter = new RateLimiter({
        maxRequests: 1,
        windowMs: 60000,
        strategy: 'queue',
      });

      const mockFn = vi.fn().mockResolvedValue('success');

      // Fill quota
      await limiter.execute(mockFn);

      // Queue a request
      const queuedPromise = limiter.execute(mockFn);

      // Reset should reject queued requests
      limiter.reset();

      await expect(queuedPromise).rejects.toThrow(RateLimitError);
    });
  });
});

describe('RateLimitError', () => {
  it('should create error with retry after time', () => {
    const error = new RateLimitError(5000, 'Custom message');

    expect(error.name).toBe('RateLimitError');
    expect(error.retryAfter).toBe(5000);
    expect(error.message).toContain('Custom message');
    expect(error.message).toContain('5000ms');
  });

  it('should use default message', () => {
    const error = new RateLimitError(1000);

    expect(error.message).toContain('Rate limit exceeded');
    expect(error.message).toContain('1000ms');
  });
});

describe('createRateLimiter', () => {
  it('should create RateLimiter instance', () => {
    const limiter = createRateLimiter({ maxRequests: 50 });

    expect(limiter).toBeInstanceOf(RateLimiter);
    expect(limiter.getStatus().requestsRemaining).toBe(50);
  });

  it('should create with default config when none provided', () => {
    const limiter = createRateLimiter();

    expect(limiter).toBeInstanceOf(RateLimiter);
    expect(limiter.getStatus().requestsRemaining).toBe(DEFAULT_RATE_LIMIT_CONFIG.maxRequests);
  });
});
