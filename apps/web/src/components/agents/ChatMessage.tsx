import { css, keyframes } from '@emotion/react';
import styled from '@emotion/styled';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useState } from 'react';
import { colors, radius, spacing, typography } from '../../theme';
import { ToolResult } from './ToolResult';
import { ImageZoomModal } from '../ImageZoomModal';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  display: flex;
  flex-direction: column;
  max-width: 80%;
  animation: ${fadeIn} 0.2s ease;
  align-self: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
  align-items: ${({ isUser }) => (isUser ? 'flex-end' : 'flex-start')};
`;

const MessageContent = styled.div<{ isUser: boolean }>`
  padding: ${spacing.md};
  border-radius: ${radius.lg};
  font-size: ${typography.fontSize.base};
  line-height: ${typography.lineHeight.relaxed};
  word-break: break-word;

  ${({ isUser }) =>
    isUser
      ? css`
          background: ${colors.primary};
          color: white;
          border-bottom-right-radius: ${radius.sm};
        `
      : css`
          background: ${colors.surface};
          border: 1px solid ${colors.border};
          border-bottom-left-radius: ${radius.sm};
          color: ${colors.text};
        `}

  h1, h2, h3, h4, h5, h6 {
    margin: 0.5em 0 0.25em;
    font-weight: 600;
    line-height: 1.3;
  }
  h1:first-of-type, h2:first-of-type, h3:first-of-type, h4:first-of-type, h5:first-of-type, h6:first-of-type {
    margin-top: 0;
  }
  h1:last-of-type, h2:last-of-type, h3:last-of-type, h4:last-of-type, h5:last-of-type, h6:last-of-type {
    margin-bottom: 0;
  }
  h1 { font-size: 1.2em; }
  h2 { font-size: 1.1em; }
  h3 { font-size: 1.05em; }

  p { margin: 0.5em 0; }
  p:first-of-type { margin-top: 0; }
  p:last-of-type { margin-bottom: 0; }
  ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
  li { margin: 0.25em 0; }

  code {
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    font-size: 0.9em;
    padding: 0.15em 0.4em;
    border-radius: 3px;
    background: ${colors.surfaceSecondary};
  }
  pre {
    margin: 0.5em 0;
    padding: ${spacing.sm};
    border-radius: ${radius.sm};
    background: ${colors.background};
    overflow-x: auto;
    code { padding: 0; background: none; }
  }

  blockquote {
    margin: 0.5em 0;
    padding-left: 1em;
    border-left: 3px solid ${colors.primary}50;
    color: ${colors.textSecondary};
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5em 0;
    font-size: 0.9em;
  }
  th, td {
    border: 1px solid ${colors.border};
    padding: 0.5em;
    text-align: left;
  }
  th { background: ${colors.surfaceSecondary}; font-weight: 600; }

  strong { font-weight: 600; }

  .hljs { background: ${colors.background}; color: ${colors.text}; }
  .hljs-keyword, .hljs-selector-tag { color: #7c3aed; }
  .hljs-string, .hljs-attr { color: #059669; }
  .hljs-number { color: #dc2626; }
  .hljs-comment { color: ${colors.textTertiary}; font-style: italic; }
  .hljs-function, .hljs-title { color: #2563eb; }
  .hljs-variable, .hljs-params { color: #ea580c; }
`;

// Extract code blocks and inline content from raw text
function extractContentBlocks(content: string): Array<{ type: 'text' | 'json' | 'code'; content: string }> {
  // Check if content is primarily JSON
  const trimmedContent = content.trim();
  const isJsonDominated = trimmedContent.startsWith('[') || trimmedContent.startsWith('{');

  if (isJsonDominated) {
    // Try to format as pretty JSON
    try {
      const parsed = JSON.parse(trimmedContent);
      return [{
        type: 'json' as const,
        content: JSON.stringify(parsed, null, 2)
      }];
    } catch {
      // Not valid JSON, treat as regular content
    }
  }

  // Split by code blocks while preserving markdown formatting
  const parts = trimmedContent.split(/(```[\s\S]*?```)/);

  const blocks: Array<{ type: 'text' | 'json' | 'code'; content: string }> = [];
  for (const part of parts) {
    const trimmed = part.trim();
    if (!trimmed) continue;

    if (trimmed.startsWith('```')) {
      // Extract code content without the backticks
      const codeContent = trimmed.replace(/^```[a-z]*\n?/, '').replace(/\n?```$/, '');
      blocks.push({ type: 'code', content: codeContent });
    } else {
      blocks.push({ type: 'text', content: trimmed });
    }
  }

  return blocks.length > 0 ? blocks : [{ type: 'text', content: content }];
}

const InlineCodeBlock = styled.div`
  background: ${colors.background};
  border: 1px solid ${colors.border};
  border-radius: ${radius.sm};
  padding: ${spacing.md};
  margin: 0.5em 0;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: ${typography.fontSize.sm};
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: ${colors.text};
`;

const JsonKey = styled.span`
  color: #7c3aed;
`;

const JsonString = styled.span`
  color: #059669;
`;

const JsonNumber = styled.span`
  color: #dc2626;
`;

const JsonBoolean = styled.span`
  color: #2563eb;
`;

const JsonNull = styled.span`
  color: ${colors.textTertiary};
`;

const JsonBracket = styled.span`
  color: ${colors.textSecondary};
`;

const QueryBlock = styled.div`
  margin: 0.75em 0;
  border-radius: ${radius.md};
  overflow: hidden;
  border: 1px solid ${colors.border};
  background: ${colors.background};
`;

const QueryLabel = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.xs};
  padding: ${spacing.xs} ${spacing.md};
  background: ${colors.surfaceSecondary};
  font-size: ${typography.fontSize.xs};
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid ${colors.border};

  &::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${colors.primary};
  }
