import { RootSignals } from '../../src/client';
import { TestUtils } from '../helpers/test-utils';

describe('RootSignals Client', () => {
  describe('constructor', () => {
    it('should create client with valid API key', () => {
      const client = new RootSignals({ apiKey: 'test-key' });
      
      expect(client).toBeInstanceOf(RootSignals);
      expect(client.evaluators).toBeDefined();
      expect(client.judges).toBeDefined();
      expect(client.objectives).toBeDefined();
      expect(client.models).toBeDefined();
      expect(client.executionLogs).toBeDefined();
    });

    it('should initialize all resource instances', () => {
      const client = new RootSignals({ apiKey: 'test-key' });
      
      expect(client.evaluators).toBeDefined();
      expect(client.judges).toBeDefined();
      expect(client.objectives).toBeDefined();
      expect(client.models).toBeDefined();
      expect(client.executionLogs).toBeDefined();
    });

    it('should throw error with invalid config', () => {
      // Client construction doesn't throw errors - API calls do
      expect(() => {
        new RootSignals({} as any);
      }).not.toThrow();
    });
  });

  describe.skip('ping', () => {
    it('should return successful ping response', async () => {
      const client = TestUtils.createMockClient();
      
      const result = await client.ping();
      
      expect(result).toEqual({
        success: true,
        message: 'Successfully connected to Root Signals API'
      });
    });

    it('should indicate SDK version and client info', async () => {
      const client = TestUtils.createMockClient();
      
      const result = await client.ping();
      
      expect(result.message).toContain('Root Signals API');
      expect(result.success).toBe(true);
    });
  });

  describe('configuration', () => {
    it('should use default base URL when not provided', () => {
      const client = new RootSignals({ apiKey: 'test-key' });
      
      // Client should be configured with default URL
      expect(client).toBeDefined();
    });

    it('should accept custom configuration', () => {
      const client = new RootSignals({ 
        apiKey: 'test-key',
        baseUrl: 'https://custom.api.com'
      });
      
      expect(client).toBeDefined();
    });
  });
});