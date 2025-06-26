import { TestUtils } from '../helpers/test-utils';
import { mockClient } from '../helpers/mock-client';
import { mockResponses } from '../fixtures/mock-responses';
import { TestDataFactory } from '../fixtures/test-data';

describe('JudgesResource', () => {
  let client: any;

  beforeEach(() => {
    client = TestUtils.createMockClient();
    mockClient.reset();
  });

  describe('list', () => {
    it('should list judges successfully', async () => {
      mockClient.setMockResponse('GET', '/v1/judges/', {
        data: mockResponses.judges.list,
        error: undefined,
      });

      const result = await client.judges.list();

      expect(result.results).toHaveLength(1);
      expect(result.results[0]).toHaveProperty('id');
      expect(result.results[0]).toHaveProperty('name');
      expect(result.results[0]).toHaveProperty('intent');
    });

    it('should handle pagination parameters', async () => {
      await client.judges.list({ page_size: 5, search: 'test' });

      expect(mockClient.GET).toHaveBeenCalledWith('/v1/judges/', {
        params: {
          query: { page_size: 5, search: 'test' },
        },
      });
    });
  });

  describe('get', () => {
    it('should get judge by ID', async () => {
      const judgeId = 'f6ba8a25-77ae-46fe-86f4-1ced13be81d2';
      mockClient.setMockResponse('GET', `/v1/judges/${judgeId}/`, {
        data: mockResponses.judges.detail,
        error: undefined,
      });

      const result = await client.judges.get(judgeId);

      expect(result.id).toBe(judgeId);
      expect(result.name).toBe('Test Judge');
      expect(result.intent).toBeDefined();
    });
  });

  describe('create', () => {
    it('should create judge successfully', async () => {
      const judgeData = {
        name: 'New Test Judge',
        intent: 'Test judge for evaluation',
        evaluators: [],
      };

      const createdJudge = TestDataFactory.createJudge(judgeData);
      mockClient.setMockResponse('POST', '/v1/judges/', {
        data: createdJudge,
        error: undefined,
      });

      const result = await client.judges.create(judgeData);

      expect(result.name).toBe(judgeData.name);
      expect(result.intent).toBe(judgeData.intent);
      expect(mockClient.POST).toHaveBeenCalledWith('/v1/judges/', {
        body: judgeData,
      });
    });

    it('should handle validation errors', async () => {
      mockClient.setMockError('POST', '/v1/judges/', {
        name: ['This field is required.'],
      });

      await expect(client.judges.create({ intent: 'Missing name' })).rejects.toThrow();
    });
  });

  describe('update', () => {
    it('should update judge successfully', async () => {
      const judgeId = 'judge-123';
      const updateData = {
        name: 'Updated Judge Name',
        intent: 'Updated intent',
        evaluators: [],
      };

      const updatedJudge = TestDataFactory.createJudge({
        id: judgeId,
        ...updateData,
      });
      mockClient.setMockResponse('PUT', `/v1/judges/${judgeId}/`, {
        data: updatedJudge,
        error: undefined,
      });

      const result = await client.judges.update(judgeId, updateData);

      expect(result.id).toBe(judgeId);
      expect(result.name).toBe(updateData.name);
      expect(mockClient.PUT).toHaveBeenCalledWith(`/v1/judges/${judgeId}/`, {
        params: { path: { id: judgeId } },
        body: updateData,
      });
    });
  });

  describe('patch', () => {
    it.skip('should partially update judge', async () => {
      const judgeId = 'judge-123';
      const patchData = { name: 'Partially Updated Name' };

      const patchedJudge = TestDataFactory.createJudge({
        id: judgeId,
        ...patchData,
      });
      mockClient.setMockResponse('PATCH', `/v1/judges/${judgeId}/`, {
        data: patchedJudge,
        error: undefined,
      });

      const result = await client.judges.patch(judgeId, patchData);

      expect(result.name).toBe(patchData.name);
      expect(mockClient.PATCH).toHaveBeenCalledWith(`/v1/judges/${judgeId}/`, {
        params: { path: { id: judgeId } },
        body: patchData,
      });
    });
  });

  describe('delete', () => {
    it('should delete judge successfully', async () => {
      const judgeId = 'judge-123';
      mockClient.setMockResponse('DELETE', `/v1/judges/${judgeId}/`, {
        data: undefined,
        error: undefined,
      });

      await client.judges.delete(judgeId);

      expect(mockClient.DELETE).toHaveBeenCalledWith(`/v1/judges/${judgeId}/`, {
        params: { path: { id: judgeId } },
      });
    });

    it('should handle delete errors', async () => {
      const judgeId = 'judge-123';
      mockClient.setMockError('DELETE', `/v1/judges/${judgeId}/`, {
        detail: 'Cannot delete judge with active evaluations.',
      });

      await expect(client.judges.delete(judgeId)).rejects.toThrow();
    });
  });

  describe('execute', () => {
    it('should execute judge successfully', async () => {
      const judgeId = 'judge-123';
      const executionData = TestDataFactory.getTestJudgeInputs();

      mockClient.setMockResponse('POST', `/v1/judges/${judgeId}/execute/`, {
        data: mockResponses.judges.execution,
        error: undefined,
      });

      const result = await client.judges.execute(judgeId, executionData);

      expect(result.evaluator_results).toBeDefined();
      expect(Array.isArray(result.evaluator_results)).toBe(true);
      expect(mockClient.POST).toHaveBeenCalledWith(`/v1/judges/${judgeId}/execute/`, {
        params: { path: { judge_id: judgeId } },
        body: executionData,
      });
    });
  });

  describe('generate', () => {
    it('should generate judge with string intent', async () => {
      const intent = 'Evaluate code review comments for clarity';
      mockClient.setMockResponse('POST', '/v1/judges/generate/', {
        data: mockResponses.judges.generation,
        error: undefined,
      });

      const result = await client.judges.generate(intent);

      expect(result.judge_id).toBeDefined();
      expect(mockClient.POST).toHaveBeenCalledWith('/v1/judges/generate/', {
        body: { intent },
      });
    });

    it('should generate judge with detailed request', async () => {
      const generateRequest = {
        intent: 'Evaluate responses for helpfulness',
        examples: [
          {
            input: 'Test input',
            good_output: 'Good response',
            bad_output: 'Bad response',
          },
        ],
      };

      mockClient.setMockResponse('POST', '/v1/judges/generate/', {
        data: mockResponses.judges.generation,
        error: undefined,
      });

      const result = await client.judges.generate(generateRequest);

      expect(result.judge_id).toBeDefined();
      expect(mockClient.POST).toHaveBeenCalledWith('/v1/judges/generate/', {
        body: generateRequest,
      });
    });
  });

  describe('duplicate', () => {
    it('should duplicate judge successfully', async () => {
      const judgeId = 'judge-123';
      const duplicatedJudge = TestDataFactory.createJudge({
        id: 'judge-duplicated-456',
        name: 'Test Judge (Copy)',
      });

      mockClient.setMockResponse('POST', `/v1/judges/${judgeId}/duplicate/`, {
        data: duplicatedJudge,
        error: undefined,
      });

      const result = await client.judges.duplicate(judgeId);

      expect(result.id).toBe('judge-duplicated-456');
      expect(mockClient.POST).toHaveBeenCalledWith(`/v1/judges/${judgeId}/duplicate/`, {
        params: { path: { id: judgeId } },
      });
    });
  });

  describe('invite', () => {
    it.skip('should send invitations successfully', async () => {
      const judgeId = 'judge-123';
      const emails = ['user1@example.com', 'user2@example.com'];

      mockClient.setMockResponse('POST', `/v1/judges/${judgeId}/invite/`, {
        data: { success: true },
        error: undefined,
      });

      const result = await client.judges.invite(judgeId, emails);

      expect(result.success).toBe(true);
      expect(mockClient.POST).toHaveBeenCalledWith(`/v1/judges/${judgeId}/invite/`, {
        params: { path: { id: judgeId } },
        body: { emails },
      });
    });

    it.skip('should handle too many emails', async () => {
      const judgeId = 'judge-123';
      const tooManyEmails = Array(15).fill('user@example.com');

      mockClient.setMockError('POST', `/v1/judges/${judgeId}/invite/`, {
        emails: ['Maximum 10 emails allowed.'],
      });

      await expect(client.judges.invite(judgeId, tooManyEmails)).rejects.toThrow();
    });
  });
});
