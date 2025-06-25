import type { paths, components } from '../generated/types.js';
import { PaginatedResponse, ListParams, RootSignalsError, ExecutionPayload } from '../types/common.js';

type Client = ReturnType<typeof import('openapi-fetch').default<paths>>;

export type EvaluatorListItem = components['schemas']['EvaluatorListOutput'];
export type EvaluatorDetail = components['schemas']['Evaluator'];
export type ExecutionResult = components['schemas']['EvaluatorExecutionResult'];

export interface EvaluatorListParams extends ListParams {
  is_preset?: boolean;
  is_public?: boolean;
}

export class EvaluatorsResource {
  constructor(
    private _client: Client
  ) {}

  /**
   * List all accessible evaluators
   */
  async list(params: EvaluatorListParams = {}): Promise<PaginatedResponse<EvaluatorListItem>> {
    const { data, error } = await this._client.GET('/v1/evaluators/', {
      params: { query: params }
    });

    if (error) {
      throw new RootSignalsError(
        (error as any)?.status ?? 500,
        'LIST_EVALUATORS_FAILED',
        error,
        'Failed to list evaluators'
      );
    }

    return {
      results: data.results,
      next: data.next ?? undefined,
      previous: data.previous ?? undefined,
      count: data.results.length
    };
  }

  /**
   * Get a specific evaluator by ID
   */
  async get(id: string): Promise<EvaluatorDetail> {
    const { data, error } = await this._client.GET('/v1/evaluators/{id}/', {
      params: { path: { id } }
    });

    if (error) {
      throw new RootSignalsError(
        (error as any)?.status ?? 500,
        'GET_EVALUATOR_FAILED',
        error,
        `Failed to get evaluator ${id}`
      );
    }

    return data;
  }

  /**
   * Execute an evaluator by ID
   */
  async execute(id: string, payload: ExecutionPayload): Promise<ExecutionResult> {
    const { data, error } = await this._client.POST('/v1/evaluators/execute/{id}/', {
      params: { path: { id } },
      body: payload
    });

    if (error) {
      throw new RootSignalsError(
        (error as any)?.status ?? 500,
        'EXECUTE_EVALUATOR_FAILED',
        error,
        `Failed to execute evaluator ${id}`
      );
    }

    return data;
  }

  /**
   * Execute an evaluator by name (convenience method)
   */
  async executeByName(name: string, payload: ExecutionPayload): Promise<ExecutionResult> {
    const { data, error } = await this._client.POST('/v1/evaluators/execute/by-name/', {
      params: { query: { name } },
      body: payload
    });

    if (error) {
      throw new RootSignalsError(
        (error as any)?.status ?? 500,
        'EXECUTE_EVALUATOR_BY_NAME_FAILED',
        error,
        `Failed to execute evaluator by name: ${name}`
      );
    }

    return data;
  }

  /**
   * Duplicate an evaluator
   */
  async duplicate(id: string): Promise<EvaluatorDetail> {
    const { data, error } = await this._client.POST('/v1/evaluators/duplicate/{id}/', {
      params: { path: { id } },
      body: { name: `Copy of evaluator ${id}` }
    });

    if (error) {
      throw new RootSignalsError(
        (error as any)?.status ?? 500,
        'DUPLICATE_EVALUATOR_FAILED',
        error,
        `Failed to duplicate evaluator ${id}`
      );
    }

    return data;
  }
}