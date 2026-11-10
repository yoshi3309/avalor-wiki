# Atlas Through Time — Phase 6.3

The Living Chronicle and Cartographer's Table now share a careful public historical-navigation layer. Its purpose is to show where a source supports a geographical connection, without assigning invented positions to events that remain unplaced.

## Sources and limits

- data/living-chronicle.yml supplies all 18 events, exact existing display dates, historical periods, public source articles and date-confidence labels.
- data/avalor-map.yml supplies all approved cartographic coordinates. This feature neither creates nor relocates markers.
- data/atlas-history.yml is the manually reviewed bridge. Only published, placed, non-provisional existing map pins can appear.
- An event may have a **recorded site**, an **affected region**, or an **associated place**. Associated does not imply that the historical act took place at that spot.
- Six geographic relationships are currently supported; twelve events remain with no atlas location. Do not invent past borders, ceremonial sites, battlefronts, travel paths, distances or new dates.

## Reviewed connections

| Chronicle event | Existing marker | Meaning and limitation |
| --- | --- | --- |
| Gathering of crowns and Osmo's defeat | Heroes Hill | Recorded battle site, NOT an alliance meeting site |
| Kingdom established | Renada | Capital of the new realm, NOT an established place of signing |
| Black Tower catastrophe | Black Tower | Recorded site of catastrophe; date remains approximate |
| Elven Concord | Forest of the Fey | Communities and woodland rights affected, NOT proven signing site |
| Arnaud's persecution | Heaven's Heart | Shelter and resistance to the edicts, NOT the place edicts were issued |
| Gradvum takes throne | Renada | Established seat of government, NOT a verified coronation location |

## Reader experience

The cartographer now offers a scrollable historical shelf before the unchanged map. By default, it shows six events with approved geographic relationships. A checkbox reveals all 18 historical events, including those without established map locations. Period filters follow the five published Chronicle period IDs. Each event opens a detailed summary, an honest label describing the strength/type of its geographic association, and the original date-confidence explanation.

Events linked to public map pins highlight and focus the approved markers without drawing historical border overlays or changing any map coordinates. Unmapped events visibly say the location is not established. A historical view link can be copied for sharing in Discord, pointing to map/?event=EVENT#atlas-history-detail. The Chronicle links directly back to the mapped events only and also links to the new historical Atlas in its sidebar.

The catalog, dates, and Chronicle references remain readable without JavaScript, although interactive map focus requires the browser script.

## Maintenance

When new authoritative geography becomes available, add one record under links in data/atlas-history.yml with event, place, relation, and an explanatory note. The accepted relation values are event-site, affected-region, associated-place. The build refuses unknown or duplicate events, missing or unpublished/unplaced/provisional pins, unsupported relation types, and inadequate provenance notes. Do not modify the chronology's original dates simply to fit a marker.

## Testing

GitHub Actions now checks atlas-time.js syntax and runs tests/check_atlas_time.py, as well as the rest of the site's usual tests. This check verifies all 18 events remain present, exactly six public pin associations exist, original dates and narratives are preserved, chronological links resolve, and historical navigation does not manufacture new geography. Manual touch and assistive-tech tests remain recommended.
