/* eslint-disable no-restricted-imports */
import type { CSSProperties } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Ban,
  BarChart3,
  Bell,
  Brain,
  Calendar,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Circle,
  ClipboardList,
  Clock,
  Cpu,
  DollarSign,
  Download,
  Edit3,
  ExternalLink,
  Eye,
  FileText,
  Flag,
  Folder,
  GitCompare,
  GitBranch,
  HelpCircle,
  History,
  Info,
  LayoutDashboard,
  Layers,
  Lightbulb,
  Link2,
  Loader2,
  Lock,
  MessageSquare,
  Mic,
  MoreHorizontal,
  Package,
  Paperclip,
  PauseCircle,
  RefreshCw,
  Rocket,
  Search,
  Send,
  Server,
  Settings,
  Shield,
  Sparkles,
  StickyNote,
  Table,
  Undo2,
  Unlock,
  User,
  Wrench,
  X,
  XCircle,
} from 'lucide-react';
import { tokens } from '@design-system/tokens/tokens';
import { iconMap, resolveIconSemantic, type IconColorKey, type IconSemantic } from './iconMap';
import styles from './Icon.module.css';

const iconRegistry = {
  Activity,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Ban,
  BarChart3,
  Bell,
  Brain,
  Calendar,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Circle,
  ClipboardList,
  Clock,
  Cpu,
  DollarSign,
  Download,
  Edit3,
  ExternalLink,
  Eye,
  FileText,
  Flag,
  Folder,
  GitCompare,
  GitBranch,
  HelpCircle,
  History,
  Info,
  LayoutDashboard,
  Layers,
  Lightbulb,
  Link2,
  Loader2,
  Lock,
  MessageSquare,
  Mic,
  MoreHorizontal,
  Package,
  Paperclip,
  PauseCircle,
  RefreshCw,
  Rocket,
  Search,
  Send,
  Server,
  Settings,
  Shield,
  Sparkles,
  StickyNote,
  Table,
  Undo2,
  Unlock,
  User,
  Wrench,
  X,
  XCircle,
};

type IconSizeOverride = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';

type BaseIconProps = {
  semantic: IconSemantic;
  className?: string;
  size?: IconSizeOverride;
  color?: IconColorKey;
  title?: string;
  style?: CSSProperties;
};

type IconProps =
  | (BaseIconProps & { decorative: true; label?: never })
  | (BaseIconProps & { decorative?: false; label: string });

const sizeTokens: Record<IconSizeOverride, number> = {
  sm: tokens.iconography.sizePx.min,
  md: tokens.iconography.sizePx.default,
  lg: tokens.iconography.sizePx.max,
  xl: tokens.spacingPx.lg,
  '2xl': tokens.spacingPx.xl,
  '3xl': tokens.spacingPx['2xl'],
};

const tokenToCssVar: Record<string, string> = {
  'tokens.color.brand.orange500': 'var(--color-brand-orange-500)',
  'tokens.color.neutral.grey500': 'var(--color-neutral-grey-500)',
  'tokens.color.text.primary': 'var(--color-text-primary)',
  'tokens.color.state.success.fg': 'var(--color-state-success-fg)',
  'tokens.color.state.warning.fg': 'var(--color-state-warning-fg)',
  'tokens.color.state.error.fg': 'var(--color-state-error-fg)',
  'tokens.color.state.info.fg': 'var(--color-state-info-fg)',
};

function resolveColor(colorKey: IconColorKey | undefined): string {
  const resolvedKey = colorKey ?? 'primaryText';
  const tokenPath = iconMap.defaults.colorTokens[resolvedKey];
  return tokenToCssVar[tokenPath] ?? 'var(--color-text-primary)';
}

export function Icon({
  semantic,
  className,
  size,
  color,
  label,
  decorative,
  title,
  style,
}: IconProps) {
  const resolved = resolveIconSemantic(semantic);
  if (!resolved) {
    if (import.meta.env.DEV) {
      console.warn(`Unknown icon semantic: ${semantic}`);
    }
    return null;
  }

  const { entry } = resolved;
  const IconComponent = iconRegistry[entry.icon as keyof typeof iconRegistry];

  if (!IconComponent) {
    if (import.meta.env.DEV) {
      console.warn(`Missing lucide icon for ${entry.icon}`);
    }
    return null;
  }

  const iconSize = sizeTokens[size ?? (entry.size as IconSizeOverride)] ??
    tokens.iconography.sizePx.default;
  const iconColor = resolveColor(color ?? (entry.color as IconColorKey));
  const shouldSpin = entry.animate === 'spin';
  const ariaLabel = decorative ? undefined : label;

  const combinedClassName = [
    styles.icon,
    className,
    shouldSpin ? styles.spin : null,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span
      className={combinedClassName}
      aria-hidden={decorative ? 'true' : undefined}
      aria-label={ariaLabel}
      role={decorative ? undefined : 'img'}
      title={title ?? ariaLabel}
      style={{
        color: iconColor,
        width: iconSize,
        height: iconSize,
        ...style,
      }}
    >
      <IconComponent width={iconSize} height={iconSize} aria-hidden="true" />
    </span>
  );
}
