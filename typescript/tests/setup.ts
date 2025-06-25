// Vitest setup file
import { vi } from 'vitest';

// Mock environment variables for testing
process.env.NODE_ENV = 'test';

// Global test helpers
declare global {
  namespace Vi {
    interface JestAssertion<T = any> {
      toBeValidUUID(): T;
      toMatchApiResponse(): T;
    }
  }
}

// Custom matchers
expect.extend({
  toBeValidUUID(received: string) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    const pass = uuidRegex.test(received);
    
    if (pass) {
      return {
        message: () => `expected ${received} not to be a valid UUID`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be a valid UUID`,
        pass: false,
      };
    }
  },
  
  toMatchApiResponse(received: any) {
    const hasRequiredFields = received && 
      typeof received === 'object' &&
      'id' in received;
    
    if (hasRequiredFields) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to match API response format`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to match API response format`,
        pass: false,
      };
    }
  }
});