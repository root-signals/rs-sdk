import { ApiError } from '../types/common.js';

/**
 * Configuration for retry logic with exponential backoff
 */
export interface RetryConfig {
  /** Maximum number of retry attempts */
  maxRetries: number;
  /** Base delay in milliseconds before first retry */
  baseDelay: number;
  /** Maximum delay in milliseconds between retries */
  maxDelay: number;
  /** Multiplier for exponential backoff */
  backoffMultiplier: number;
  /** Function to determine if an error should trigger a retry */
  retryCondition?: (_error: Error, _attemptNumber: number) => boolean;
  /** Function called before each retry attempt */
  onRetry?: (_error: Error, _attemptNumber: number, _delay: number) => void;
}

/**
 * Default retry configuration
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffMultiplier: 2,
  retryCondition: (error: Error) => {
    // Retry on network errors, timeouts, and 5xx server errors
    if (error.name === 'NetworkError' || error.name === 'TimeoutError') {
      return true;
    }
    // Check for RootSignalsError with retryable status codes
    if ('status' in error) {
      const status = (error as unknown as ApiError).status;
      return status >= 500 || status === 429; // Server errors or rate limiting
    }
    return false;
  },
};

/**
 * Utility class for implementing retry logic with exponential backoff
 */
export class RetryManager {
  private config: RetryConfig;

  constructor(config: Partial<RetryConfig> = {}) {
    this.config = { ...DEFAULT_RETRY_CONFIG, ...config };
  }

  /**
   * Execute a function with retry logic
   * @param fn - Function to execute with retry
   * @returns Promise resolving to the function result
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry on last attempt
        if (attempt === this.config.maxRetries) {
          break;
        }

        // Check if this error should trigger a retry
        if (!this.config.retryCondition?.(lastError, attempt + 1)) {
          break;
        }

        // Calculate delay with exponential backoff
        const delay = this.calculateDelay(attempt);

        // Call retry callback if provided
        this.config.onRetry?.(lastError, attempt + 1, delay);

        // Wait before retrying
        await this.sleep(delay);
      }
    }

    throw lastError ?? new Error('Retry attempts exhausted');
  }

  /**
   * Calculate delay for the given attempt number using exponential backoff
   */
  private calculateDelay(attemptNumber: number): number {
    const delay = this.config.baseDelay * Math.pow(this.config.backoffMultiplier, attemptNumber);
    return Math.min(delay, this.config.maxDelay);
  }

  /**
   * Sleep for the specified number of milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      if (typeof setTimeout !== 'undefined') {
        setTimeout(resolve, ms);
      } else {
        // Fallback for environments without setTimeout
        resolve();
      }
    });
  }

  /**
   * Update retry configuration
   */
  updateConfig(config: Partial<RetryConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current retry configuration
   */
  getConfig(): RetryConfig {
    return { ...this.config };
  }
}

/**
 * Convenience function to retry a function with default configuration
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  config?: Partial<RetryConfig>,
): Promise<T> {
  const retryManager = new RetryManager(config);
  return retryManager.execute(fn);
}
