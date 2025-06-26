import { vi } from 'vitest';

// Mock HTTP client that simulates openapi-fetch behavior
export class MockClient {
  // Add missing properties to match openapi-fetch Client interface
  OPTIONS = vi.fn();
  HEAD = vi.fn();
  TRACE = vi.fn();
  use = vi.fn();
  eject = vi.fn();
  private mockResponses: Map<string, any> = new Map();

  constructor() {
    this.setupDefaultMocks();
  }

  // Set up default mock responses
  private setupDefaultMocks() {
    // Default evaluators list response
    this.mockResponses.set('GET /v1/evaluators/', {
      data: {
        results: [
          {
            id: 'eval-123',
            name: 'Test Evaluator',
            requires_expected_output: false,
            requires_contexts: false,
            requires_functions: false,
          },
        ],
        next: null,
        previous: null,
      },
      error: undefined,
    });

    // Default judges list response
    this.mockResponses.set('GET /v1/judges/', {
      data: {
        results: [
          {
            id: 'judge-123',
            name: 'Test Judge',
            intent: 'Test judge for evaluation',
          },
        ],
        next: null,
        previous: null,
      },
      error: undefined,
    });

    // Default execution response
    this.mockResponses.set('POST /v1/evaluators/eval-123/execute/', {
      data: {
        score: 0.85,
        justification: 'Test justification',
      },
      error: undefined,
    });
  }

  // Mock GET requests
  GET = vi.fn().mockImplementation((url: any, _options?: any) => {
    const key = `GET ${url}`;
    const response = this.mockResponses.get(key);

    if (response) {
      return Promise.resolve(response);
    }

    // Default success response for unknown endpoints
    return Promise.resolve({
      data: { results: [], next: null, previous: null },
      error: undefined,
    });
  });

  // Mock POST requests
  POST = vi.fn().mockImplementation((url: any, options?: any) => {
    const key = `POST ${url}`;
    const response = this.mockResponses.get(key);

    if (response) {
      return Promise.resolve(response);
    }

    // Default creation response
    return Promise.resolve({
      data: { id: 'created-123', ...(options?.body || {}) },
      error: undefined,
    });
  });

  // Mock PUT requests
  PUT = vi.fn().mockImplementation((url: any, options?: any) => {
    return Promise.resolve({
      data: { id: 'updated-123', ...(options?.body || {}) },
      error: undefined,
    });
  });

  // Mock PATCH requests
  PATCH = vi.fn().mockImplementation((url: any, options?: any) => {
    return Promise.resolve({
      data: { id: 'patched-123', ...(options?.body || {}) },
      error: undefined,
    });
  });

  // Mock DELETE requests
  DELETE = vi.fn().mockImplementation((_url: any, _options?: any) => {
    return Promise.resolve({
      data: undefined,
      error: undefined,
    });
  });

  // Helper to set custom mock responses
  setMockResponse(method: string, url: string, response: any) {
    this.mockResponses.set(`${method} ${url}`, response);
  }

  // Helper to simulate errors
  setMockError(method: string, url: string, error: any) {
    this.mockResponses.set(`${method} ${url}`, {
      data: undefined,
      error,
    });
  }

  // Reset all mocks
  reset() {
    this.mockResponses.clear();
    this.setupDefaultMocks();
    vi.clearAllMocks();
  }
}

// Create a singleton mock client for tests
export const mockClient = new MockClient();
