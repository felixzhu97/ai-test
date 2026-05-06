import { Global, css } from '@emotion/react';
import { colors, typography, transitions } from './theme';

const globalStyles = css`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    scroll-behavior: smooth;
  }

  body {
    font-family: ${typography.fontFamily.body};
    font-size: ${typography.fontSize.base};
    color: ${colors.text};
    background: ${colors.background};
    line-height: ${typography.lineHeight.normal};
    min-height: 100vh;
  }

  ::selection {
    background: ${colors.primaryLight};
    color: ${colors.primary};
  }

  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: transparent;
  }

  ::-webkit-scrollbar-thumb {
    background: ${colors.border};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${colors.textTertiary};
  }

  input, button, textarea, select {
    font-family: inherit;
    font-size: inherit;
  }

  button {
    cursor: pointer;
    border: none;
    background: none;
  }

  a {
    color: ${colors.primary};
    text-decoration: none;
    transition: color ${transitions.fast};

    &:hover {
      color: ${colors.primaryHover};
    }
  }

  img {
    max-width: 100%;
    height: auto;
    display: block;
  }

  code {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    font-size: 0.9em;
    background: ${colors.primaryLight};
    color: ${colors.primary};
    padding: 2px 6px;
    border-radius: 4px;
  }

  pre {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    overflow-x: auto;
  }
`;

export function GlobalStyles() {
  return <Global styles={globalStyles} />;
}
