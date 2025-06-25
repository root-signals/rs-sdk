// Mock API responses for testing
export const mockResponses = {
  evaluators: {
    list: {
      results: [
        {
          id: '31a16e18-afc4-4f85-bb16-cc7635fc8829',
          name: 'Precision of Scorers Description',
          requires_expected_output: false,
          requires_contexts: false,
          requires_functions: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 'f96a49f5-4ff0-478d-b04c-db96bc6cd1b9',
          name: 'Comprehensiveness of Scorers',
          requires_expected_output: true,
          requires_contexts: false,
          requires_functions: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ],
      next: null,
      previous: null
    },
    
    detail: {
      id: '31a16e18-afc4-4f85-bb16-cc7635fc8829',
      name: 'Precision of Scorers Description',
      requires_expected_output: false,
      requires_contexts: false,
      requires_functions: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      objective: {
        id: 'obj-123',
        intent: 'Test objective'
      }
    },
    
    execution: {
      score: 0.85,
      justification: 'The response demonstrates good precision and detail in the scorer description.'
    }
  },

  judges: {
    list: {
      results: [
        {
          id: 'f6ba8a25-77ae-46fe-86f4-1ced13be81d2',
          name: 'Test Judge',
          intent: 'Evaluate customer service responses for helpfulness and politeness',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ],
      next: null,
      previous: null
    },
    
    detail: {
      id: 'f6ba8a25-77ae-46fe-86f4-1ced13be81d2',
      name: 'Test Judge',
      intent: 'Evaluate customer service responses for helpfulness and politeness',
      evaluators: [],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    },
    
    execution: {
      evaluator_results: [
        {
          evaluator_id: 'eval-123',
          evaluator_name: 'Helpfulness',
          score: 0.9,
          justification: 'Response is very helpful'
        }
      ]
    },
    
    generation: {
      judge_id: 'generated-judge-123',
      error_code: null
    }
  },

  objectives: {
    list: {
      results: [
        {
          id: '286d3f8c-264e-45e8-82e7-312ef6455e8b',
          intent: 'Test objective for code review politeness',
          status: 'listed',
          owner: {
            email: 'test@example.com',
            full_name: 'Test User'
          },
          created_at: '2024-01-01T00:00:00Z',
          validators: []
        }
      ],
      next: null,
      previous: null
    },
    
    detail: {
      id: '286d3f8c-264e-45e8-82e7-312ef6455e8b',
      intent: 'Test objective for code review politeness',
      status: 'listed',
      test_set: null,
      validators: [],
      created_at: '2024-01-01T00:00:00Z',
      owner: {
        email: 'test@example.com',
        full_name: 'Test User'
      },
      version_id: 'version-123',
      test_dataset_id: null
    },
    
    create: {
      id: 'new-objective-123'
    }
  },

  models: {
    list: {
      results: [
        {
          id: '46ea5586-95c0-468d-a636-82c7989736fb',
          name: 'claude-2',
          model: 'claude-2',
          max_token_count: 100000,
          max_output_token_count: 4096,
          created_at: '2024-01-01T00:00:00Z'
        }
      ],
      next: null,
      previous: null
    },
    
    detail: {
      id: '46ea5586-95c0-468d-a636-82c7989736fb',
      name: 'claude-2',
      model: 'claude-2',
      max_token_count: 100000,
      max_output_token_count: 4096,
      created_at: '2024-01-01T00:00:00Z'
    }
  },

  executionLogs: {
    list: {
      results: [
        {
          id: '820f5be9-f51f-4757-8da8-26b0bfbcb585',
          created_at: '2024-01-01T00:00:00Z',
          cost: 0.001,
          score: 0.85,
          model: 'gpt-3.5-turbo'
        }
      ],
      next: null,
      previous: null
    },
    
    detail: {
      id: '820f5be9-f51f-4757-8da8-26b0bfbcb585',
      created_at: '2024-01-01T00:00:00Z',
      cost: 0.001,
      score: 0.85,
      model: 'gpt-3.5-turbo',
      execution_duration: 1.5,
      token_count: 100
    }
  },

  errors: {
    notFound: {
      detail: 'Not found.'
    },
    
    unauthorized: {
      detail: 'Invalid authentication credentials.'
    },
    
    badRequest: {
      detail: 'Invalid input.'
    },
    
    validation: {
      non_field_errors: ['This field is required.']
    }
  }
};