import { useState, useRef, useEffect } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { GlobalStyles } from './GlobalStyles';
import { ImageUploader } from './components/ImageUploader';
import { RAGChat } from './components/RAGChat';
import { I18nProvider, useI18n, Language, languageNames } from './i18n';
import { colors, spacing, typography, radius } from './theme';

type Tab = 'vision' | 'rag';

const AppContainer = styled.div`
  min-height: 100vh;
  background: ${colors.background};
`;

const NavBar = styled.nav`
  position: sticky;
  top: 0;
  z-index: 100;
  height: 52px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid ${colors.border};
  display: flex;
  align-items: center;
  padding: 0 ${spacing.xl};
`;

const NavContent = styled.div`
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  font-size: ${typography.fontSize.lg};
  font-weight: ${typography.fontWeight.semibold};
  color: ${colors.text};
`;

const NavTabs = styled.div`
  display: flex;
  gap: 2px;
`;

const NavTab = styled.button<{ active: boolean }>`
  padding: 8px 16px;
  font-size: ${typography.fontSize.base};
  font-weight: ${typography.fontWeight.medium};
  font-family: ${typography.fontFamily.body};
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  color: ${props => props.active ? colors.primary : colors.textSecondary};
  background: transparent;

  &:hover {
    color: ${colors.text};
  }
`;

const LanguageSelector = styled.div`
  position: relative;
  display: flex;
  justify-content: flex-end;
`;

const LanguageButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: ${typography.fontSize.sm};
  font-family: ${typography.fontFamily.body};
  color: ${colors.textSecondary};
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  border-radius: ${radius.sm};

  &:hover {
    color: ${colors.text};
  }
`;

const ChevronIcon = styled.span<{ open: boolean }>`
  display: inline-block;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid currentColor;
  transform: rotate(${props => props.open ? '180deg' : '0deg'});
  transition: transform 0.2s ease;
`;

const Dropdown = styled.div<{ open: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  min-width: 140px;
  background: ${colors.surface};
  border: 1px solid ${colors.border};
  border-radius: ${radius.md};
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  opacity: ${props => props.open ? 1 : 0};
  visibility: ${props => props.open ? 'visible' : 'hidden'};
  transform: translateY(${props => props.open ? 0 : '-8px'});
  transition: all 0.2s ease;
  z-index: 200;
`;

const DropdownItem = styled.button<{ active: boolean }>`
  width: 100%;
  padding: 10px 16px;
  font-size: ${typography.fontSize.sm};
  font-family: ${typography.fontFamily.body};
  text-align: left;
  color: ${props => props.active ? colors.primary : colors.text};
  background: ${props => props.active ? colors.primaryLight : 'transparent'};
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: ${props => props.active ? colors.primaryLight : colors.surfaceSecondary};
  }
`;

const Main = styled.main`
  padding: ${spacing.xl};
`;

const ContentWrapper = styled.div`
  max-width: 680px;
  margin: 0 auto;
`;

const languages: Language[] = ['en', 'zh', 'ja', 'fr', 'es'];

function AppContent() {
  const [activeTab, setActiveTab] = useState<Tab>('vision');
  const [langOpen, setLangOpen] = useState(false);
  const { language, setLanguage, t } = useI18n();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setLangOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <AppContainer>
      <NavBar>
        <NavContent>
          <Logo>AI Vision</Logo>
          <NavTabs>
            <NavTab
              active={activeTab === 'vision'}
              onClick={() => setActiveTab('vision')}
            >
              {t.nav.visionAI}
            </NavTab>
            <NavTab
              active={activeTab === 'rag'}
              onClick={() => setActiveTab('rag')}
            >
              {t.nav.documentQA}
            </NavTab>
          </NavTabs>
          <LanguageSelector ref={dropdownRef}>
            <LanguageButton onClick={() => setLangOpen(!langOpen)}>
              {languageNames[language]}
              <ChevronIcon open={langOpen} />
            </LanguageButton>
            <Dropdown open={langOpen}>
              {languages.map((lang) => (
                <DropdownItem
                  key={lang}
                  active={lang === language}
                  onClick={() => {
                    setLanguage(lang);
                    setLangOpen(false);
                  }}
                >
                  {languageNames[lang]}
                </DropdownItem>
              ))}
            </Dropdown>
          </LanguageSelector>
        </NavContent>
      </NavBar>
      <Main>
        <ContentWrapper>
          {activeTab === 'vision' ? <ImageUploader /> : <RAGChat />}
        </ContentWrapper>
      </Main>
    </AppContainer>
  );
}

export default function App() {
  return (
    <>
      <GlobalStyles />
      <I18nProvider>
        <AppContent />
      </I18nProvider>
    </>
  );
}
