# Private site analytics

Use the administrator's Google account. Google enforces access to reports; the
public GitHub Pages site contains no report data, API secret or client-side password.

- [GA4 home](https://analytics.google.com/analytics/web/#/a413293572p560565339/reports/intelligenthome): visitors, page views, engagement and traffic sources.
- [Search Console](https://search.google.com/search-console?resource_id=https%3A%2F%2Fjin-castle.github.io%2Fmeep-examples%2F): Google Search impressions, clicks, queries, CTR and positions. This is site visibility, not total keyword search volume.

GA account: `413293572`; property: `560565339`; web stream: `16194251384`;
public measurement ID: `G-4BL7PWF8YR`. Both language editions share this stream.
Reporting timezone is Korea (UTC+09:00). Enhanced measurement and optional
account data sharing were disabled during setup. Do not add other users or link
advertising products without an explicit owner request.

The public measurement ID and Search Console verification meta tag in `_config.yml`
are identifiers, not credentials. Retain the verification tag after verification.
Never place OAuth tokens, private keys, GA API secrets or exported reports here.

`_includes/settings-head.html` loads the local consent controller in every layout,
including the catalog's custom head. Google code loads only on the configured
production origin and project path, after explicit consent. A single `config`
command sends the page view. Enhanced measurement stays off to avoid automatic
URL/search capture and history-based pageview duplication. URL queries/fragments
are stripped and referrers reduced to origin; campaign attribution is consequently
limited. No custom internal-search events are sent.

GA cookies use the `meep` prefix, host-only scope, project path and 60-day expiry.
Signals and advertising personalization are disabled in code. Default ad consent
stays denied. Withdrawing stops collection, clears project cookies and reloads
an already-instrumented page. Cross-tab revocation also stops active collection.
Only consenting visits with a working tag count; past visits cannot be restored.
Reports may take time to populate and Search Console can omit anonymized queries.

Privacy pages: `/privacy/` and `/en/privacy/`. Visitors can reopen their choice
from any footer. To exclude your ordinary admin visits on this browser, choose
Decline analytics; use an explicitly consenting browser for a controlled smoke test.

The dependency-free `sitemap.xml` covers public lessons, topics and policy pages
in both languages. Submit `https://jin-castle.github.io/meep-examples/sitemap.xml`
in Search Console. No root `robots.txt` is provided because this repository is
hosted under a subpath rather than the domain root.

Validation:

```sh
node --check assets/analytics.js
node _tools/check-analytics.mjs
node _tools/check-analytics.mjs --live
node _tools/check-rights.mjs --live
```

Browser smoke tests must confirm no Google request before consent, one pageview
after consent, refusal persistence, withdrawal, both languages and mobile themes.
Google dashboards, not a local stub, confirm reception and account access.
