/**
 * AIHub Component Tests
 * Comprehensive test suite for AIHub component covering Chat, Image Generation, and TTS features
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { AIHub } from '../AIHub';
import { I18nProvider } from '../../i18n';

// ==================== Browser API Mocks ====================

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn().mockReturnValue(null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
vi.stubGlobal('localStorage', localStorageMock);

// Mock navigator.language
Object.defineProperty(navigator, 'language', {
  value: 'en',
  writable: true,
});

// Mock URL.createObjectURL and URL.revokeObjectURL
const mockCreateObjectURL = vi.fn(() => 'blob:mock-url');
const mockRevokeObjectURL = vi.fn();
vi.stubGlobal('URL', {
  createObjectURL: mockCreateObjectURL,
  revokeObjectURL: mockRevokeObjectURL,
});

// Mock fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Mock scrollIntoView for jsdom
Element.prototype.scrollIntoView = vi.fn();

// ==================== Mock Data ====================

const mockVoices = [
  { id: 'en-US', name: 'English (US)', language: 'en-US', provider: 'browser', is_default: true },
  { id: 'en-GB', name: 'English (UK)', language: 'en-GB', provider: 'browser', is_default: false },
  { id: 'zh-CN', name: 'Chinese', language: 'zh-CN', provider: 'browser', is_default: false },
];

const mockProviders = [
  { name: 'openai', display_name: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini'], status: 'available' },
  { name: 'anthropic', display_name: 'Anthropic Claude', models: ['claude-sonnet-4-20250514'], status: 'available' },
  { name: 'ollama', display_name: 'Ollama (Local)', models: ['qwen2.5:7b', 'llama3.2:3b'], status: 'available' },
];

const mockModels = [
  { name: 'gpt-4o', provider: 'openai', status: 'available' },
  { name: 'gpt-4o-mini', provider: 'openai', status: 'available' },
];

// ==================== Mock aiServices ====================

const mockChatStream = vi.fn();
const mockGenerateImage = vi.fn();
const mockSynthesizeSpeech = vi.fn();
const mockGetVoices = vi.fn();
const mockGetProviders = vi.fn();
const mockGetModels = vi.fn();
const mockDownloadBase64Image = vi.fn();
const mockDownloadBlob = vi.fn();

vi.mock('../../lib/aiServices', () => ({
  chatStream: (...args: unknown[]) => mockChatStream(...args),
  generateImage: (...args: unknown[]) => mockGenerateImage(...args),
  synthesizeSpeech: (...args: unknown[]) => mockSynthesizeSpeech(...args),
  getVoices: (...args: unknown[]) => mockGetVoices(...args),
  getProviders: (...args: unknown[]) => mockGetProviders(...args),
  getModels: (...args: unknown[]) => mockGetModels(...args),
  downloadBase64Image: (...args: unknown[]) => mockDownloadBase64Image(...args),
  downloadBlob: (...args: unknown[]) => mockDownloadBlob(...args),
}));

// ==================== Test Setup ====================

const renderWithProvider = (ui: React.ReactElement) => {
  return render(<I18nProvider>{ui}</I18nProvider>);
};

const setupMocks = () => {
  mockGetVoices.mockResolvedValue(mockVoices);
  mockGetProviders.mockResolvedValue(mockProviders);
  mockGetModels.mockResolvedValue(mockModels);
  mockGenerateImage.mockResolvedValue({ images: [] });
  mockSynthesizeSpeech.mockResolvedValue(new Blob(['audio'], { type: 'audio/mp3' }));
  mockChatStream.mockResolvedValue(undefined);
};

// ==================== Test Suites ====================

describe('AIHub Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // ==================== 1. Basic Rendering Tests ====================

  describe('Basic Rendering', () => {
    it('should render without crashing', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByText('Chat')).toBeInTheDocument();
    });

    it('should render with correct container structure', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('should render all three tabs', () => {
      renderWithProvider(<AIHub />);
      const tabs = screen.getAllByRole('tab');
      expect(tabs).toHaveLength(3);
    });

    it('should have Chat as default active tab', () => {
      renderWithProvider(<AIHub />);
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      expect(chatTab).toHaveAttribute('aria-selected', 'true');
    });
  });

  // ==================== 2. Tab Navigation Tests ====================

  describe('Tab Navigation', () => {
    it('should switch to Image Gen tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /image/i }));

      expect(screen.getByRole('tab', { name: /image/i })).toHaveAttribute('aria-selected', 'true');
      expect(screen.getByText('Image Generation')).toBeInTheDocument();
    });

    it('should switch to Text to Speech tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      expect(screen.getByRole('tab', { name: /speech/i })).toHaveAttribute('aria-selected', 'true');
      // Panel content is visible
      expect(screen.getByText(/Convert text to natural speech/i)).toBeInTheDocument();
    });

    it('should switch back to Chat tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      // First go to Image tab
      await user.click(screen.getByRole('tab', { name: /image/i }));
      expect(screen.getByRole('tab', { name: /chat/i })).toHaveAttribute('aria-selected', 'false');

      // Then go back to Chat tab
      await user.click(screen.getByRole('tab', { name: /chat/i }));
      expect(screen.getByRole('tab', { name: /chat/i })).toHaveAttribute('aria-selected', 'true');
    });
  });

  // ==================== 3. Chat Tab Tests ====================

  describe('Chat Tab', () => {
    it('should render chat title and description', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByText('Conversational AI')).toBeInTheDocument();
      expect(screen.getByText(/Chat with AI powered by GPT-4o/i)).toBeInTheDocument();
    });

    it('should render empty state when no messages', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByText('Start a conversation with the AI...')).toBeInTheDocument();
      expect(screen.getByText('Choose a prompt below to get started')).toBeInTheDocument();
    });

    it('should render quick action buttons', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByText('Hello! How can you help me?')).toBeInTheDocument();
      expect(screen.getByText('What can you do?')).toBeInTheDocument();
      expect(screen.getByText('Write a short poem about nature')).toBeInTheDocument();
    });

    it('should render input textarea', () => {
      renderWithProvider(<AIHub />);
      const input = screen.getByPlaceholderText('Type your message...');
      expect(input).toBeInTheDocument();
      expect(input.tagName).toBe('TEXTAREA');
    });

    it('should render send button', () => {
      renderWithProvider(<AIHub />);
      const sendButton = screen.getByRole('button', { name: /→/ });
      expect(sendButton).toBeInTheDocument();
    });

    it('should render provider selector', async () => {
      renderWithProvider(<AIHub />);
      await waitFor(() => {
        expect(screen.getByText('Provider:')).toBeInTheDocument();
        expect(screen.getByText('OpenAI')).toBeInTheDocument();
      });
    });

    it('should disable send button when input is empty', () => {
      renderWithProvider(<AIHub />);
      const sendButton = screen.getByRole('button', { name: /→/ });
      expect(sendButton).toBeDisabled();
    });

    it('should enable send button when input has text', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      const input = screen.getByPlaceholderText('Type your message...');
      await user.type(input, 'Hello AI');

      const sendButton = screen.getByRole('button', { name: /→/ });
      expect(sendButton).not.toBeDisabled();
    });

    it('should update input value when typing', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      const input = screen.getByPlaceholderText('Type your message...');
      await user.type(input, 'Test message');

      expect(input).toHaveValue('Test message');
    });

    it('should not send empty message', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      const sendButton = screen.getByRole('button', { name: /→/ });
      await user.click(sendButton);

      expect(mockChatStream).not.toHaveBeenCalled();
    });

    it('should set quick prompt to input when clicked', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      const quickPrompt = screen.getByText('Hello! How can you help me?');
      await user.click(quickPrompt);

      const input = screen.getByPlaceholderText('Type your message...');
      expect(input).toHaveValue('Hello! How can you help me?');
    });
  });

  // ==================== 4. Image Generation Tab Tests ====================

  describe('Image Generation Tab', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);
      await user.click(screen.getByRole('tab', { name: /image/i }));
    });

    it('should render image generation title and description', () => {
      expect(screen.getByText('Image Generation')).toBeInTheDocument();
      expect(screen.getByText(/Create images using Stable Diffusion XL/i)).toBeInTheDocument();
    });

    it('should render prompt textarea', () => {
      const promptInput = screen.getByPlaceholderText('Describe the image you want to generate...');
      expect(promptInput).toBeInTheDocument();
      expect(promptInput.tagName).toBe('TEXTAREA');
    });

    it('should render negative prompt textarea', () => {
      const negativePromptInput = screen.getByPlaceholderText('What to avoid in the image...');
      expect(negativePromptInput).toBeInTheDocument();
    });

    it('should render image size selector with all options', () => {
      expect(screen.getByText('Image Size')).toBeInTheDocument();
      expect(screen.getByText('512x512')).toBeInTheDocument();
      expect(screen.getByText('768x768')).toBeInTheDocument();
      expect(screen.getByText('1024x1024')).toBeInTheDocument();
    });

    it('should render generate button', () => {
      const generateButton = screen.getByText('Generate Image');
      expect(generateButton).toBeInTheDocument();
    });

    it('should disable generate button when prompt is empty', () => {
      const generateButton = screen.getByText('Generate Image');
      expect(generateButton).toBeDisabled();
    });

    it('should enable generate button when prompt has text', async () => {
      const user = userEvent.setup();

      const promptInput = screen.getByPlaceholderText('Describe the image you want to generate...');
      await user.type(promptInput, 'A beautiful sunset');

      const generateButton = screen.getByText('Generate Image');
      expect(generateButton).not.toBeDisabled();
    });

    it('should update prompt input value', async () => {
      const user = userEvent.setup();

      const promptInput = screen.getByPlaceholderText('Describe the image you want to generate...');
      await user.type(promptInput, 'A cat sitting on a chair');

      expect(promptInput).toHaveValue('A cat sitting on a chair');
    });

    it('should update negative prompt input value', async () => {
      const user = userEvent.setup();

      const negativePromptInput = screen.getByPlaceholderText('What to avoid in the image...');
      await user.type(negativePromptInput, 'blurry, low quality');

      expect(negativePromptInput).toHaveValue('blurry, low quality');
    });

    it('should call generateImage when generate button clicked', async () => {
      const user = userEvent.setup();

      const promptInput = screen.getByPlaceholderText('Describe the image you want to generate...');
      await user.type(promptInput, 'A beautiful landscape');

      const generateButton = screen.getByText('Generate Image');
      await user.click(generateButton);

      await waitFor(() => {
        expect(mockGenerateImage).toHaveBeenCalledWith(
          expect.objectContaining({
            prompt: 'A beautiful landscape',
            width: 1024,
            height: 1024,
            num_images: 1,
          })
        );
      });
    });

    it('should render empty state when no image generated', () => {
      expect(screen.getByText('Generate an image to see preview')).toBeInTheDocument();
    });
  });

  // ==================== 5. TTS Tab Tests ====================

  describe('Text to Speech Tab', () => {
    it('should render TTS panel elements', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      // Switch to TTS tab
      await user.click(screen.getByRole('tab', { name: /speech/i }));

      await waitFor(() => {
        // Check that the TTS panel description exists
        expect(screen.getByText(/Convert text to natural speech/i)).toBeInTheDocument();
      });
    });

    it('should render text input textarea', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
      expect(textInput).toBeInTheDocument();
      expect(textInput.tagName).toBe('TEXTAREA');
    });

    it('should render voice selector', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      await waitFor(() => {
        expect(screen.getByText('Voice')).toBeInTheDocument();
      });
    });

    it('should render speed slider', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      await waitFor(() => {
        expect(screen.getByText(/Speed: 1\.0x/)).toBeInTheDocument();
      });
    });

    it('should render synthesize button', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const synthesizeButton = screen.getByText('Synthesize');
      expect(synthesizeButton).toBeInTheDocument();
    });

    it('should disable synthesize button when text is empty', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const synthesizeButton = screen.getByText('Synthesize');
      expect(synthesizeButton).toBeDisabled();
    });

    it('should enable synthesize button when text has content', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
      await user.type(textInput, 'Hello world');

      const synthesizeButton = screen.getByText('Synthesize');
      expect(synthesizeButton).not.toBeDisabled();
    });

    it('should update text input value', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
      await user.type(textInput, 'This is a test');

      expect(textInput).toHaveValue('This is a test');
    });

    it('should call synthesizeSpeech when synthesize clicked', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
      await user.type(textInput, 'Hello world');

      const synthesizeButton = screen.getByText('Synthesize');
      await user.click(synthesizeButton);

      await waitFor(() => {
        expect(mockSynthesizeSpeech).toHaveBeenCalledWith(
          expect.objectContaining({
            text: 'Hello world',
            speed: 1,
            output_format: 'mp3',
          })
        );
      });
    });

    it('should display audio player when synthesis completes', async () => {
      mockSynthesizeSpeech.mockResolvedValue(new Blob(['audio'], { type: 'audio/mp3' }));

      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      await user.click(screen.getByRole('tab', { name: /speech/i }));

      const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
      await user.type(textInput, 'Hello world');

      const synthesizeButton = screen.getByText('Synthesize');
      await user.click(synthesizeButton);

      await waitFor(() => {
        expect(screen.getByText('Audio ready')).toBeInTheDocument();
      });
    });
  });

  // ==================== 6. Model Selector Tests ====================

  describe('Model Selector', () => {
    it('should load providers on mount', async () => {
      renderWithProvider(<AIHub />);

      await waitFor(() => {
        expect(mockGetProviders).toHaveBeenCalled();
      });
    });

    it('should display current model badge', async () => {
      renderWithProvider(<AIHub />);

      await waitFor(() => {
        expect(screen.getByText(/openai\//i)).toBeInTheDocument();
      });
    });

    it('should load voices on component mount', async () => {
      renderWithProvider(<AIHub />);
      await waitFor(() => {
        expect(mockGetVoices).toHaveBeenCalled();
      });
    });
  });

  // ==================== 7. Error Handling Tests ====================

  describe('Error Handling', () => {
    describe('Image Generation Errors', () => {
      it('should display error message when image generation fails', async () => {
        const user = userEvent.setup();
        mockGenerateImage.mockRejectedValue(new Error('Image generation failed'));

        renderWithProvider(<AIHub />);
        await user.click(screen.getByRole('tab', { name: /image/i }));

        const promptInput = screen.getByPlaceholderText('Describe the image you want to generate...');
        await user.type(promptInput, 'A cat');

        const generateButton = screen.getByText('Generate Image');
        await user.click(generateButton);

        await waitFor(() => {
          expect(screen.getByText('Image generation failed')).toBeInTheDocument();
        });
      });
    });

    describe('TTS Errors', () => {
      it('should display error message when TTS fails', async () => {
        const user = userEvent.setup();
        mockSynthesizeSpeech.mockRejectedValue(new Error('Synthesis failed'));

        renderWithProvider(<AIHub />);
        await user.click(screen.getByRole('tab', { name: /speech/i }));

        const textInput = screen.getByPlaceholderText('Enter text to convert to speech...');
        await user.type(textInput, 'Hello');

        const synthesizeButton = screen.getByText('Synthesize');
        await user.click(synthesizeButton);

        await waitFor(() => {
          expect(screen.getByText('Synthesis failed')).toBeInTheDocument();
        });
      });
    });
  });

  // ==================== 8. Accessibility Tests ====================

  describe('Accessibility', () => {
    it('should have proper tab roles', () => {
      renderWithProvider(<AIHub />);
      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('aria-selected');
      });
    });

    it('should have tablist with tabs', () => {
      renderWithProvider(<AIHub />);
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('should have textareas for text input', () => {
      renderWithProvider(<AIHub />);
      const textareas = screen.getAllByRole('textbox');
      expect(textareas.length).toBeGreaterThan(0);
    });

    it('should have buttons for actions', () => {
      renderWithProvider(<AIHub />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  // ==================== 9. Integration Tests ====================

  describe('Integration Tests', () => {
    it('should maintain state across tab switches', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      // Type in chat input
      const chatInput = screen.getByPlaceholderText('Type your message...');
      await user.type(chatInput, 'Hello AI');

      // Switch to Image tab
      await user.click(screen.getByRole('tab', { name: /image/i }));

      // Switch back to Chat tab
      await user.click(screen.getByRole('tab', { name: /chat/i }));

      // Input should still have the value
      expect(chatInput).toHaveValue('Hello AI');
    });

    it('should handle multiple quick prompt clicks', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      // Click first quick prompt
      await user.click(screen.getByText('Hello! How can you help me?'));

      const chatInput = screen.getByPlaceholderText('Type your message...');
      expect(chatInput).toHaveValue('Hello! How can you help me?');

      // Clear and click another
      await user.clear(chatInput);
      await user.click(screen.getByText('What can you do?'));

      expect(chatInput).toHaveValue('What can you do?');
    });
  });

  // ==================== 10. Edge Cases ====================

  describe('Edge Cases', () => {
    it('should handle text input', async () => {
      const user = userEvent.setup();
      renderWithProvider(<AIHub />);

      const input = screen.getByPlaceholderText('Type your message...');
      await user.type(input, 'Hello World');

      expect(input).toHaveValue('Hello World');
    });

    it('should handle empty providers list gracefully', async () => {
      mockGetProviders.mockResolvedValue([]);

      renderWithProvider(<AIHub />);

      await waitFor(() => {
        expect(screen.getByText('Conversational AI')).toBeInTheDocument();
      });
    });

    it('should handle empty voices list gracefully', async () => {
      mockGetVoices.mockResolvedValue([]);

      renderWithProvider(<AIHub />);

      // Switch to TTS tab
      const user = userEvent.setup();
      await user.click(screen.getByRole('tab', { name: /speech/i }));

      await waitFor(() => {
        expect(screen.getByText('English (US)')).toBeInTheDocument();
      });
    });

    it('should handle API failures gracefully', async () => {
      mockGetProviders.mockRejectedValue(new Error('API Error'));
      mockGetVoices.mockRejectedValue(new Error('API Error'));

      // Should not throw
      expect(() => {
        renderWithProvider(<AIHub />);
      }).not.toThrow();
    });
  });
});
