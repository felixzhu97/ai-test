import styled from '@emotion/styled';
import { css, keyframes } from '@emotion/react';
import { colors, shadows, radius, typography, transitions } from '../theme';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const getVariantStyles = (variant: ButtonVariant) => {
  const variants = {
    primary: css`
      background: ${colors.primary};
      color: white;
      box-shadow: ${shadows.sm};

      &:hover:not(:disabled) {
        background: ${colors.primaryHover};
        box-shadow: ${shadows.card};
      }

      &:active:not(:disabled) {
        background: ${colors.primaryActive};
        transform: scale(0.98);
      }
    `,
    secondary: css`
      background: ${colors.surface};
      color: ${colors.primary};
      border: 1px solid ${colors.border};
      box-shadow: ${shadows.sm};

      &:hover:not(:disabled) {
        background: ${colors.primaryLight};
        border-color: ${colors.primary};
      }

      &:active:not(:disabled) {
        background: ${colors.primaryLight};
        transform: scale(0.98);
      }
    `,
    ghost: css`
      background: transparent;
      color: ${colors.primary};

      &:hover:not(:disabled) {
        background: ${colors.primaryLight};
      }

      &:active:not(:disabled) {
        background: ${colors.primaryLight};
        transform: scale(0.98);
      }
    `,
    danger: css`
      background: ${colors.error};
      color: white;
      box-shadow: ${shadows.sm};

      &:hover:not(:disabled) {
        background: #e6352b;
        box-shadow: ${shadows.card};
      }

      &:active:not(:disabled) {
        background: #cc3126;
        transform: scale(0.98);
      }
    `,
  };

  return variants[variant];
};

const getSizeStyles = (size: ButtonSize) => {
  const sizes = {
    sm: css`
      padding: 6px 12px;
      font-size: ${typography.fontSize.sm};
      border-radius: ${radius.sm};
      gap: 4px;
    `,
    md: css`
      padding: 10px 18px;
      font-size: ${typography.fontSize.base};
      border-radius: ${radius.md};
      gap: 6px;
    `,
    lg: css`
      padding: 14px 24px;
      font-size: ${typography.fontSize.md};
      border-radius: ${radius.lg};
      gap: 8px;
    `,
  };

  return sizes[size];
};

const StyledButton = styled.button<{
  variant: ButtonVariant;
  size: ButtonSize;
  fullWidth: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: ${typography.fontFamily.body};
  font-weight: ${typography.fontWeight.medium};
  line-height: 1;
  border: none;
  cursor: pointer;
  transition: all ${transitions.default};
  white-space: nowrap;
  user-select: none;

  ${({ variant }) => getVariantStyles(variant)}
  ${({ size }) => getSizeStyles(size)}
  ${({ fullWidth }) => fullWidth && css`width: 100%;`}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:focus-visible {
    outline: none;
    box-shadow: ${shadows.input};
  }
`;

const Spinner = styled.span`
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: ${spin} 0.6s linear infinite;
`;

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  icon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Spinner />
      ) : icon ? (
        <>
          {icon}
          {children}
        </>
      ) : (
        children
      )}
    </StyledButton>
  );
}
