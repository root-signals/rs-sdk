/**
 * @file Unit tests for retry utilities
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { RetryManager, withRetry, DEFAULT_RETRY_CONFIG } from '../../../src/utils/retry';

describe('RetryManager', () => {
  let retryManager: RetryManager;

  beforeEach(() => {
    retryManager = new RetryManager();
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should use default configuration', () => {
      const manager = new RetryManager();
      const config = manager.getConfig();

      expect(config.maxRetries).toBe(DEFAULT_RETRY_CONFIG.maxRetries);
      expect(config.baseDelay).toBe(DEFAULT_RETRY_CONFIG.baseDelay);
      expect(config.maxDelay).toBe(DEFAULT_RETRY_CONFIG.maxDelay);
      expect(config.backoffMultiplier).toBe(DEFAULT_RETRY_CONFIG.backoffMultiplier);
    });

    it('should merge custom configuration with defaults', () => {
      const customConfig = { maxRetries: 5, baseDelay: 2000 };
      const manager = new RetryManager(customConfig);
      const config = manager.getConfig();

      expect(config.maxRetries).toBe(5);
      expect(config.baseDelay).toBe(2000);
      expect(config.maxDelay).toBe(DEFAULT_RETRY_CONFIG.maxDelay);
      expect(config.backoffMultiplier).toBe(DEFAULT_RETRY_CONFIG.backoffMultiplier);
    });
  });

  describe('execute', () => {
    it('should succeed on first attempt', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');

      const result = await retryManager.execute(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should retry on retryable errors', async () => {
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce(new Error('Server Error'))
        .mockRejectedValueOnce(new Error('Server Error'))
        .mockResolvedValue('success');

      // Create manager with custom retry condition
      const manager = new RetryManager({
        retryCondition: (error) => error.message === 'Server Error',
      });

      const result = await manager.execute(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(3);
    });

    it('should not retry on non-retryable errors', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Client Error'));

      const manager = new RetryManager({
        retryCondition: (error) => error.message !== 'Client Error',
      });

      await expect(manager.execute(mockFn)).rejects.toThrow('Client Error');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should respect max retries limit', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Server Error'));

      const manager = new RetryManager({
        maxRetries: 2,
        retryCondition: () => true,
      });

      await expect(manager.execute(mockFn)).rejects.toThrow('Server Error');
      expect(mockFn).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it('should use exponential backoff', async () => {
      const delays: number[] = [];
      let callCount = 0;
      const mockFn = vi.fn(() => {
        callCount++;
        return Promise.reject(new Error('Server Error'));
      });

      const manager = new RetryManager({
        maxRetries: 3,
        baseDelay: 100,
        backoffMultiplier: 2,
        retryCondition: () => true,
        onRetry: (error, attempt, delay) => {
          delays.push(delay);
        },
      });

      await expect(manager.execute(mockFn)).rejects.toThrow('Server Error');

      expect(callCount).toBe(4); // Initial + 3 retries
      expect(delays).toEqual([100, 200, 400]); // Exponential backoff
    });

    it('should respect max delay limit', async () => {
      const delays: number[] = [];
      let callCount = 0;
      const mockFn = vi.fn(() => {
        callCount++;
        return Promise.reject(new Error('Server Error'));
      });

      const manager = new RetryManager({
        maxRetries: 3, // Reduced from 5 to speed up test
        baseDelay: 100, // Reduced from 1000 to speed up test
        maxDelay: 300, // Reduced from 3000 to speed up test
        backoffMultiplier: 2,
        retryCondition: () => true,
        onRetry: (error, attempt, delay) => {
          delays.push(delay);
        },
      });

      await expect(manager.execute(mockFn)).rejects.toThrow('Server Error');

      expect(callCount).toBe(4); // Initial + 3 retries
      expect(delays).toEqual([100, 200, 300]); // Capped at maxDelay
    });

    it('should call onRetry callback', async () => {
      const onRetryMock = vi.fn();
      const mockFn = vi
        .fn()
        .mockRejectedValueOnce(new Error('Server Error'))
        .mockResolvedValue('success');

      const manager = new RetryManager({
        retryCondition: () => true,
        onRetry: onRetryMock,
      });

      await manager.execute(mockFn);

      expect(onRetryMock).toHaveBeenCalledTimes(1);
      expect(onRetryMock).toHaveBeenCalledWith(expect.any(Error), 1, expect.any(Number));
    });

    it('should handle ScorableError with status codes', async () => {
      class MockScorableError extends Error {
        constructor(
          public status: number,
          message: string,
        ) {
          super(message);
          this.status = status;
          this.name = 'ScorableError';
        }
      }

      const mockFn = vi
        .fn()
        .mockRejectedValueOnce(new MockScorableError(500, 'Server Error'))
        .mockRejectedValueOnce(new MockScorableError(429, 'Rate Limited'))
        .mockResolvedValue('success');

      const result = await retryManager.execute(mockFn);

      expect(result).toBe('success');
      expect(mockFn).toHaveBeenCalledTimes(3);
    });

    it('should not retry on 4xx errors except 429', async () => {
      class MockScorableError extends Error {
        constructor(
          public status: number,
          message: string,
        ) {
          super(message);
          this.status = status;
          this.name = 'ScorableError';
        }
      }

      const mockFn = vi.fn().mockRejectedValue(new MockScorableError(404, 'Not Found'));

      await expect(retryManager.execute(mockFn)).rejects.toThrow('Not Found');
      expect(mockFn).toHaveBeenCalledTimes(1);
    });
  });

  describe('updateConfig', () => {
    it('should update configuration', () => {
      retryManager.updateConfig({ maxRetries: 5, baseDelay: 2000 });
      const config = retryManager.getConfig();

      expect(config.maxRetries).toBe(5);
      expect(config.baseDelay).toBe(2000);
    });
  });

  describe('getConfig', () => {
    it('should return copy of configuration', () => {
      const config1 = retryManager.getConfig();
      const config2 = retryManager.getConfig();

      expect(config1).toEqual(config2);
      expect(config1).not.toBe(config2); // Different objects
    });
  });
});

describe('withRetry', () => {
  it('should create RetryManager and execute function', async () => {
    const mockFn = vi.fn().mockResolvedValue('success');

    const result = await withRetry(mockFn, { maxRetries: 2 });

    expect(result).toBe('success');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('should use default configuration when none provided', async () => {
    const mockFn = vi.fn().mockResolvedValue('success');

    const result = await withRetry(mockFn);

    expect(result).toBe('success');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});
