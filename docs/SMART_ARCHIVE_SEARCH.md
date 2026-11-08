# Smart Archive Search — Public Scholar's Edition

Search is entirely static, client-side, and free: no third-party search provider, account, or Keeper notes. Open the search dialog from any page or with **Ctrl+K / Cmd+K**.

## How it works

- `assets/search.js`: testable client-side search engine. Normalizes punctuation, whitespace and accents, ranks exact title matches, aliases, subtitles, summaries and public article body. Uses conservative one-character typo tolerance for meaningful names; never invents a result.
- `assets/app.js`: search UI interactions, category filter chips, result labels, up/down keyboard navigation, Enter to open, Esc to close, focus return and focus trapping.
- `assets/search.css`: mobile and desktop style for the existing dark archival modal.
- `build.py`: builds `search-index.json` from public `content/articles/*.md`, `data/search-aliases.yml`, and the approved `data/article-merges.yml`. Each consolidated entry receives a `type: section` search result that links to its actual parent article with the correct fragment.
- `tests/test_search.js`: search engine regression checks, executed during GitHub Actions publication.
- `tests/check_public_canon.py`: checks every alias maps to a currently published public article.

## Adding a new alias

Edit `data/search-aliases.yml`:

```yaml
aliases:
  faelynn:
    - Night Mistress
```

Only add synonyms genuinely supported by an existing public record. Aliases should not assert unknown identities or reveal future campaign plot details. You do not need to list the article title itself, which is already searchable.

## Search relevance

Exact titles and exact known aliases carry the most weight, followed by prefix and partial matches, subtitles, descriptions, and full public article content. A one-character typo may match a reasonably long title word or nickname. Every query term must match somewhere in a record. Search sections have distinct labels and direct anchors. When no query is entered, the interface offers featured articles.

## Testing

```sh
node --check assets/search.js
node --check assets/app.js
node --test tests/test_search.js
python tests/check_public_canon.py
python build.py
```

Inspect `_site/search-index.json` after building to verify which articles and merged sections are publicly indexed.

## Known limitations

This is conservative client-side fuzzy matching, not semantic search. It does not automatically guess an unrelated nickname, a multi-word typo with several missing words, or a Keeper-only connection. Publish an appropriate public alias if readers regularly use an alternate name.
