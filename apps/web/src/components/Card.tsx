import styled from '@emotion/styled';
import { css } from '@emotion/react';
import { colors, shadows, radius, spacing, transitions } from '../theme';

type CardVariant = 'default' | 'elevated' | 'outlined' | 'glass';
type CardPadding = 'none' | 'sm' | 'md' | 'lg';

interface CardProps {
  variant?: CardVariant;
  padding?: CardPadding;
  hoverable?: boolean;
  onClick?: () => void;
  testID?: string;
}

const getPadding = (padding: CardPadding) => {
  const paddings = {
    none: '0',
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
  };
  return paddings[padding];
};

const getVariantStyles = (variant: CardVariant) => {
  const variants = {
    default: css`
      background: ${colors.surface};
      box-shadow: ${shadows.card};
    `,
    elevated: css`
      background: ${colors.surface};
      box-shadow: ${shadows.elevated};
    `,
    outlined: css`
      background: ${colors.surface};
      border: 1px solid ${colors.border};
      box-shadow: none;
    `,
    glass: css`
      background: ${colors.glass};
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      box-shadow: ${shadows.card};
      border: 1px solid ${colors.borderLight};
    `,
  };

  return variants[variant];
};

const StyledCard = styled.div<{
  variant: CardVariant;
  padding: CardPadding;
  hoverable: boolean;
  onClick?: () => void;
}>`
  border-radius: ${radius.lg};
  overflow: hidden;
  transition: all ${transitions.smooth};

  ${({ variant }) => getVariantStyles(variant)}
  padding: ${({ padding }) => getPadding(padding)};

  ${({ hoverable, onClick }) =>
    (hoverable || onClick) &&
    css`
      cursor: pointer;

      &:hover {
        transform: translateY(-2px);
        box-shadow: ${shadows.cardHover};
      }

      &:active {
        transform: translateY(0);
      }
    `}
`;

export function Card({
  variant = 'default',
  padding = 'md',
  hoverable = false,
  children,
  onClick,
  testID,
  ...props
}: CardProps & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <StyledCard
      variant={variant}
      padding={padding}
      hoverable={hoverable}
      onClick={onClick}
      {...props}
    >
      {children}
    </StyledCard>
  );
}
