import { Page, Locator, APIRequestContext } from '@playwright/test';

/**
 * Page Object for RAG Chat functionality
 * Encapsulates all interactions with the RAG Chat component
 */
export class RAGChatPage {
  readonly page: Page;
  readonly request: APIRequestContext;

  // Main components
  readonly header: Locator;
  readonly modelBadge: Locator;
  readonly chatContainer: Locator;

  // Documents section
  readonly documentsSection: Locator;
  readonly sectionTitle: Locator;
  readonly documentCards: Locator;
  readonly selectAllButton: Locator;
  readonly clearSelectionButton: Locator;
  readonly emptyDocsMessage: Locator;

  // File upload
  readonly fileUploadArea: Locator;
  readonly fileInput: Locator;
  readonly uploadLabel: Locator;
  readonly uploadButton: Locator;

  // Chat input
  readonly messageInput: Locator;
  readonly sendButton: Locator;

  // Messages
  readonly emptyState: Locator;
  readonly quickActions: Locator;
  readonly userMessages: Locator;
  readonly assistantMessages: Locator;
  readonly sourceBadges: Locator;

  // Toast notifications
  readonly toastContainer: Locator;

  // Navigation
  readonly ragTab: Locator;

  constructor(page: Page) {
    this.page = page;
    this.request = page.context().request;

    // Header components
    this.header = page.locator('h2').filter({ hasText: /RAG|文档问答|Document/i });
    this.modelBadge = page.locator('header, [class*="Header"]').last().locator('span').filter({ hasText: /model|Model/i });

    // Chat container
    this.chatContainer = page.locator('[class*="ChatContainer"]').first();

    // Documents section
    this.documentsSection = page.locator('[class*="DocumentsSection"]').first();
    this.sectionTitle = page.locator('h3, [class*="SectionTitle"]').filter({ hasText: /文档|Documents/i });
    this.documentCards = page.locator('[class*="DocumentCard"]');
    this.selectAllButton = page.locator('button').filter({ hasText: /全选|Select All|选择全部/i });
    this.clearSelectionButton = page.locator('button').filter({ hasText: /清除|Clear|取消选择/i });
    this.emptyDocsMessage = page.locator('[class*="EmptyDocsMessage"], p').filter({ hasText: /没有文档|No documents|暂无/i });

    // File upload
    this.fileUploadArea = page.locator('[class*="FileUploadArea"]').first();
    this.fileInput = page.locator('input[type="file"]#file-upload');
    this.uploadLabel = page.locator('label[for="file-upload"], [class*="FileUploadLabel"]');
    this.uploadButton = page.locator('[class*="UploadButton"], button').filter({ hasText: /上传|Upload|上传文档/i });

    // Chat input
    this.messageInput = page.locator('textarea').last();
    this.sendButton = page.locator('[class*="SendButton"]');

    // Messages
    this.emptyState = page.locator('[class*="EmptyState"]').first();
    this.quickActions = page.locator('[class*="QuickAction"], [class*="QuickActions"] button');
    this.userMessages = page.locator('[class*="MessageBubble"]').filter({ has: page.locator('[class*="MessageContent"]') });
    this.assistantMessages = page.locator('[class*="MessageBubble"]');
    this.sourceBadges = page.locator('[class*="SourceBadge"]');

    // Toast
    this.toastContainer = page.locator('[class*="ToastContainer"]');

    // Navigation - Document QA tab
    this.ragTab = page.locator('button, [role="tab"], a').filter({ hasText: /文档问答|Document QA|文档/i });
  }

  /**
   * Navigate to the RAG Chat page/tab
   */
  async navigateToRAG(): Promise<void> {
    await this.ragTab.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Send a message in the chat
   */
  async sendMessage(message: string): Promise<void> {
    await this.messageInput.fill(message);
    await this.sendButton.click();
  }

  /**
   * Wait for assistant response
   */
  async waitForResponse(timeout: number = 30000): Promise<void> {
    await this.page.waitForSelector('[class*="MessageBubble"]:not([class*="user"])', { timeout });
  }

  /**
   * Get all user messages
   */
  async getUserMessages(): Promise<string[]> {
    return this.userMessages.allTextContents();
  }

  /**
   * Get all assistant messages
   */
  async getAssistantMessages(): Promise<string[]> {
    return this.assistantMessages.allTextContents();
  }

  /**
   * Select a document by title
   */
  async selectDocument(title: string): Promise<void> {
    const docCard = this.page.locator('[class*="DocumentCard"]').filter({ hasText: title });
    await docCard.click();
  }

  /**
   * Delete a document
   */
  async deleteDocument(title: string): Promise<void> {
    const deleteBtn = this.page.locator('[class*="DocumentCard"]')
      .filter({ hasText: title })
      .locator('[class*="DeleteButton"], button[aria-label*="删除"]');
    await deleteBtn.click();
  }

  /**
   * Upload a file
   */
  async uploadFile(filePath: string): Promise<void> {
    await this.fileInput.setInputFiles(filePath);
    await this.uploadButton.click();
  }

  /**
   * Click on source badge to expand sources
   */
  async expandSources(): Promise<void> {
    const badge = this.sourceBadges.first();
    if (await badge.isVisible()) {
      await badge.click();
    }
  }

  /**
   * Check if there are any sources in the response
   */
  async hasSources(): Promise<boolean> {
    return this.sourceBadges.first().isVisible();
  }

  /**
   * Wait for loading state to disappear
   */
  async waitForLoadingComplete(): Promise<void> {
    await this.page.waitForFunction(() => {
      const sendButton = document.querySelector('[class*="SendButton"]');
      const spinner = document.querySelector('[class*="Spinner"]');
      return !spinner || sendButton?.getAttribute('disabled') === null;
    }, { timeout: 60000 });
  }

  /**
   * Click on a quick action button
   */
  async clickQuickAction(text: string): Promise<void> {
    await this.quickActions.filter({ hasText: text }).click();
  }

  /**
   * Check if the empty state is displayed
   */
  async isEmptyStateVisible(): Promise<boolean> {
    return this.emptyState.isVisible();
  }

  /**
   * Get the count of available documents
   */
  async getDocumentCount(): Promise<number> {
    const countText = await this.sectionTitle.locator('[class*="DocumentCount"]').textContent();
    return countText ? parseInt(countText, 10) : 0;
  }

  /**
   * Mock RAG API responses
   */
  async mockRAGAPI(): Promise<void> {
    await this.page.route('**/chat/stream**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: `data: Hello! This is a mocked RAG response.\n\ndata: Based on your documents, here's what I found:\n\ndata: [DONE]`,
      });
    });

    await this.page.route('**/documents/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          documents: [
            { doc_id: 'doc_1', filename: 'sample_document.pdf' },
            { doc_id: 'doc_2', filename: 'test_file.md' },
          ],
        }),
      });
    });
  }

  /**
   * Clear all messages
   */
  async clearMessages(): Promise<void> {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
    await this.page.reload();
  }
}

// Export singleton instance for convenience
let pageInstance: RAGChatPage | null = null;

export function getRAGChatPage(page: Page): RAGChatPage {
  if (!pageInstance) {
    pageInstance = new RAGChatPage(page);
  }
  return pageInstance;
}
