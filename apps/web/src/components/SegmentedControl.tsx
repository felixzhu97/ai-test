import styled from '@emotion/styled';
import { css } from '@emotion/react';
import { colors, shadows, radius, typography, transitions } from '../theme';

interface SegmentedControlProps<T extends string> {
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
}

const Container = styled.div`
  display: inline-flex;
  background: ${colors.surface};
  border-radius: ${radius.md};
  padding: 3px;
  box-shadow: ${shadows.card}, inset 0 1px 1px ${colors.border};
  gap: 2px;
`;

const Option = styled.button<{ active: boolean }>`
  position: relative;
  padding: 8px 20px;
  font-family: ${typography.fontFamily.body};
  font-size: ${typography.fontSize.base};
  font-weight: ${typography.fontWeight.medium};
  color: ${colors.textSecondary};
  background: transparent;
  border: none;
  border-radius: ${radius.sm};
  cursor: pointer;
  transition: all ${transitions.fast};
  white-space: nowrap;

  ${({ active }) =>
    active &&
    css`
      color: ${colors.text};
      background: ${colors.surface};
      box-shadow: ${shadows.sm};
    `}

  &:hover:not([data-active="true"]) {
    color: ${colors.text};
  }

  &:focus-visible {
    outline: none;
    box-shadow: ${shadows.input};
  }
`;

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
}: SegmentedControlProps<T>) {
  return (
    <Container role="tablist">
      {options.map((option) => (
        <Option
          key={option.value}
          active={value === option.value}
          data-active={value === option.value}
          role="tab"
          aria-selected={value === option.value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </Option>
      ))}
    </Container>
  );
}
