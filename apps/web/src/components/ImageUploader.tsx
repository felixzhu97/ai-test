import { useState, useRef, useCallback } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { colors, radius, spacing, typography, transitions } from '../theme';
import { Button } from './Button';
import { useI18n } from '../i18n';

type TaskType = 'caption' | 'detect' | 'ocr';

interface Detection {
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
}

interface Result {
  caption?: string;
  detections?: Detection[];
  full_text?: string;
  processing_time_ms?: number;
}

const API_BASE = 'http://localhost:8000';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateX(8px); }
  to { opacity: 1; transform: translateX(0); }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing.lg};
`;

const TaskTabs = styled.div`
  display: flex;
  gap: ${spacing.xs};
  padding: 4px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: ${radius.md};
  width: fit-content;
`;

const TaskTab = styled.button<{ active: boolean }>`
  padding: 8px 16px;
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
  color: ${props => props.active ? colors.text : colors.textSecondary};
  background: ${props => props.active ? colors.surface : 'transparent'};
  border: none;
  border-radius: ${radius.sm};
  cursor: pointer;
  transition: all ${transitions.fast};
  box-shadow: ${props => props.active ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'};

  &:hover {
    color: ${colors.text};
  }
`;

const MainArea = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${spacing.lg};
  min-height: 480px;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const Panel = styled.div`
  background: ${colors.surface};
  border-radius: ${radius.lg};
  padding: ${spacing.lg};
  display: flex;
  flex-direction: column;
`;

const PanelTitle = styled.h3`
  font-size: ${typography.fontSize.sm};
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.textTertiary};
  margin: 0 0 ${spacing.md} 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ImageArea = styled.div`
  flex: 1;
  position: relative;
  border-radius: ${radius.md};
  background: ${colors.background};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${transitions.fast};
  overflow: hidden;

  &:hover {
    background: rgba(0, 0, 0, 0.02);
  }
`;

const HiddenInput = styled.input`
  display: none;
`;

const DropZone = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: ${spacing.md};
  padding: ${spacing.xl};
  text-align: center;
  width: 100%;
  height: 100%;
`;

const DropIcon = styled.div`
  width: 56px;
  height: 56px;
  border-radius: ${radius.lg};
  background: ${colors.primaryLight};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: ${colors.primary};
`;

const DropText = styled.p`
  font-size: ${typography.fontSize.base};
  color: ${colors.text};
  margin: 0;
`;

const DropHint = styled.p`
  font-size: ${typography.fontSize.sm};
  color: ${colors.textTertiary};
  margin: 0;
