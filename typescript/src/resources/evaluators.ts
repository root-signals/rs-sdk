import type { paths, components } from '../generated/types.js';
import {
  PaginatedResponse,
  ListParams,
  RootSignalsError,
  ExecutionPayload,
  ApiError,
} from '../types/common.js';

type Client = ReturnType<typeof import('openapi-fetch').default<paths>>;

export type EvaluatorListItem = components['schemas']['EvaluatorListOutput'];
export type EvaluatorDetail = components['schemas']['Evaluator'];
export type ExecutionResult = components['schemas']['EvaluatorExecutionResult'];
export type EvaluatorRequest = components['schemas']['EvaluatorRequest'];

export interface EvaluatorWithExecute extends EvaluatorDetail {
  execute(payload: ExecutionPayload): Promise<ExecutionResult>;
}

export interface EvaluatorListParams extends ListParams {
  is_preset?: boolean;
  is_public?: boolean;
}

export interface EvaluatorCreateParams {
  name: string;
  predicate: string;
  intent?: string;
  model?: string;
  models?: string[];
  system_message?: string;
  change_note?: string;
  status?: components['schemas']['StatusEnum'];
  overwrite?: boolean;
  objective_id?: string;
  objective_version_id?: string;
}

export class EvaluatorsResource {
  constructor(private _client: Client) {}

  /**
   * List all accessible evaluators
   */
  async list(params: EvaluatorListParams = {}): Promise<PaginatedResponse<EvaluatorListItem>> {
    const { data, error } = await this._client.GET('/v1/evaluators/', {
      params: { query: params },
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'LIST_EVALUATORS_FAILED',
        error,
        'Failed to list evaluators',
      );
    }

    return {
      results: data.results,
      next: data.next ?? undefined,
      previous: data.previous ?? undefined,
    };
  }

  /**
   * Get a specific evaluator by ID
   */
  async get(id: string): Promise<EvaluatorDetail> {
    const { data, error } = await this._client.GET('/v1/evaluators/{id}/', {
      params: { path: { id } },
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'GET_EVALUATOR_FAILED',
        error,
        `Failed to get evaluator ${id}`,
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
      body: payload,
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'EXECUTE_EVALUATOR_FAILED',
        error,
        `Failed to execute evaluator ${id}`,
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
      body: payload,
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'EXECUTE_EVALUATOR_BY_NAME_FAILED',
        error,
        `Failed to execute evaluator by name: ${name}`,
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
      // @ts-expect-error - TODO: fix this
      body: {},
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'DUPLICATE_EVALUATOR_FAILED',
        error,
        `Failed to duplicate evaluator ${id}`,
      );
    }

    return data;
  }

  async create(params: EvaluatorCreateParams): Promise<EvaluatorWithExecute> {
    if (params.objective_id && params.intent) {
      throw new RootSignalsError(
        400,
        'INVALID_PARAMS',
        {},
        'Objective ID and intent cannot be used together',
      );
    }

    let objectiveId: string;

    if (params.intent) {
      const { data: objectiveResponse, error } = await this._client.POST('/v1/objectives/', {
        body: {
          intent: params.intent,
        },
      });

      if (error) {
        throw new RootSignalsError(
          (error as ApiError)?.status ?? 500,
          'CREATE_OBJECTIVE_FAILED',
          error,
          'Failed to create objective',
        );
      }
      objectiveId = objectiveResponse.id;
    } else if (params.objective_id) {
      objectiveId = params.objective_id;
    } else {
      throw new RootSignalsError(400, 'INVALID_PARAMS', {}, 'Objective ID or intent is required');
    }

    const requestBody: EvaluatorRequest = {
      name: params.name,
      objective_id: objectiveId,
      overwrite: params.overwrite ?? false,
      prompt: params.predicate,
    };
    if (params.system_message) {
      requestBody.system_message = params.system_message;
    }
    if (params.models) {
      requestBody.models = params.models;
    }
    if (params.status) {
      requestBody.status = params.status;
    }
    if (params.overwrite !== undefined) {
      requestBody.overwrite = params.overwrite;
    }

    if (objectiveId) {
      requestBody.objective_id = objectiveId;
    }
    if (params.objective_version_id) {
      requestBody.objective_version_id = params.objective_version_id;
    }

    const { data, error } = await this._client.POST('/v1/evaluators/', {
      body: requestBody,
    });

    if (error) {
      throw new RootSignalsError(
        (error as ApiError)?.status ?? 500,
        'CREATE_EVALUATOR_FAILED',
        error,
        'Failed to create evaluator',
      );
    }

    const evaluatorWithExecute: EvaluatorWithExecute = {
      ...data,
      execute: (payload: ExecutionPayload) => this.execute(data.id, payload),
    };

    return evaluatorWithExecute;
  }
}
