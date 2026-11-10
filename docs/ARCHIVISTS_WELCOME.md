# Phase 6.1 — The Archivist's Welcome

An optional, source-grounded introduction to the Archives at /start/, designed for newcomers arriving from Discord or a shared wiki link.

## Editorial aim

The entry point should resemble an invitation from the Royal Commission, not a tutorial popup or gamified test. Four doorways lead through existing PUBLIC articles:

1. Discover the Kingdom — crown, founding settlement, capital.
2. Meet the Heroes — later fellowship, Lavitz, founding fellowship.
3. Uncover the History — unification, the Six, the sundering.
4. Explore the World — landscapes, the Forest of the Fey, and Renada.

Each doorway includes introductory editorial copy, three linked public starting records, and either an already-published reading journey or the current public Interactive Atlas. The introductions avoid narrating major twists, while deeper articles may contain the full approved historical record. Do not claim the entire wiki is spoiler-free.

The presentation intentionally does NOT require an account, use location data, save preferences, replace the homepage, or block returning readers.

## Files and behavior

- data/welcome-routes.yml: four curated routes and public record slugs.
- templates/welcome.html: accessible public HTML for all paths, rendered server-side.
- assets/welcome.css: welcome page and homepage entry styling.
- assets/welcome.js: optional route selection and hash linking. With JavaScript disabled all four routes remain visible.
- templates/home.html and templates/base.html: homepage gateway, ribbon, and main navigation.
- build.py: validates route IDs, article slugs, journey IDs and text; generates /start/index.html and its unique social preview.
- tests/check_welcome.py: validates published paths and navigation.

## Editing routes

Edit the route YAML and run the build. Retain exactly four recognized IDs in the established order. Each path must contain three distinct published article slugs. The destination field must be a published journey ID or the explicit atlas option. The builder rejects invalid or duplicated steps, missing labels and unknown destinations.

## Accessibility and canon

Choice cards are ordinary anchor links and work without JavaScript. With JavaScript the selected route is highlighted while the others are collapsed. The selected heading gets focus, deep links and browser history work, and reduced-motion settings are respected.

All copy is introductory editorial synthesis of public articles, not new fictional lore. No Keeper data or unpublished material is loaded. The page uses the existing lion crest and public archive skyline rather than generating or inventing character imagery.