`;

const PreviewImage = styled.img`
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
`;

const ClearButton = styled.button`
  position: absolute;
  top: ${spacing.sm};
  right: ${spacing.sm};
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${transitions.fast};
  font-size: 18px;
  color: white;
  opacity: 0;
  z-index: 10;

  ${ImageArea}:hover & {
    opacity: 1;
  }

  &:hover {
    background: rgba(0, 0, 0, 0.8);
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${radius.md};
  z-index: 5;
`;

const Spinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid ${colors.border};
  border-top-color: ${colors.primary};
  border-radius: 50%;
  animation: ${spin} 0.7s linear infinite;
`;

const ResultContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${colors.textTertiary};
  font-size: ${typography.fontSize.sm};
  text-align: center;
`;

const ResultText = styled.p`
  font-size: ${typography.fontSize.md};
  line-height: 1.6;
  color: ${colors.text};
  margin: 0;
`;

const DetectionList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing.sm};
`;

const DetectionItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${spacing.md};
  background: ${colors.background};
  border-radius: ${radius.md};
`;

const DetectionName = styled.span`
  font-size: ${typography.fontSize.base};
  color: ${colors.text};
`;

const Confidence = styled.span`
  font-size: ${typography.fontSize.sm};
  color: ${colors.textSecondary};
`;

const OCRText = styled.pre`
  font-family: inherit;
  font-size: ${typography.fontSize.sm};
  line-height: 1.7;
  color: ${colors.text};
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  overflow-y: auto;
  flex: 1;
`;

const ErrorMessage = styled.div`
  margin-top: ${spacing.md};
  padding: ${spacing.md};
  background: ${colors.errorLight};
  color: ${colors.error};
  border-radius: ${radius.md};
  font-size: ${typography.fontSize.sm};
  animation: ${fadeIn} 0.2s ease-out;
`;

const ActionArea = styled.div`
  margin-top: ${spacing.md};
  padding-top: ${spacing.md};
  border-top: 1px solid ${colors.border};
`;

const taskOptions = [
  { value: 'caption' as TaskType, labelKey: 'caption' },
  { value: 'detect' as TaskType, labelKey: 'detect' },
  { value: 'ocr' as TaskType, labelKey: 'ocr' },
];

export function ImageUploader() {
  const { t } = useI18n();
  const [image, setImage] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [task, setTask] = useState<TaskType>('caption');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback((selectedFile: File) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError(t.imageUploader.selectImageError);
      return;
    }
    setFile(selectedFile);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => setImage(e.target?.result as string);
    reader.readAsDataURL(selectedFile);
    setResult(null);
  }, [t.imageUploader.selectImageError]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleClear = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setImage(null);
    setFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    const endpoints: Record<TaskType, string> = {
      caption: `${API_BASE}/vision/caption`,
      detect: `${API_BASE}/vision/detect`,
      ocr: `${API_BASE}/vision/ocr`,
    };

    try {
      const res = await fetch(endpoints[task], {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(t.imageUploader.requestFailed);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.imageUploader.processingFailed);
    } finally {
      setLoading(false);
    }
  }, [file, task, t.imageUploader.requestFailed, t.imageUploader.processingFailed]);

  const renderResult = () => {
    if (!result) return <EmptyState>{t.imageUploader.noImageYet}</EmptyState>;

    if (task === 'caption' && result.caption) {
      return <ResultText>"{result.caption}"</ResultText>;
    }

    if (task === 'detect' && result.detections) {
      return (
        <DetectionList>
          {result.detections.map((det, i) => (
            <DetectionItem key={i}>
              <DetectionName>{det.class_name}</DetectionName>
              <Confidence>{(det.confidence * 100).toFixed(0)}%</Confidence>
            </DetectionItem>
          ))}
        </DetectionList>
      );
    }

    if (task === 'ocr' && result.full_text) {
      return <OCRText>{result.full_text}</OCRText>;
    }

    return <EmptyState>{t.imageUploader.noImageYet}</EmptyState>;
  };

  const getTaskLabel = (labelKey: string) => {
    return t.imageUploader[labelKey as keyof typeof t.imageUploader] || labelKey;
  };

  return (
    <Container>
      <TaskTabs>
        {taskOptions.map((opt) => (
          <TaskTab
            key={opt.value}
            active={task === opt.value}
            onClick={() => setTask(opt.value)}
          >
            {getTaskLabel(opt.labelKey)}
          </TaskTab>
        ))}
      </TaskTabs>

      <MainArea>
        <Panel>
          <PanelTitle>{t.imageUploader.imageLabel}</PanelTitle>
          <ImageArea
            onClick={() => !image && fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <HiddenInput
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            />
            {image ? (
              <>
                <PreviewImage src={image} alt="Preview" />
                <ClearButton onClick={handleClear}>×</ClearButton>
                {loading && (
                  <LoadingOverlay>
                    <Spinner />
                  </LoadingOverlay>
                )}
              </>
            ) : (
              <DropZone>
                <DropIcon>+</DropIcon>
                <DropText>{t.imageUploader.dropText}</DropText>
                <DropHint>{t.imageUploader.dropHint}</DropHint>
              </DropZone>
            )}
          </ImageArea>
        </Panel>

        <Panel>
          <PanelTitle>{t.imageUploader.resultLabel}</PanelTitle>
          <ResultContent>
            {renderResult()}
          </ResultContent>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          <ActionArea>
            <Button
              fullWidth
              size="lg"
              onClick={handleSubmit}
              disabled={!file}
            >
              {loading ? t.imageUploader.analyzing : t.imageUploader.startAnalyze}
            </Button>
          </ActionArea>
        </Panel>
      </MainArea>
    </Container>
  );
}
