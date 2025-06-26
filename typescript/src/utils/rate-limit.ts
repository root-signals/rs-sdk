/**
 * Configuration for rate limiting
 */
export interface RateLimitConfig {
  /** Maximum number of requests per window */
  maxRequests: number;
  /** Time window in milliseconds */
  windowMs: number;
  /** Strategy for handling rate limit exceeded */
  strategy: 'throw' | 'queue' | 'drop';
  /** Maximum queue size when using 'queue' strategy */
  maxQueueSize?: number;
  /** Function called when rate limit is exceeded */
  onRateLimitExceeded?: (_remainingTime: number) => void;
}

/**
 * Default rate limit configuration
 */
export const DEFAULT_RATE_LIMIT_CONFIG: RateLimitConfig = {
  maxRequests: 100,
  windowMs: 60000, // 1 minute
  strategy: 'queue',
  maxQueueSize: 50,
};

/**
 * Request tracking for rate limiting
 */
interface RequestRecord {
  timestamp: number;
  resolve: () => void;
  reject: (_error: Error) => void;
}

/**
 * Rate limiter implementation using token bucket algorithm
 */
export class RateLimiter {
  private config: RateLimitConfig;
  private requestTimes: number[] = [];
  private queue: RequestRecord[] = [];
  private isProcessingQueue = false;

  constructor(config: Partial<RateLimitConfig> = {}) {
    this.config = { ...DEFAULT_RATE_LIMIT_CONFIG, ...config };
  }

  /**
   * Execute a function with rate limiting
   * @param fn - Function to execute
   * @returns Promise resolving to the function result
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    await this.waitForSlot();
    return fn();
  }

  /**
   * Wait for an available slot or handle according to strategy
   */
  private async waitForSlot(): Promise<void> {
    return new Promise((resolve, reject) => {
      const now = Date.now();

      // Clean old requests outside the window
      this.cleanOldRequests(now);

      // Check if we can proceed immediately
      if (this.requestTimes.length < this.config.maxRequests) {
        this.requestTimes.push(now);
        resolve();
        return;
      }

      // Rate limit exceeded - handle according to strategy
      const remainingTime = this.calculateRemainingTime(now);
      this.config.onRateLimitExceeded?.(remainingTime);

      switch (this.config.strategy) {
        case 'throw':
          reject(new RateLimitError(remainingTime));
          break;

        case 'queue':
          if (this.queue.length >= (this.config.maxQueueSize ?? 50)) {
            reject(new RateLimitError(remainingTime, 'Queue is full'));
          } else {
            this.queue.push({ timestamp: now, resolve, reject });
            this.processQueue();
          }
          break;

        case 'drop':
          reject(new RateLimitError(remainingTime, 'Request dropped due to rate limit'));
          break;
      }
    });
  }

  /**
   * Process queued requests
   */
  private processQueue(): void {
    if (this.isProcessingQueue || this.queue.length === 0) {
      return;
    }

    this.isProcessingQueue = true;

    const processNext = (): void => {
      const now = Date.now();
      this.cleanOldRequests(now);

      if (this.queue.length === 0) {
        this.isProcessingQueue = false;
        return;
      }

      if (this.requestTimes.length < this.config.maxRequests) {
        const request = this.queue.shift();
        if (request) {
          this.requestTimes.push(now);
          request.resolve();
        }

        // Process next request immediately if possible
        if (this.queue.length > 0) {
          if (typeof setImmediate !== 'undefined') {
            setImmediate(processNext);
          } else if (typeof setTimeout !== 'undefined') {
            setTimeout(processNext, 0);
          } else {
            // Fallback - process synchronously
            processNext();
          }
        } else {
          this.isProcessingQueue = false;
        }
      } else {
        // Wait until next slot becomes available
        const remainingTime = this.calculateRemainingTime(now);
        if (typeof setTimeout !== 'undefined') {
          setTimeout(processNext, remainingTime);
        } else {
          // Fallback for environments without setTimeout
          this.isProcessingQueue = false;
        }
      }
    };

    processNext();
  }

  /**
   * Remove old requests that are outside the time window
   */
  private cleanOldRequests(now: number): void {
    const cutoff = now - this.config.windowMs;
    this.requestTimes = this.requestTimes.filter((time) => time > cutoff);
  }

  /**
   * Calculate time remaining until next slot becomes available
   */
  private calculateRemainingTime(now: number): number {
    if (this.requestTimes.length === 0) {
      return 0;
    }
    const oldestRequest = Math.min(...this.requestTimes);
    return Math.max(0, oldestRequest + this.config.windowMs - now);
  }

  /**
   * Get current rate limit status
   */
  getStatus(): {
    requestsRemaining: number;
    resetTime: number;
    queueSize: number;
  } {
    const now = Date.now();
    this.cleanOldRequests(now);

    return {
      requestsRemaining: Math.max(0, this.config.maxRequests - this.requestTimes.length),
      resetTime:
        this.requestTimes.length > 0 ? Math.min(...this.requestTimes) + this.config.windowMs : now,
      queueSize: this.queue.length,
    };
  }

  /**
   * Update rate limit configuration
   */
  updateConfig(config: Partial<RateLimitConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Reset rate limiter state
   */
  reset(): void {
    this.requestTimes = [];
    this.queue.forEach((request) => request.reject(new RateLimitError(0, 'Rate limiter reset')));
    this.queue = [];
    this.isProcessingQueue = false;
  }
}

/**
 * Error thrown when rate limit is exceeded
 */
export class RateLimitError extends Error {
  constructor(
    public readonly retryAfter: number,
    message: string = 'Rate limit exceeded',
  ) {
    super(`${message}. Retry after ${retryAfter}ms`);
    this.name = 'RateLimitError';
    // Preserve prototype chain in down-compiled targets
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }
}

/**
 * Convenience function to create a rate limiter with default configuration
 */
export function createRateLimiter(config?: Partial<RateLimitConfig>): RateLimiter {
  return new RateLimiter(config);
}
