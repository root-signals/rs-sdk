/**
 * Error Handling Patterns Example
 *
 * This example demonstrates comprehensive error handling strategies:
 * - Different types of API errors
 * - Retry strategies and backoff patterns
 * - Graceful degradation
 * - Circuit breaker patterns
 */

import { Scorable, ScorableError } from '../src/index.js';

interface RetryOptions {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

class RobustEvaluationClient {
  private client: Scorable;
  private circuitBreaker: {
    isOpen: boolean;
    failureCount: number;
    threshold: number;
    resetTimeout: number;
    lastFailureTime: number;
  };

  constructor(apiKey: string) {
    this.client = new Scorable({
      apiKey,
      timeout: 15000,
      retry: {
        maxRetries: 2, // Lower retries as we'll implement our own logic
        baseDelay: 500,
      },
    });

    // Circuit breaker state
    this.circuitBreaker = {
      isOpen: false,
      failureCount: 0,
      threshold: 5,
      resetTimeout: 60000, // 1 minute
      lastFailureTime: 0,
    };
  }

  /**
   * Execute evaluation with comprehensive error handling
   */
  async safeEvaluate(
    evaluatorName: string,
    payload: any,
    options: {
      fallbackResponse?: any;
      enableCircuitBreaker?: boolean;
      customRetry?: RetryOptions;
    } = {},
  ): Promise<{
    success: boolean;
    result?: any;
    error?: string;
    fallbackUsed?: boolean;
    retriesUsed?: number;
  }> {
    // Check circuit breaker
    if (options.enableCircuitBreaker && this.isCircuitBreakerOpen()) {
      console.log('⚡ Circuit breaker is open, skipping API call');
      return this.handleFallback(options.fallbackResponse);
    }

    const retryOptions: RetryOptions = options.customRetry || {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 10000,
      backoffMultiplier: 2,
    };

    let lastError: Error | null = null;
    let retriesUsed = 0;

    for (let attempt = 0; attempt <= retryOptions.maxRetries; attempt++) {
      try {
        console.log(
          `🔄 Attempt ${attempt + 1}/${retryOptions.maxRetries + 1} for ${evaluatorName}`,
        );

        const result = await this.client.evaluators.executeByName(evaluatorName, payload);

        // Success - reset circuit breaker
        this.circuitBreaker.failureCount = 0;

        console.log(`✅ Success on attempt ${attempt + 1}`);
        return {
          success: true,
          result,
          retriesUsed: attempt,
        };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        retriesUsed = attempt;

        console.log(`❌ Attempt ${attempt + 1} failed: ${lastError.message}`);

        // Handle different error types
        if (error instanceof ScorableError) {
          const shouldRetry = this.shouldRetryError(error);

          if (!shouldRetry) {
            console.log(`🚫 Non-retryable error (${error.status}), stopping retries`);
            break;
          }

          // Update circuit breaker on API errors
          if (options.enableCircuitBreaker) {
            this.updateCircuitBreaker(true);
          }
        }

        // Calculate delay for next attempt
        if (attempt < retryOptions.maxRetries) {
          const delay = Math.min(
            retryOptions.baseDelay * Math.pow(retryOptions.backoffMultiplier, attempt),
            retryOptions.maxDelay,
          );

          console.log(`⏳ Waiting ${delay}ms before retry...`);
          await this.delay(delay);
        }
      }
    }

    // All attempts failed
    console.log(`💥 All ${retryOptions.maxRetries + 1} attempts failed`);

    if (options.enableCircuitBreaker) {
      this.updateCircuitBreaker(true);
    }

    // Try fallback
    if (options.fallbackResponse) {
      console.log('🔄 Using fallback response');
      return this.handleFallback(options.fallbackResponse);
    }

    return {
      success: false,
      error: lastError?.message || 'Unknown error',
      retriesUsed,
    };
  }

  /**
   * Demonstrate different error scenarios
   */
  async demonstrateErrorScenarios(): Promise<void> {
    console.log('🧪 Demonstrating various error handling scenarios...\n');

    // 1. Invalid evaluator name
    console.log('1️⃣ Testing invalid evaluator name:');
    const invalidResult = await this.safeEvaluate(
      'NonExistentEvaluator',
      { request: 'test', response: 'test' },
      { fallbackResponse: { score: 0.5, justification: 'Fallback used due to error' } },
    );
    console.log(
      `   Result: ${invalidResult.success ? 'Success' : 'Failed'}, Fallback used: ${invalidResult.fallbackUsed}\n`,
    );

    // 2. Invalid payload
    console.log('2️⃣ Testing invalid payload:');
    const invalidPayloadResult = await this.safeEvaluate(
      'Helpfulness',
      { invalid_field: 'this will cause an error' },
      { fallbackResponse: { score: 0.0, justification: 'Invalid request format' } },
    );
    console.log(
      `   Result: ${invalidPayloadResult.success ? 'Success' : 'Failed'}, Fallback used: ${invalidPayloadResult.fallbackUsed}\n`,
    );

    // 3. Successful evaluation for comparison
    console.log('3️⃣ Testing valid evaluation:');
    const validResult = await this.safeEvaluate('Helpfulness', {
      request: 'How do I reset my password?',
      response: 'Click the forgot password link.',
    });
    console.log(
      `   Result: ${validResult.success ? 'Success' : 'Failed'}, Score: ${validResult.result?.score?.toFixed(3) || 'N/A'}\n`,
    );

    // 4. Circuit breaker demonstration
    console.log('4️⃣ Testing circuit breaker pattern:');
    console.log('   Simulating multiple failures to trigger circuit breaker...');

    for (let i = 0; i < 3; i++) {
      await this.safeEvaluate(
        'NonExistentEvaluator',
        { request: 'test', response: 'test' },
        {
          enableCircuitBreaker: true,
          fallbackResponse: { score: 0.3, justification: 'Circuit breaker fallback' },
        },
      );
      console.log(`   Failure ${i + 1}: Circuit breaker open = ${this.circuitBreaker.isOpen}`);
    }
    console.log();
  }

