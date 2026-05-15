import { useState } from 'react';
import styled from '@emotion/styled';
import { css, keyframes } from '@emotion/react';
import { colors, radius, spacing, typography } from '../../theme';
import { ToolCall } from './ChatMessage';
import { ImageZoomModal } from '../ImageZoomModal';

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const ToolContainer = styled.div`
  background: ${colors.surfaceSecondary};
  border: 1px solid ${colors.border};
  border-radius: ${radius.md};
  overflow: hidden;
  font-size: ${typography.fontSize.sm};
`;

const ToolHeader = styled.div<{ status: ToolCall['status'] }>`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.sm} ${spacing.md};
  background: ${({ status }) => {
    switch (status) {
      case 'error': return colors.errorLight;
      case 'success': return colors.successLight;
      default: return colors.surface;
    }
  }};
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: ${({ status }) => {
      switch (status) {
        case 'error': return colors.errorLight;
        case 'success': return colors.successLight;
        default: return colors.surfaceTertiary;
      }
    }};
  }
`;

const ToolIcon = styled.span`
  font-size: 14px;
`;

const ToolName = styled.span`
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.text};
  flex: 1;
`;

const StatusIndicator = styled.span<{ status: ToolCall['status'] }>`
  ${({ status }) => {
    switch (status) {
      case 'pending':
        return css`color: ${colors.textTertiary};`;
      case 'running':
        return css`
          color: ${colors.warning};
          animation: ${pulse} 1s ease-in-out infinite;
        `;
      case 'success':
        return css`color: ${colors.success};`;
      case 'error':
        return css`color: ${colors.error};`;
    }
  }}
`;

const SpinnerIcon = styled.span`
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: ${spin} 0.6s linear infinite;
`;

const ExpandIcon = styled.span<{ expanded: boolean }>`
  display: inline-block;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid ${colors.textTertiary};
  transform: rotate(${({ expanded }) => expanded ? '180deg' : '0deg'});
  transition: transform 0.2s ease;
`;

const ToolBody = styled.div<{ expanded: boolean }>`
  display: ${({ expanded }) => expanded ? 'block' : 'none'};
  padding: ${spacing.md};
  border-top: 1px solid ${colors.border};
  max-height: 300px;
  overflow-y: auto;
`;

const SectionLabel = styled.div`
  font-size: ${typography.fontSize.xs};
  color: ${colors.textTertiary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: ${spacing.xs};
`;

const CodeBlock = styled.pre`
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: ${typography.fontSize.xs};
  line-height: 1.5;
  color: ${colors.text};
  background: ${colors.background};
  padding: ${spacing.sm};
  border-radius: ${radius.sm};
  overflow-x: auto;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
`;

const ErrorText = styled.div`
  color: ${colors.error};
  font-size: ${typography.fontSize.sm};
`;

const EmptyOutput = styled.div`
  color: ${colors.textTertiary};
  font-style: italic;
`;

const ImagePreview = styled.img`
  max-width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: ${radius.sm};
  cursor: zoom-in;
  transition: transform 0.2s ease;
  margin: ${spacing.xs} 0;

  &:hover {
    transform: scale(1.02);
  }
`;

