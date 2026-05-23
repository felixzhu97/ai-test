import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nProvider, useI18n, languageNames, languageFlags } from '../index';

// Simple mock - assign directly to global
beforeEach(() => {
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn().mockReturnValue(null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    },
    writable: true,
  });
  Object.defineProperty(window, 'navigator', {
    value: { ...window.navigator, language: 'zh-CN' },
    writable: true,
  });
});

function TestComponent() {
  const { language, setLanguage, t } = useI18n();
  return (
    <div>
      <span data-testid="language">{language}</span>
      <span data-testid="title">{t.aiHub.title}</span>
      <button onClick={() => setLanguage('en')}>Switch to English</button>
    </div>
  );
}

describe('I18nProvider', () => {
  afterEach(() => {
    cleanup();
  });

  describe('initialization', () => {
    it('should initialize with zh when no stored language', () => {
      render(
        <I18nProvider>
          <TestComponent />
        </I18nProvider>
      );
      expect(screen.getByTestId('language')).toHaveTextContent('zh');
    });

    it('should use stored language from localStorage', () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn().mockReturnValue('ja'),
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn(),
        },
        writable: true,
      });
      render(
        <I18nProvider>
          <TestComponent />
        </I18nProvider>
      );
      expect(screen.getByTestId('language')).toHaveTextContent('ja');
    });
  });

  describe('setLanguage', () => {
    it('should update language state', async () => {
      const user = userEvent.setup();
      render(
        <I18nProvider>
          <TestComponent />
        </I18nProvider>
      );
      await user.click(screen.getByText('Switch to English'));
      expect(screen.getByTestId('language')).toHaveTextContent('en');
    });

    it('should store language in localStorage', async () => {
      const user = userEvent.setup();
      render(
        <I18nProvider>
          <TestComponent />
        </I18nProvider>
      );
      await user.click(screen.getByText('Switch to English'));
      expect(window.localStorage.setItem).toHaveBeenCalledWith('language', 'en');
    });
  });

  describe('translations', () => {
    it('should render translation', () => {
      render(
        <I18nProvider>
          <TestComponent />
        </I18nProvider>
      );
      expect(screen.getByTestId('title')).toHaveTextContent('AI Hub');
    });
  });

  describe('tReplace', () => {
    function TestReplaceComponent() {
      const { tReplace } = useI18n();
      const result = tReplace('Hello {name}', { name: 'John' });
      return <span data-testid="replaced">{result}</span>;
    }

    it('should replace template placeholders with values', () => {
      render(
        <I18nProvider>
          <TestReplaceComponent />
        </I18nProvider>
      );
      expect(screen.getByTestId('replaced')).toHaveTextContent('Hello John');
    });
  });

  describe('languageNames', () => {
    it('should export language names', () => {
      expect(languageNames.en).toBe('English');
      expect(languageNames.zh).toBe('中文');
      expect(languageNames.ja).toBe('日本語');
    });
  });

  describe('languageFlags', () => {
    it('should export language flags', () => {
      expect(languageFlags.en).toBe('🇺🇸');
      expect(languageFlags.zh).toBe('🇨🇳');
      expect(languageFlags.ja).toBe('🇯🇵');
    });
  });
});
