/**
 * Mock data for RAG Chat E2E tests
 */

/**
 * Sample documents for testing
 */
export const mockDocuments = [
  {
    doc_id: 'doc_1',
    filename: 'introduction_to_rag.pdf',
    content: 'Retrieval Augmented Generation (RAG) is a technique that combines...',
  },
  {
    doc_id: 'doc_2',
    filename: 'vector_search_guide.md',
    content: 'Vector search is a method of finding similar items based on...',
  },
  {
    doc_id: 'doc_3',
    filename: 'llm_prompts.txt',
    content: 'Effective prompts for LLMs should be clear, specific, and include...',
  },
];

/**
 * Sample queries for testing
 */
export const mockQueries = [
  'What is RAG?',
  'How does vector search work?',
  'Explain the difference between embedding models',
  'What are the best practices for prompt engineering?',
  'How can I improve retrieval accuracy?',
];

/**
 * Mock streaming response chunks
 */
export const mockStreamingResponse = {
  success: [
    'Here is a comprehensive answer based on your documents:',
    'RAG combines retrieval and generation to produce accurate responses.',
    'The key components are:',
    '- Document retrieval',
    '- Context augmentation',
    '- Response generation',
    'This approach ensures factual accuracy and relevance.',
  ],
  partial: [
    'Based on the retrieved documents...',
    'The answer involves multiple steps...',
  ],
  error: {
    message: 'An error occurred while processing your request.',
    code: 'RAG_ERROR_001',
  },
};

/**
 * Mock sources/retrieval results
 */
export const mockSources = [
  {
    text: 'Retrieval Augmented Generation (RAG) is a technique that combines information retrieval with text generation...',
    score: 0.95,
    metadata: {
      source: 'introduction_to_rag.pdf',
      page: 1,
      chunk_id: 'chunk_001',
    },
  },
  {
    text: 'Vector search uses embeddings to find semantically similar documents...',
    score: 0.87,
    metadata: {
      source: 'vector_search_guide.md',
      page: 3,
      chunk_id: 'chunk_042',
    },
  },
  {
    text: 'Effective prompts should include context, instructions, and examples...',
    score: 0.72,
    metadata: {
      source: 'llm_prompts.txt',
      line: 15,
      chunk_id: 'chunk_103',
    },
  },
];

/**
 * Mock API responses
 */
export const mockAPIResponses = {
  documentsList: {
    documents: mockDocuments.map((d) => ({
      doc_id: d.doc_id,
      filename: d.filename,
    })),
    total: mockDocuments.length,
  },
  chatStream: (message: string) => ({
    query: message,
    session_id: 'test_session',
    response: mockStreamingResponse.success.join(' '),
    sources: mockSources,
  }),
  uploadSuccess: {
    id: 'doc_new_001',
    filename: 'test_upload.pdf',
    status: 'success',
    message: 'Document uploaded successfully',
  },
  uploadError: {
    status: 'error',
    message: 'Failed to process document',
  },
};

/**
 * Test data factories
 */
export const TestDataFactory = {
  createDocument: (overrides = {}) => ({
    doc_id: `doc_${Date.now()}`,
    filename: 'test_document.pdf',
    content: 'Test document content',
    ...overrides,
  }),

  createQuery: (overrides = {}) => ({
    query: 'Test query',
    session_id: `session_${Date.now()}`,
    top_k: 5,
    temperature: 0.7,
    ...overrides,
  }),

  createSource: (overrides = {}) => ({
    text: 'Sample source text',
    score: 0.85,
    metadata: {
      source: 'document.pdf',
      page: 1,
    },
    ...overrides,
  }),
};

/**
 * Test file paths for upload testing
 */
export const testFiles = {
  valid: [
    '/path/to/test-document.pdf',
    '/path/to/test-notes.md',
    '/path/to/test-report.txt',
  ],
  invalid: [
    '/path/to/image.png',
    '/path/to/spreadsheet.xlsx',
    '/path/to/executable.exe',
  ],
};
