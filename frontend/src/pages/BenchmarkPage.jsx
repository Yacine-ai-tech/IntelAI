import React from 'react';
import { useTranslation } from '../i18n/I18nContext';

export default function BenchmarkPage() {
  const { t } = useTranslation();
  const content = `# ${t('benchSub')}

${t('benchIntro')}
Reproducible: \`python tests/run_rag_eval.py\`

## Setup
${t('benchSetup')}
The evaluation checks:
- **${t('benchAccuracy')}**
- **${t('benchSecurity')}**
- **${t('benchHallucination')}**

## ${t('benchResults')}
| Metric | Score |
|--------|-------|
| Evaluated Queries | 20 |
| Passed Queries | 18 |
| Overall Success Rate | **90.0%** (18/20) |

**${t('benchHeadline')}**

*Note: Tested using Anthropic Claude 3.5 Sonnet / 4.6 as the underlying reasoning engine.*
\n\n`;

  return (
    <div className="p-8 max-w-5xl mx-auto overflow-auto h-full">
      <h1 className="text-3xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">{t('benchTitle')}</h1>
      <div className="bg-gray-800/50 backdrop-blur-md p-8 rounded-xl border border-gray-700 shadow-2xl text-gray-200">
        <pre className="whitespace-pre-wrap font-sans leading-relaxed text-sm">{content}</pre>
      </div>
    </div>
  );
}