`;

const QueryBlockPre = styled.pre`
  margin: 0;
  padding: ${spacing.md};
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: ${typography.fontSize.sm};
  line-height: 1.6;
  color: ${colors.text};
  overflow-x: auto;
  white-space: pre;
`;

const ZoomableImage = styled.img`
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: ${radius.sm};
  cursor: zoom-in;
  transition: transform 0.2s ease;
  margin: 0.5em 0;

  &:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

// Syntax highlight JSON for display
function highlightJson(json: string): React.ReactNode {
  return json.split(/("(?:[^"\\]|\\.)*"|true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}\[\],:])/g).map((part, i) => {
    if (part.startsWith('"') && part.endsWith('"')) {
      const keyMatch = /"([^"]+)":?$/.exec(part);
      if (keyMatch && json[json.indexOf(part) + part.length] === ':') {
        return <JsonKey key={i}>{part}</JsonKey>;
      }
      return <JsonString key={i}>{part}</JsonString>;
    }
    if (part === 'true' || part === 'false') {
      return <JsonBoolean key={i}>{part}</JsonBoolean>;
    }
    if (part === 'null') {
      return <JsonNull key={i}>{part}</JsonNull>;
    }
    if (/^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$/.test(part)) {
      return <JsonNumber key={i}>{part}</JsonNumber>;
    }
    if (/^[{}\[\],:]$/.test(part)) {
      return <JsonBracket key={i}>{part}</JsonBracket>;
    }
    return part;
  });
}

const MessageMeta = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  margin-top: 4px;
  padding: 0 4px;
`;

const MessageTime = styled.span`
  font-size: ${typography.fontSize.xs};
  color: ${colors.textTertiary};
