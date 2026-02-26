/**
 * 邮箱配置相关类型定义 | Email Configuration Types
 */

export interface SMTPConfig {
  host: string;
  port: number;
  useTLS: boolean;
  useSSL: boolean;
}

export interface EmailProviderPreset {
  id: string;
  name: string;
  category: string;
  categoryLabel: string;
  icon: string;
  description: string;
  smtp: SMTPConfig;
  helpText: string;
  helpLink: string | null;
}

export interface ProviderCategory {
  label: string;
  description: string;
  icon: string;
}

export interface EmailProvidersResponse {
  providers: EmailProviderPreset[];
  categories: Record<string, ProviderCategory>;
}