const ImageHint = styled.div`
  font-size: ${typography.fontSize.xs};
  color: ${colors.textTertiary};
  margin-top: ${spacing.xs};
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

function highlightJson(json: string): React.ReactNode {
  return json.split(/("(?:[^"\\]|\\.)*"|true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[{}\[\],:])/g).map((part, i) => {
    if (part.startsWith('"') && part.endsWith('"')) {
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

function formatOutput(output: string): React.ReactNode {
  const trimmed = output.trim();

  // Detect image URLs
  const imagePattern = /(https?:\/\/[^\s]+\.(?:png|jpg|jpeg|gif|webp|bmp|svg)(?:\?[^\s]*)?)/gi;
  const imageMatches = [...trimmed.matchAll(imagePattern)];

  if (imageMatches.length > 0) {
    // Find the image URL position
    const imageUrl = imageMatches[0][1];
    const imageStartIndex = trimmed.indexOf(imageUrl);

    // Get text before and after image
    const beforeText = trimmed.substring(0, imageStartIndex).trim();
    const afterText = trimmed.substring(imageStartIndex + imageUrl.length).trim();

    return (
      <>
        {beforeText && <span>{beforeText} </span>}
        <ImagePreview
          src={imageUrl}
          alt="Tool output"
          onClick={() => {}}
          data-image-zoom={imageUrl}
        />
        {afterText && <span> {afterText}</span>}
      </>
    );
  }

  // Detect if content contains structured metrics (key: value format)
  const hasMetrics = /^[A-Z_]+:|\b(Time Range|Metric|Current Value|Trend|Data Points|Min|Max|Avg)\b:/im.test(trimmed);
  
  if (hasMetrics) {
    // Format as structured metrics display
    return (
      <div style={{ lineHeight: 1.6 }}>
        {trimmed.split('\n').map((line, i) => {
          const trimmedLine = line.trim();
          if (!trimmedLine) return <br key={i} />;
          
          // Check if it's a key: value line
          const match = trimmedLine.match(/^([^:]+):\s*(.*)$/);
          if (match) {
            return (
              <div key={i}>
                <span style={{ color: colors.textSecondary }}>{match[1]}:</span>{' '}
                <span style={{ fontWeight: match[1].toLowerCase().includes('value') || match[1].toLowerCase().includes('avg') ? '600' : '400' }}>
                  {match[2]}
                </span>
              </div>
            );
          }
          
          // Check for separator lines (contains only | or -)
          if (/^[\s|/\\-]+$/.test(trimmedLine)) {
            return <div key={i} style={{ color: colors.textTertiary, fontFamily: 'monospace' }}>{trimmedLine}</div>;
          }
          
          return <div key={i}>{trimmedLine}</div>;
        })}
      </div>
    );
  }

  // Try to detect and format JSON
  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) ||
      (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      const parsed = JSON.parse(trimmed);
      return highlightJson(JSON.stringify(parsed, null, 2));
    } catch {
      // Not valid JSON
    }
  }

  // Try to extract JSON from mixed content
  const jsonMatch = trimmed.match(/(\{[\s\S]*\}|\[[\s\S]*\])/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[1]);
      const formatted = JSON.stringify(parsed, null, 2);
      const before = trimmed.substring(0, trimmed.indexOf(jsonMatch[1]));
      const after = trimmed.substring(trimmed.indexOf(jsonMatch[1]) + jsonMatch[1].length);
      return (
        <>
          {before && <span>{before}</span>}
          {highlightJson(formatted)}
          {after && <span>{after}</span>}
        </>
      );
    } catch {
      // Not valid JSON
    }
  }

  return output;
}

interface ToolResultProps {
  toolCall: ToolCall;
}

export function ToolResult({ toolCall }: ToolResultProps) {
  const [expanded, setExpanded] = useState(false);
  const [zoomedImage, setZoomedImage] = useState<string | null>(null);

  const getStatusIcon = () => {
    switch (toolCall.status) {
      case 'pending': return '○';
      case 'running': return <SpinnerIcon />;
      case 'success': return '✓';
      case 'error': return '✗';
    }
  };

  const formatJson = (obj: unknown): string => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  };

  const handleImageClick = (e: React.MouseEvent<HTMLImageElement>) => {
    const src = e.currentTarget.dataset.imageZoom;
    if (src) {
      setZoomedImage(src);
    }
  };

  return (
    <ToolContainer>
      <ToolHeader
        status={toolCall.status}
        onClick={() => setExpanded(!expanded)}
      >
        <ToolIcon>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </svg>
          </ToolIcon>
        <ToolName>{toolCall.name}</ToolName>
        <StatusIndicator status={toolCall.status}>
          {getStatusIcon()}
        </StatusIndicator>
        <ExpandIcon expanded={expanded} />
      </ToolHeader>

      <ToolBody expanded={expanded}>
        <SectionLabel>Input</SectionLabel>
        <CodeBlock>{formatJson(toolCall.input)}</CodeBlock>

        {toolCall.output && (
          <>
            <SectionLabel style={{ marginTop: spacing.md }}>Output</SectionLabel>
            {toolCall.status === 'error' ? (
              <ErrorText>{toolCall.output}</ErrorText>
            ) : (
              <>
                <CodeBlock onClick={handleImageClick}>{formatOutput(toolCall.output)}</CodeBlock>
                {/(https?:\/\/[^\s]+\.(?:png|jpg|jpeg|gif|webp|bmp|svg)(?:\?[^\s]*)?)/i.test(toolCall.output) && (
                  <ImageHint>Click image to enlarge</ImageHint>
                )}
              </>
            )}
          </>
        )}

        {!toolCall.output && toolCall.status === 'success' && (
          <EmptyOutput>No output</EmptyOutput>
        )}
      </ToolBody>

      {zoomedImage && (
        <ImageZoomModal
          src={zoomedImage}
          alt="Tool output image"
          onClose={() => setZoomedImage(null)}
        />
      )}
    </ToolContainer>
  );
}
