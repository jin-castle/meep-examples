---
layout: rights
title: "Privacy & Analytics"
eyebrow: "PRIVACY & ANALYTICS"
description: "What visitor analytics measures, why it is used, and how to choose."
permalink: /en/privacy/
lang: en
updated: "2026-10-24"
toc:
  - { id: analytics, label: "Optional visitor analytics" }
  - { id: choices, label: "Consent and withdrawal" }
  - { id: search, label: "Search and reports" }
  - { id: hosting, label: "Hosting and services" }
---

<h2 id="analytics">Optional visitor analytics</h2>

[jin-castle](https://github.com/jin-castle) uses Google Analytics 4 (GA4) to improve these learning materials. **The Analytics tag is not loaded and no Analytics requests are sent before you allow it.** Declining does not restrict access to the lessons.

If you allow analytics, Google receives and processes statistics such as page views, visits, engagement time, referring sites, browser/device information and approximate region. Your IP address may be transmitted to Google servers as part of the request. We do not send login credentials, names or email addresses as analytics fields. Page URL queries/fragments and referring URL paths/queries are removed. We do not separately collect search-box text or campaign parameters.

Analytics cookies start with `meep_ga`, are scoped to this project's path, and have a configured 60-day expiry. Google Signals, advertising personalization and enhanced measurement are disabled. See [how Google uses information from sites and apps using its services](https://policies.google.com/technologies/partner-sites) and the [Google Privacy Policy](https://policies.google.com/privacy).

<h2 id="choices">Consent and withdrawal</h2>

Use **Analytics settings** in any page footer to allow analytics or withdraw your consent. Withdrawal stops this site's GA collection, clears its project analytics cookies and reloads the page if the tag has already run. It does not retroactively delete previously transmitted statistics.

Your choice is stored in this browser's local storage (`meep-examples:analytics-consent:v1`). Clearing storage resets it. If storage is unavailable, the choice applies only to the current page and you may be asked again on the next page. Language/theme preferences also use browser storage; these preference changes are not sent as analytics events.

If local storage cannot save a refusal, the non-tracking `meep_analytics_denied` cookie remembers only that refusal for 60 days. If both cookies and storage are blocked, collection stops on the current page and the page explains that the choice could not be saved.

<h2 id="search">Search and reports</h2>

GA4 counts **consenting visits where the tag runs successfully**. Declining, blockers and browser settings affect the result, so it may differ from the total number of actual visitors. Visits before the integration are not recovered.

Google Search Console separately reports this site's impressions, clicks, queries and positions in Google Search. It does not require an additional visitor-tracking script. It does not measure total market-wide search volume; Google can anonymize or omit some queries.

Reports are protected by the administrator's Google account permissions. Visitor-level records and dashboard data are not published on this website. For inquiries, use the contact methods listed on the [maintainer's GitHub profile](https://github.com/jin-castle).

<h2 id="hosting">Hosting and external services</h2>

GitHub Pages hosts this website and processes requests needed to serve it regardless of analytics consent. See the [GitHub General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). External resources, including formula rendering, and external links may involve other services governed by their own privacy policies.
