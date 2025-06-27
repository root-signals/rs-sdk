import { RootSignalsError } from '../../src/types/common';

describe('RootSignalsError', () => {
  describe('constructor', () => {
    it('should create error with all parameters', () => {
      const error = new RootSignalsError(
        404,
        'RESOURCE_NOT_FOUND',
        { detail: 'Resource not found' },
        'Custom error message',
      );

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(RootSignalsError);
      expect(error.status).toBe(404);
      expect(error.code).toBe('RESOURCE_NOT_FOUND');
      expect(error.details).toEqual({ detail: 'Resource not found' });
      expect(error.message).toBe('Custom error message');
      expect(error.name).toBe('RootSignalsError');
    });

    it('should create error with minimal parameters', () => {
      const error = new RootSignalsError(500, 'INTERNAL_ERROR');

      expect(error.status).toBe(500);
      expect(error.code).toBe('INTERNAL_ERROR');
      expect(error.details).toBeUndefined();
      expect(error.message).toBe(`API Error 500: INTERNAL_ERROR`);
      expect(error.name).toBe('RootSignalsError');
    });

    it('should use custom message when provided', () => {
      const error = new RootSignalsError(
        400,
        'VALIDATION_ERROR',
        { field: 'name is required' },
        'Validation failed',
      );

      expect(error.message).toBe('Validation failed');
    });

    it('should be throwable', () => {
      expect(() => {
        throw new RootSignalsError(404, 'NOT_FOUND');
      }).toThrow(RootSignalsError);
    });

    it('should preserve error stack trace', () => {
      const error = new RootSignalsError(500, 'INTERNAL_ERROR');

      expect(error.stack).toBeDefined();
      expect(error.stack).toContain('RootSignalsError');
    });
  });

  describe('error handling patterns', () => {
    it('should handle API error responses', () => {
      const apiResponse = {
        detail: 'Invalid evaluator ID provided',
      };

      const error = new RootSignalsError(
        404,
        'EVALUATOR_NOT_FOUND',
        apiResponse,
        'Evaluator not found',
      );

      expect(error.status).toBe(404);
      expect(error.details).toEqual(apiResponse);
    });

    it('should handle validation errors', () => {
      const validationErrors = {
        name: ['This field is required.'],
        email: ['Enter a valid email address.'],
      };

      const error = new RootSignalsError(
        400,
        'VALIDATION_ERROR',
        validationErrors,
        'Validation failed',
      );

      expect(error.status).toBe(400);
      expect(error.details).toEqual(validationErrors);
    });

    it('should handle network errors', () => {
      const error = new RootSignalsError(
        0,
        'NETWORK_ERROR',
        { cause: 'Connection refused' },
        'Network connection failed',
      );

      expect(error.status).toBe(0);
      expect(error.code).toBe('NETWORK_ERROR');
    });
  });
});
