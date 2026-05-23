import { test as base } from '@playwright/test';

/**
 * Custom fixtures for RAG Chat E2E tests
 */

interface RAGTestData {
  testQuery: string;
  testDocument: {
    id: string;
    title: string;
    content: string;
  };
  mockResponse: string;
}

/**
 * Create custom test with RAG-specific fixtures
 */
export const test = base.extend<{ ragData: RAGTestData }>({
  ragData: async ({ page }, use) => {
    const data: RAGTestData = {
      testQuery: 'What is retrieval augmented generation?',
      testDocument: {
        id: 'doc_test_1',
        title: 'test_document.pdf',
        content: 'This is a test document for RAG testing purposes.',
      },
      mockResponse: `Based on the retrieved documents, RAG (Retrieval Augmented Generation) is a technique that combines:

1. **Retrieval** - Finding relevant documents from a knowledge base
2. **Augmentation** - Adding retrieved context to the LLM prompt
3. **Generation** - Producing responses using both the query and retrieved content

This approach helps improve the accuracy and relevance of LLM responses by grounding them in specific documents.`,
    };

    await use(data);
  },
});

export { expect } from '@playwright/test';
