import { vi } from 'vitest';
import type { paths } from '../../src/generated/types';

type GetMethod = <TPath extends keyof paths>(
  url: TPath,
  options?: paths[TPath]['get'] extends { parameters?: infer TParams }
    ? { params?: TParams }
    : never,
) => Promise<{
  data: paths[TPath]['get'] extends {
    responses: { 200: { content: { 'application/json': infer TData } } };
  }
    ? TData
    : any;
  error: any;
}>;

type PostMethod = <TPath extends keyof paths>(
  url: TPath,
  options?: paths[TPath]['post'] extends {
    requestBody?: { content: { 'application/json': infer TBody } };
    parameters?: infer TParams;
  }
    ? { body?: TBody; params?: TParams }
    : never,
) => Promise<{
  data: paths[TPath]['post'] extends {
    responses:
      | { 200: { content: { 'application/json': infer TData } } }
      | { 201: { content: { 'application/json': infer TData } } };
  }
    ? TData
    : any;
  error: any;
}>;

type PutMethod = <TPath extends keyof paths>(
  url: TPath,
  options?: paths[TPath]['put'] extends {
    requestBody?: { content: { 'application/json': infer TBody } };
    parameters?: infer TParams;
  }
    ? { body?: TBody; params?: TParams }
    : never,
) => Promise<{
  data: paths[TPath]['put'] extends {
    responses: { 200: { content: { 'application/json': infer TData } } };
  }
    ? TData
    : any;
  error: any;
}>;

type PatchMethod = <TPath extends keyof paths>(
  url: TPath,
  options?: paths[TPath]['patch'] extends {
    requestBody?: { content: { 'application/json': infer TBody } };
    parameters?: infer TParams;
  }
    ? { body?: TBody; params?: TParams }
    : never,
) => Promise<{
  data: paths[TPath]['patch'] extends {
    responses: { 200: { content: { 'application/json': infer TData } } };
  }
    ? TData
    : any;
  error: any;
}>;

type DeleteMethod = <TPath extends keyof paths>(
  url: TPath,
  options?: paths[TPath]['delete'] extends { parameters?: infer TParams }
    ? { params?: TParams }
    : never,
) => Promise<{
  data: paths[TPath]['delete'] extends { responses: { 204: any } } ? undefined : any;
  error: any;
}>;

// Mock HTTP client that simulates openapi-fetch behavior
export class MockClient {
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
  GET = vi.fn<GetMethod>((url, options) => {
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
  POST = vi.fn<PostMethod>((url, options) => {
    const key = `POST ${url}`;
    const response = this.mockResponses.get(key);

    if (response) {
      return Promise.resolve(response);
    }

    // Default creation response
    return Promise.resolve({
      data: { id: 'created-123', ...options?.body },
      error: undefined,
    });
  });

  // Mock PUT requests
  PUT = vi.fn<PutMethod>((url, options) => {
    return Promise.resolve({
      data: { id: 'updated-123', ...options?.body },
      error: undefined,
    });
  });

  // Mock PATCH requests
  PATCH = vi.fn<PatchMethod>((url, options) => {
    return Promise.resolve({
      data: { id: 'patched-123', ...options?.body },
      error: undefined,
    });
  });

  // Mock DELETE requests
  DELETE = vi.fn<DeleteMethod>((url, options) => {
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
