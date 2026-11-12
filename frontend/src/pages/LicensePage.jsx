export default function LicensePage() {
  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '2rem 1.25rem', lineHeight: 1.7 }}>
      <h1 style={{ fontSize: '1.6rem', marginBottom: '0.5rem' }}>License & Terms</h1>
      <p style={{ opacity: 0.75 }}>
        This software is <strong>free and open-source</strong> under the{' '}
        <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank" rel="noreferrer">GNU Affero General Public License v3.0</a>.
        See the <code>LICENSE</code> file in the source repository.
      </p>
      <h2 style={{ fontSize: '1.15rem', marginTop: '1.75rem' }}>Open-source use (AGPL-3.0)</h2>
      <p>You may use, modify, and self-host this software — including commercially — provided modified versions made available over a network are released under AGPL-3.0.</p>
      <h2 style={{ fontSize: '1.15rem', marginTop: '1.75rem' }}>Commercial license</h2>
      <p>If your use cannot comply with AGPL obligations, a <strong>Commercial License</strong> is available. See <code>COMMERCIAL.md</code> or contact the maintainer. Licensed installs set <code>LICENSE_KEY=LIC-...</code>; opt out with <code>LICENSE_BEACON_DISABLE=true</code>.</p>
      <h2 style={{ fontSize: '1.15rem', marginTop: '1.75rem' }}>This hosted demo</h2>
      <p>Provided for evaluation. Uploaded content is processed for the app's function and may be retained for analytics; sandbox uploads are session-scoped and wiped per retention policy. Do not upload unlawful content. Provided "as is" without warranty.</p>
      <h2 style={{ fontSize: '1.15rem', marginTop: '1.75rem' }}>Telemetry</h2>
      <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>Anonymous startup ping + usage analytics are sent to the operator's gateway. Self-hosted instances can disable via <code>TELEMETRY_OPT_OUT=true</code>, <code>DO_NOT_TRACK=1</code>, or custom <code>TELEMETRY_URL</code>/<code>LICENSE_BEACON_URL</code>.</p>
    </div>
  );
}
