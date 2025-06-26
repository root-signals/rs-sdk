import { TestUtils } from '../helpers/test-utils';
import { mockClient } from '../helpers/mock-client';
import { mockResponses } from '../fixtures/mock-responses';
import { TestDataFactory } from '../fixtures/test-data';

describe('EvaluatorsResource', () => {
  let client: any;

  beforeEach(() => {
    client = TestUtils.createMockClient();
    mockClient.reset();
  });

  describe('list', () => {
    it('should list evaluators successfully', async () => {
      mockClient.setMockResponse('GET', '/v1/evaluators/', {
        data: mockResponses.evaluators.list,
        error: undefined,
      });

      const result = await client.evaluators.list();

      expect(result.results).toHaveLength(2);
      expect(result.results[0]).toHaveProperty('id');
      expect(result.results[0]).toHaveProperty('name');
    });

    it('should handle pagination parameters', async () => {
      await client.evaluators.list({
        page_size: 10,
        cursor: 'next-cursor',
      });

      expect(mockClient.GET).toHaveBeenCalledWith('/v1/evaluators/', {
        params: {
          query: { page_size: 10, cursor: 'next-cursor' },
        },
      });
    });

    it('should handle empty results', async () => {
      mockClient.setMockResponse('GET', '/v1/evaluators/', {
        data: { results: [], next: null, previous: null },
        error: undefined,
      });

      const result = await client.evaluators.list();

      expect(result.results).toHaveLength(0);
    });
  });

  describe('get', () => {
    it('should get evaluator by ID', async () => {
      const evaluatorId = '31a16e18-afc4-4f85-bb16-cc7635fc8829';
      mockClient.setMockResponse('GET', `/v1/evaluators/${evaluatorId}/`, {
        data: mockResponses.evaluators.detail,
        error: undefined,
      });

      const result = await client.evaluators.get(evaluatorId);

      expect(result.id).toBe(evaluatorId);
      expect(result.name).toBe('Precision of Scorers Description');
      expect(mockClient.GET).toHaveBeenCalledWith(`/v1/evaluators/${evaluatorId}/`, {
        params: { path: { id: evaluatorId } },
      });
    });

    it('should handle invalid evaluator ID', async () => {
      const invalidId = 'invalid-id';
      mockClient.setMockError('GET', `/v1/evaluators/${invalidId}/`, {
        detail: 'Not found.',
      });

      await expect(client.evaluators.get(invalidId)).rejects.toThrow();
    });
  });

  describe('execute', () => {
    it('should execute evaluator successfully', async () => {
      const evaluatorId = 'eval-123';
      const executionData = TestDataFactory.getTestExecutionInputs();

      mockClient.setMockResponse('POST', `/v1/evaluators/${evaluatorId}/execute/`, {
        data: mockResponses.evaluators.execution,
        error: undefined,
      });

      const result = await client.evaluators.execute(evaluatorId, executionData);

      expect(result.score).toBe(0.85);
      expect(result.justification).toBeDefined();
      expect(mockClient.POST).toHaveBeenCalledWith(`/v1/evaluators/${evaluatorId}/execute/`, {
        params: { path: { id: evaluatorId } },
        body: executionData,
      });
    });

    it('should handle missing required parameters', async () => {
      const evaluatorId = 'eval-123';
      mockClient.setMockError('POST', `/v1/evaluators/${evaluatorId}/execute/`, {
        request: ['This field is required.'],
      });

      await expect(client.evaluators.execute(evaluatorId, {})).rejects.toThrow();
    });
  });

  describe('executeByName', () => {
    it('should execute evaluator by name', async () => {
      const evaluatorName = 'Test Evaluator';
      const executionData = TestDataFactory.getTestExecutionInputs();

      mockClient.setMockResponse('POST', `/v1/evaluators/execute/${evaluatorName}/`, {
        data: mockResponses.evaluators.execution,
        error: undefined,
      });

      const result = await client.evaluators.executeByName(evaluatorName, executionData);

      expect(result.score).toBe(0.85);
      expect(result.justification).toBeDefined();
    });

    it('should handle non-existent evaluator name', async () => {
      const invalidName = 'Non Existent Evaluator';
      mockClient.setMockError('POST', `/v1/evaluators/execute/${invalidName}/`, {
        detail: 'Evaluator not found.',
      });

      await expect(client.evaluators.executeByName(invalidName, {})).rejects.toThrow();
    });
  });

  describe('duplicate', () => {
    it('should duplicate evaluator successfully', async () => {
      const evaluatorId = 'eval-123';
      const duplicatedEvaluator = TestDataFactory.createEvaluator({
        id: 'eval-duplicated-456',
        name: 'Test Evaluator (Copy)',
      });

      mockClient.setMockResponse('POST', `/v1/evaluators/duplicate/${evaluatorId}/`, {
        data: duplicatedEvaluator,
        error: undefined,
      });

      const result = await client.evaluators.duplicate(evaluatorId);

      expect(result.id).toBe('eval-duplicated-456');
      expect(result.name).toContain('Copy');
      expect(mockClient.POST).toHaveBeenCalledWith(`/v1/evaluators/duplicate/${evaluatorId}/`, {
        params: { path: { id: evaluatorId } },
      });
    });

    it('should handle permission errors', async () => {
      const evaluatorId = 'eval-123';
      mockClient.setMockError('POST', `/v1/evaluators/duplicate/${evaluatorId}/`, {
        detail: 'Permission denied.',
      });

      await expect(client.evaluators.duplicate(evaluatorId)).rejects.toThrow();
    });
  });

  describe('error handling', () => {
    it('should throw RootSignalsError on API errors', async () => {
      mockClient.setMockError('GET', '/v1/evaluators/', {
        detail: 'Internal server error',
      });

      await expect(client.evaluators.list()).rejects.toThrow('LIST_EVALUATORS_FAILED');
    });

    it('should handle network timeouts', async () => {
      mockClient.GET.mockRejectedValue(new Error('Network timeout'));

      await expect(client.evaluators.list()).rejects.toThrow();
    });
  });
});
