import { ClientConfig } from '../types/common.js';

export function createAuthHeaders(config: ClientConfig): Record<string, string> {
  return {
    Authorization: `Api-Key ${config.apiKey}`,
    'Content-Type': 'application/json',
    'User-Agent': '@root-signals/scorable/0.1.4',
  };
}

export function createApiParams(apiKey: string): {
  headers: Record<string, string>;
} {
  return {
    headers: createAuthHeaders({ apiKey }),
  };
}
