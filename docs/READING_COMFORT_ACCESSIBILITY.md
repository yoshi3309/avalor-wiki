# Reading Comfort & Accessibility — Public Archive

This enhancement preserves the dark royal archive and illuminated paper identity, while giving readers direct controls to make long histories and illustrated archival exhibits easier to read.

## Reader controls

The **Aa Reading** control in the shared topbar is available across the public site. Its non-modal panel includes:
- Text size: Standard (15px base), Large (17px), Extra large (19px). Sizing applies to long-form article body, narrative callouts, chapter navigation, reading-desk summaries, and historical exhibit text.
- Typeface: Classic serif or Clear sans-serif for long-form text (decorative and display headings remain in the existing theme).
- High contrast: darker ink and brighter text on parchment, improved dark surfaces, more visible links and borders.
- Reduce motion: turns off decorative transitions/animations and smooth scrolling; operating-system reduced-motion preferences still apply even when the site's manual toggle is off.
- Restore defaults.

Preferences use the browser's localStorage key \`avalor-reading-comfort-v1\`; no login, account, tracking, or network request. If storage is blocked, controls still apply while the page is open and display a warning. Other tabs receive preference changes through the native storage event.

The script runs early in the document head, applying saved settings before the page body is rendered. Controls do not require readers to accept cookies or create an account.

## Accessibility refinements

- The existing skip link remains first in document order, keyboard accessible.
- Visible focus styles cover links, buttons, form controls and disclosure summaries, with a darker ring inside paper surfaces.
- Mobile navigation is inert while closed so off-screen links are not keyboard accessible. Opening the sidebar places focus inside; Tab stays in the drawer until dismissed; Escape closes and returns focus to the menu button.
- Article table-of-contents links move keyboard focus to the heading reached.
- Long tables can scroll horizontally on small screens without forcing the entire article to overflow.
- Reading settings use semantic buttons with \`aria-pressed\`, checkboxes, explicit labels, an \`aria-expanded\` trigger and a status message.
- Reduced motion respects OS settings, with a site override covering animations/transitions and atlas smooth scrolling.
- Printed articles hide the controls and use readable monochrome body text.

## Test coverage and remaining validation

GitHub publishing runs \`node --check assets/reading-comfort.js\` and \`python tests/check_reading_comfort.py\` alongside the standard archive build tests.

These tests verify the generated controls, responsive styles, cross-page assets and source-level keyboard handling. They **do not** certify WCAG compliance, screen-reader behavior, perceptual contrast of every accent or fully automated keyboard usage. Before claiming formal accessibility compliance, manually test iPhone Safari, Android Chrome, desktop keyboard navigation, high browser zoom, VoiceOver/NVDA, and forced-color systems.

No Keeper content is loaded or required by these reader-only interface controls.
