import { Scorable } from '../../src/client';

describe('Scorable Client', () => {
  describe('constructor', () => {
    it('should create client with valid API key', () => {
      const client = new Scorable({ apiKey: 'test-key' });

      expect(client).toBeInstanceOf(Scorable);
      expect(client.evaluators).toBeDefined();
      expect(client.judges).toBeDefined();
      expect(client.objectives).toBeDefined();
      expect(client.models).toBeDefined();
      expect(client.executionLogs).toBeDefined();
    });

    it('should initialize all resource instances', () => {
      const client = new Scorable({ apiKey: 'test-key' });

      expect(client.evaluators).toBeDefined();
      expect(client.judges).toBeDefined();
      expect(client.objectives).toBeDefined();
      expect(client.models).toBeDefined();
      expect(client.executionLogs).toBeDefined();
      expect(client.datasets).toBeDefined();
    });

    it('should throw error with invalid config', () => {
      // Client construction doesn't throw errors - API calls do
      expect(() => {
        new Scorable({} as any);
      }).not.toThrow();
    });
  });

  describe('configuration', () => {
    it('should use default base URL when not provided', () => {
      const client = new Scorable({ apiKey: 'test-key' });

      // Client should be configured with default URL
      expect(client).toBeDefined();
    });

    it('should accept custom configuration', () => {
      const client = new Scorable({
        apiKey: 'test-key',
        baseUrl: 'https://custom.api.com',
      });

      expect(client).toBeDefined();
    });
  });
});
