import { createAuthHeaders } from '../../src/utils/auth';

describe('Authentication', () => {
  describe('createAuthHeaders', () => {
    it('should create correct auth headers with API key', () => {
      const config = { apiKey: 'test-api-key-123' };
      const headers = createAuthHeaders(config);

      expect(headers).toEqual({
        'Authorization': 'Api-Key test-api-key-123',
        'Content-Type': 'application/json',
        'User-Agent': '@root-signals/typescript-sdk/0.1.0'
      });
    });

    it('should handle empty API key', () => {
      const config = { apiKey: '' };
      const headers = createAuthHeaders(config);

      expect(headers['Authorization']).toBe('Api-Key ');
      expect(headers['Content-Type']).toBe('application/json');
      expect(headers['User-Agent']).toBe('@root-signals/typescript-sdk/0.1.0');
    });

    it('should handle special characters in API key', () => {
      const config = { apiKey: 'test-key-with-special@#$%chars' };
      const headers = createAuthHeaders(config);

      expect(headers['Authorization']).toBe('Api-Key test-key-with-special@#$%chars');
    });

    it('should always include required headers', () => {
      const config = { apiKey: 'any-key' };
      const headers = createAuthHeaders(config);

      expect(headers).toHaveProperty('Authorization');
      expect(headers).toHaveProperty('Content-Type');
      expect(headers).toHaveProperty('User-Agent');
      expect(Object.keys(headers)).toHaveLength(3);
    });
  });
});