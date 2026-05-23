import { useEffect, useCallback } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { colors, spacing } from '../theme';

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const slideIn = keyframes`
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
`;

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: ${spacing.xl};
  animation: ${fadeIn} 0.2s ease;
  cursor: zoom-out;
`;

const ImageContainer = styled.div`
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  animation: ${slideIn} 0.25s ease;
  cursor: default;
`;

const Image = styled.img`
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
`;

const CloseButton = styled.button`
  position: absolute;
  top: -16px;
  right: -16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: ${colors.surface};
  border: 1px solid ${colors.border};
  color: ${colors.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

  &:hover {
    background: ${colors.surfaceSecondary};
    transform: scale(1.1);
  }
`;

const Caption = styled.div`
  text-align: center;
  color: ${colors.textSecondary};
  font-size: 14px;
  margin-top: ${spacing.md};
`;

interface ImageZoomModalProps {
  src: string;
  alt?: string;
  onClose: () => void;
  testID?: string;
}

export function ImageZoomModal({ src, alt, onClose, testID: _testID }: ImageZoomModalProps) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [handleKeyDown]);

  return (
    <Overlay onClick={onClose}>
      <ImageContainer onClick={(e) => e.stopPropagation()}>
        <Image src={src} alt={alt || 'Zoomed image'} />
        {alt && <Caption>{alt}</Caption>}
        <CloseButton onClick={onClose} aria-label="Close">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </CloseButton>
      </ImageContainer>
    </Overlay>
  );
}
