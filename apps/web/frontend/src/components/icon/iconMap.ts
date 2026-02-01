import iconMapData from '@design-system/icons/icon-map.json';

export type IconMap = {
  name: string;
  version: string;
  library: string;
  defaults: {
    sizePx: Record<string, number>;
    colorTokens: Record<string, string>;
  };
  rules: Record<string, boolean>;
  categories: Record<
    string,
    Record<
      string,
      {
        icon: string;
        color: string;
        size: string;
        animate?: string;
      }
    >
  >;
};

export const iconMap = iconMapData as IconMap;

export type IconSemantic = `${keyof IconMap['categories'] & string}.${string}`;
export type IconColorKey = keyof IconMap['defaults']['colorTokens'] & string;
export type IconSizeKey = keyof IconMap['defaults']['sizePx'] & string;

export function resolveIconSemantic(semantic: IconSemantic): {
  category: string;
  name: string;
  entry: IconMap['categories'][string][string];
} | null {
  const [category, name] = semantic.split('.') as [string, string];
  const entry = iconMap.categories[category]?.[name];
  if (!entry) return null;
  return { category, name, entry };
}
