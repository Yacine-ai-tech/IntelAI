import React from 'react';
import { useTranslation } from '../i18n/I18nContext';

export default function ApiDocsPage() {
  const { t } = useTranslation();
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  return (
    <div className="w-full h-[calc(100vh-4rem)] p-4">
      <h1 className="text-3xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">{t('apiDocsTitle')}</h1>
      <iframe src={`${apiUrl}/docs`} className="w-full h-full border-0 rounded bg-white" title={t('apiDocsTitle')} />
    </div>
  );
}

