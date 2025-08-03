/**
 * Optimized imports to improve tree-shaking and reduce bundle size
 */

// Re-export only what we need from heavy libraries
export type { AxiosResponse } from 'axios';

// Lazy import functions for better tree-shaking
export const createAxiosInstance = async () => {
  const { default: axios } = await import('axios');
  return axios.create({
    timeout: 10000,
    headers: {
      'User-Agent': 'DeepCLI/1.0'
    }
  });
};

// Optimized chalk imports
export const createChalk = async () => {
  const { default: chalk } = await import('chalk');
  return {
    green: chalk.green,
    red: chalk.red,
    yellow: chalk.yellow,
    blue: chalk.blue,
    gray: chalk.gray
  };
};

// Optimized ora imports
export const createSpinner = async (text: string) => {
  const { default: ora } = await import('ora');
  return ora(text);
};

// Tree-shakable utility functions
export const safeStringify = (obj: any): string => {
  try {
    return JSON.stringify(obj);
  } catch {
    return String(obj);
  }
};

export const safeParse = <T = any>(str: string): T | null => {
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
};

// Debounced function for expensive operations
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T => {
  let timeout: NodeJS.Timeout;
  return ((...args: any[]) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(null, args), wait);
  }) as T;
};

// Throttled function for rate limiting
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): T => {
  let inThrottle: boolean;
  return ((...args: any[]) => {
    if (!inThrottle) {
      func.apply(null, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  }) as T;
};