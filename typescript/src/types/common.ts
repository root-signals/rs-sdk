import { RetryConfig } from '../utils/retry.js';
import { RateLimitConfig } from '../utils/rate-limit.js';
import { components } from '../generated/types.js';

type Functions = components['schemas']['EvaluatorExecutionFunctionsRequest'][];

export interface ClientConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  retry?: Partial<RetryConfig>;
  rateLimit?: Partial<RateLimitConfig>;
}

export interface PaginatedResponse<T> {
  results: T[];
  next?: string | undefined;
  previous?: string | undefined;
}

export interface ListParams {
  cursor?: string;
  page_size?: number;
  search?: string;
  ordering?: string;
}

export interface ErrorDetails {
  type?: string;
  title?: string;
  detail?: string;
  instance?: string;
  [key: string]: unknown;
}

export interface ApiError {
  status: number;
  code: string;
  details: ErrorDetails;
}

export class RootSignalsError extends Error {
  public readonly type?: string | undefined;
  public readonly title?: string | undefined;
  public readonly detail?: string | undefined;
  public readonly instance?: string | undefined;

  constructor(
    public readonly status: number,
    public readonly code: string,
    public readonly details?: ErrorDetails,
    message?: string,
  ) {
    super(message ?? details?.detail ?? details?.title ?? `API Error ${status}: ${code}`);
    this.name = 'RootSignalsError';
    this.type = details?.type;
    this.title = details?.title;
    this.detail = details?.detail;
    this.instance = details?.instance;
  }

  static isAuthenticationError(error: RootSignalsError): boolean {
    return (
      error.status === 401 ||
      error.code === 'authentication_failed' ||
      error.code === 'not_authenticated'
    );
  }

  static isQuotaError(error: RootSignalsError): boolean {
    return error.status === 429 || error.code === 'throttled';
  }

  static isValidationError(error: RootSignalsError): boolean {
    return error.status === 400 || error.code === 'invalid' || error.code === 'parse_error';
  }

  static isNotFoundError(error: RootSignalsError): boolean {
    return error.status === 404 || error.code === 'not_found';
  }

  static isServerError(error: RootSignalsError): boolean {
    return error.status >= 500;
  }
}

export interface ExecutionPayload {
  request?: string;
  response?: string;
  contexts?: string[];
  functions?: Functions;
  expected_output?: string;
  reference?: string;
  variables?: Record<string, string>;
  [key: string]: unknown;
}