`;

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
  output?: string;
  status: 'pending' | 'running' | 'success' | 'error';
}

export interface ChatMessageData {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  toolCalls?: ToolCall[];
}

interface ChatMessageProps {
  message: ChatMessageData;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const content = message.content;
  const [zoomedImage, setZoomedImage] = useState<{ src: string; alt?: string } | null>(null);

  // Detect query patterns (PromQL, SQL, etc.) that should be displayed as formatted blocks
  const detectQueryBlocks = (text: string): Array<{ type: 'query'; content: string } | { type: 'text'; content: string }> => {
    const blocks: Array<{ type: 'query'; content: string } | { type: 'text'; content: string }> = [];
    const lines = text.split('\n');
    const inBlock = { active: false, type: '', content: [] as string[], startLine: 0 };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Start of a query block - various query patterns
      const isQueryStart = /^(sum\(|count\(|rate\(|increase\(|avg\(|max\(|min\(|stddev\(|SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|PROMQL:|SQL:|QUERY:|query\s+)/i.test(trimmed) ||
        /^\{[^}]+\}=/.test(trimmed) ||
        /^(up|node_memory|process_cpu|kube_|container_)/.test(trimmed);

      // Continuation of query (indented or operator continuation)
      const isQueryContinuation = /^\s*(\+\s*|\-\s*|\*\s*|\/\s*|,|\)|\bor\b|\band\b)/.test(trimmed) ||
        /^\s{2,}[\w_]/.test(line) ||
        /^\s*\}\s*,\s*\{/.test(trimmed);

      if (isQueryStart && !inBlock.active) {
        // Save previous text block
        if (inBlock.content.length > 0) {
          blocks.push({ type: 'text', content: inBlock.content.join('\n') });
          inBlock.content = [];
        }
        inBlock.active = true;
        inBlock.type = 'query';
        inBlock.content.push(line);
        inBlock.startLine = i;
      } else if (inBlock.active) {
        // Check if query continues
        if (trimmed === '' || isQueryContinuation || /^\s*[\w_"{:.]/.test(trimmed)) {
          inBlock.content.push(line);
        } else {
          blocks.push({ type: 'query', content: inBlock.content.join('\n') });
          inBlock.content = [line];
          inBlock.active = trimmed !== '' && (
            isQueryStart ||
            /^[a-zA-Z]/.test(trimmed) ||
            /^\d/.test(trimmed)
          );
          inBlock.type = inBlock.active ? 'query' : '';
        }
      } else if (trimmed !== '') {
        blocks.push({ type: 'text', content: trimmed });
      }
    }

    if (inBlock.content.length > 0) {
      if (inBlock.active && inBlock.type === 'query') {
        blocks.push({ type: 'query', content: inBlock.content.join('\n') });
      } else {
        blocks.push({ type: 'text', content: inBlock.content.join('\n') });
      }
    }

    return blocks;
  };

  const isQueryContent = (text: string): boolean => {
    const queryPatterns = [
      /PROMQL:/i,
      /SQL:/i,
      /\b(sum|count|rate|increase|avg|max|min|stddev)\s*\(/i,
      /\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b/i,
      /\{[^}]*}=/,
      /^(up|node_memory|process_cpu|kube_|container_)/m,
    ];
    return queryPatterns.some(p => p.test(text));
  };

  // Custom components for ReactMarkdown
  const components = {
    img: ({ src, alt }: { src?: string; alt?: string }) => (
      <ZoomableImage
        src={src || ''}
        alt={alt}
        onClick={() => src && setZoomedImage({ src, alt })}
      />
    ),
  };

  const renderAssistantContent = () => {
    if (!content) return null;

    const trimmed = content.trim();
    const isRawJson = (trimmed.startsWith('[') || trimmed.startsWith('{')) &&
                      !trimmed.startsWith('```') &&
                      !trimmed.startsWith('#');

    if (isRawJson) {
      try {
        const parsed = JSON.parse(trimmed);
        return (
          <InlineCodeBlock>
            {highlightJson(JSON.stringify(parsed, null, 2))}
          </InlineCodeBlock>
        );
      } catch {
        // Not valid JSON, fall through to markdown
      }
    }

    const hasCodeBlocks = content.includes('```');
    const hasQueryContent = isQueryContent(content);

    // For content with PromQL/SQL queries but no markdown code blocks
    if (hasQueryContent && !hasCodeBlocks) {
      const blocks = detectQueryBlocks(content);
      return (
        <>
          {blocks.map((block, index) => {
            if (block.type === 'query') {
              return (
                <QueryBlock key={index}>
                  <QueryLabel>Query</QueryLabel>
                  <QueryBlockPre>{block.content}</QueryBlockPre>
                </QueryBlock>
              );
            }
            return (
              <ReactMarkdown
                key={index}
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={components}
              >
                {block.content}
              </ReactMarkdown>
            );
          })}
        </>
      );
    }

    if (hasCodeBlocks) {
      const blocks = extractContentBlocks(content);
      return (
        <>
          {blocks.map((block, index) => {
            if (block.type === 'code') {
              // Detect query in code block
              const isQuery = isQueryContent(block.content);
              return isQuery ? (
                <QueryBlock key={index}>
                  <QueryLabel>Query</QueryLabel>
                  <pre>{block.content}</pre>
                </QueryBlock>
              ) : (
                <InlineCodeBlock key={index}>
                  {block.content}
                </InlineCodeBlock>
              );
            }
            return (
              <ReactMarkdown
                key={index}
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={components}
              >
                {block.content}
              </ReactMarkdown>
            );
          })}
        </>
      );
    }

    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <MessageBubble
      isUser={isUser}
    >
      <MessageContent isUser={isUser}>
        {isUser ? content : renderAssistantContent()}
      </MessageContent>

      {message.toolCalls && message.toolCalls.length > 0 && (
        <div style={{ marginTop: spacing.sm, width: '100%', maxWidth: '500px' }}>
          {message.toolCalls.map((toolCall) => (
            <ToolResult
              key={toolCall.id}
              toolCall={toolCall}
            />
          ))}
        </div>
      )}

      <MessageMeta>
        <MessageTime>
          {new Date(message.timestamp).toLocaleTimeString()}
        </MessageTime>
      </MessageMeta>

      {zoomedImage && (
        <ImageZoomModal
          src={zoomedImage.src}
          alt={zoomedImage.alt}
          onClose={() => setZoomedImage(null)}
        />
      )}
    </MessageBubble>
  );
}