  /**
   * Batch evaluation with partial failure handling
   */
  async batchEvaluateWithErrorHandling(
    evaluatorName: string,
    payloads: Array<{ id: string; request: string; response: string }>,
  ): Promise<{
    successful: number;
    failed: number;
    results: Array<{ id: string; success: boolean; result?: any; error?: string }>;
  }> {
    console.log(`📦 Batch evaluating ${payloads.length} items with error handling...`);

    const results: Array<{
      id: string;
      success: boolean;
      result?: any;
      error?: string;
    }> = [];
    let successful = 0;
    let failed = 0;

    for (const payload of payloads) {
      console.log(`🔍 Processing item ${payload.id}...`);

      const result = await this.safeEvaluate(
        evaluatorName,
        { request: payload.request, response: payload.response },
        {
          fallbackResponse: {
            score: 0.5,
            justification: 'Default score due to evaluation failure',
          },
          enableCircuitBreaker: true,
        },
      );

      const resultEntry: {
        id: string;
        success: boolean;
        result?: any;
        error?: string;
      } = {
        id: payload.id,
        success: result.success,
        result: result.result,
      };

      if (result.error) {
        resultEntry.error = result.error;
      }

      results.push(resultEntry);

      if (result.success) {
        successful++;
        console.log(
          `   ✅ ${payload.id}: Success (Score: ${result.result?.score?.toFixed(3) || 'N/A'})`,
        );
      } else {
        failed++;
        console.log(`   ❌ ${payload.id}: Failed (${result.error})`);
      }
    }

    console.log(`📊 Batch completed: ${successful} successful, ${failed} failed\n`);

    return { successful, failed, results };
  }

  private shouldRetryError(error: ScorableError): boolean {
    // Don't retry client errors (4xx) except rate limiting
    if (error.status >= 400 && error.status < 500) {
      return error.status === 429; // Rate limit - retry with backoff
    }

    // Retry server errors (5xx)
    if (error.status >= 500) {
      return true;
    }

    // Don't retry other status codes
    return false;
  }

  private isCircuitBreakerOpen(): boolean {
    if (!this.circuitBreaker.isOpen) {
      return false;
    }

    // Check if enough time has passed to try resetting
    const timeSinceLastFailure = Date.now() - this.circuitBreaker.lastFailureTime;
    if (timeSinceLastFailure >= this.circuitBreaker.resetTimeout) {
      console.log('🔄 Circuit breaker reset timeout reached, attempting to close circuit');
      this.circuitBreaker.isOpen = false;
      this.circuitBreaker.failureCount = 0;
      return false;
    }

    return true;
  }

  private updateCircuitBreaker(failure: boolean): void {
    if (failure) {
      this.circuitBreaker.failureCount++;
      this.circuitBreaker.lastFailureTime = Date.now();

      if (this.circuitBreaker.failureCount >= this.circuitBreaker.threshold) {
        console.log(`⚡ Circuit breaker opened after ${this.circuitBreaker.failureCount} failures`);
        this.circuitBreaker.isOpen = true;
      }
    } else {
      this.circuitBreaker.failureCount = 0;
    }
  }

  private handleFallback(fallbackResponse?: any): {
    success: boolean;
    result?: any;
    fallbackUsed: boolean;
  } {
    if (fallbackResponse) {
      return {
        success: true,
        result: fallbackResponse,
        fallbackUsed: true,
      };
    }

    return {
      success: false,
      fallbackUsed: false,
    };
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Public method to check circuit breaker status
  getCircuitBreakerStatus() {
    return {
      isOpen: this.circuitBreaker.isOpen,
      failureCount: this.circuitBreaker.failureCount,
      threshold: this.circuitBreaker.threshold,
    };
  }
}

async function main() {
  try {
    console.log('🚀 Starting error handling patterns example...\n');

    const robustClient = new RobustEvaluationClient(process.env.SCORABLE_API_KEY!);

    // Demonstrate error scenarios
    await robustClient.demonstrateErrorScenarios();

    // Batch processing with error handling
    const batchPayloads = [
      { id: 'item1', request: 'Valid request', response: 'Valid response' },
      { id: 'item2', request: 'Another valid request', response: 'Another valid response' },
      { id: 'item3', request: 'Valid request', response: 'Valid response again' },
    ];

    await robustClient.batchEvaluateWithErrorHandling('Helpfulness', batchPayloads);

    // Show circuit breaker status
    const cbStatus = robustClient.getCircuitBreakerStatus();
    console.log(`⚡ Final Circuit Breaker Status:`);
    console.log(`   Open: ${cbStatus.isOpen}`);
    console.log(`   Failure Count: ${cbStatus.failureCount}/${cbStatus.threshold}`);

    console.log('\n✅ Error handling patterns example completed successfully!');
  } catch (error) {
    console.error('❌ Critical error in example:', error);
    process.exit(1);
  }
}

// Run the example
main().catch(console.error);
