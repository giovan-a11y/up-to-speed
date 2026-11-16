# Daily routine: keep Up to Speed current

A Claude cloud routine runs this every morning at 06:30 Hong Kong time with this repository checked out. Work on `main` and push to `main`: GitHub Pages republishes the app on every push.

Today's date in Hong Kong (`TZ=Asia/Hong_Kong date`) decides what to do:

1. **Every day: topic requests.** List the open issues whose title starts with `Topic:`, opened by `giovan-a11y` (ignore anyone else's). For each, write a new topic (see "Writing a new topic"), then close the issue with a one-line comment saying it's added. If a request is not a real topic or is harmful, close it with a short explanation instead.
   Also handle open issues titled `Cuisine: X` by `giovan-a11y` the same way: add the cuisine (see "Adding a cuisine") and close the issue.
2. **Mondays: weekly refresh.** Refresh every topic whose `refresh` is `"weekly"`, plus every `"monthly"` topic whose `updated` date is 27 or more days ago (see "Refreshing a topic").
3. Any other day with no requests: do nothing and don't commit.

If the scheduled run missed a Monday (for example `data/weekly.json` is more than 7 days old), do the weekly refresh today.

When anything changed: run `python3 build.py` (it validates every topic and fails with a list of problems; fix them and run it again), then commit `data/` and `sw.js` with a message like `Weekly update 2026-11-16` or `Add topic: mahjong`, and push.

## Who it's for

giovanni lives in Hong Kong and uses this to keep up with popular small-talk topics well enough to chat with enthusiasts at work, at a bar or on a date. Casual, warm, plain English; specific and accurate; real names, results, numbers and dates. Never invent a result: if you couldn't confirm it with a search, leave it out.

## Refreshing a topic

Topic files are `data/topics/<slug>.json`. Search the web for what has actually happened in that topic recently (the last week or two for weekly topics, the last month or two for monthly ones), including Hong Kong news where there is some. Then change **only** these fields and leave the evergreen course content alone:

- `now`: 5–6 `{ "headline", "detail" }` talking points, freshest and most talked-about first. Detail is 1–2 sentences with specifics (who won, by how much, what it costs, when it's out). Keep an older point only if people still talk about it.
- `numbers`: 3–6 `{ "label", "value" }` key figures worth knowing right now: league leaders and points, championship standings, index levels, Bitcoin price, box office, chart toppers. `[]` if the topic has none.
- `asOf`: today's date, e.g. `"16 Nov 2026"`.
- `updated`: today's date as `YYYY-MM-DD`.
- `quiz`: remove the questions marked `"current": true` and add 3 new ones about these current events, each `{ "q", "options": [4 strings], "answer": <0-based index>, "explain", "current": true }`. Vary where the right answer sits. Keep the other questions as they are.

After refreshing, rewrite `data/weekly.json`:

```json
{
  "date": "2026-11-16",
  "refreshed": ["slug", "..."],
  "highlights": [{ "slug": "formula-1", "topic": "Formula 1", "headline": "One sentence on the biggest change this week." }]
}
```

Include a highlight only for topics where something genuinely notable changed, biggest first, at most 8. The app shows these under "Fresh this week".

## Writing a new topic

Copy the shape of an existing file such as `data/topics/wine.json` and research the topic with web search. The file name and `slug` are the topic name in lowercase with spaces as hyphens (e.g. `board-games`). Fields:

- `slug`, `topic` (clean display name), `category` (one of: Sports, Luxury & style, Money, Food & drink, Tech, Culture, Lifestyle)
- `refresh`: `"weekly"` if it has fast-moving news, results or prices people talk about, otherwise `"monthly"`
- `updated` and `requested`: today as `YYYY-MM-DD`; `asOf`: today, e.g. `"16 Nov 2026"`
- `tagline`: one punchy sentence; `why`: 2–4 sentences on what it is and why people are into it
- `essentials`: exactly 5 `{ "title", "body" }` core ideas
- `jargon`: 12 `{ "term", "meaning" }`; `names`: 12 `{ "name", "what" }`
- `timeline`: 8–10 `{ "year", "event" }`, oldest first
- `now`: 5 `{ "headline", "detail" }`; `numbers`: 0–6 `{ "label", "value" }`
- `local`: 4 `{ "headline", "detail" }` Hong Kong angles (local scene, places, people, how Hong Kongers talk about it)
- `debates`: 4 `{ "question", "sides" }`; `starters`: 5 questions to ask an enthusiast
- `sayThis`: 3 `{ "say", "why" }`; `avoid`: 3–4 rookie mistakes
- `quiz`: 10 `{ "q", "options": [4], "answer", "explain" }`, answer positions varied
- `gallery` (for anything visual: products, cars, watches, bags, dishes, places, artworks): 6–14 `{ "name", "what", "wiki" }` iconic things people mention by name, where `wiki` is the exact title of the English Wikipedia article that shows it (the app loads its picture from there). Leave it out for non-visual topics.
- Any `names` entry whose plain name would find the wrong Wikipedia article can also get a `wiki` title.

Also add a highlight for it to `data/weekly.json` (keep the existing entries) so it appears under "Fresh this week".

## World cuisines

`data/cuisines/<slug>.json` holds the World cuisines section: one file per cuisine with signature dishes the app shows with a picture, name and main ingredients. It is evergreen: **don't touch it in the weekly refresh**, only when a `Cuisine:` request comes in.

### Adding a cuisine

Copy the shape of `data/cuisines/thai.json`. Fields: `slug` (file name), `cuisine` (display name), `flag` (emoji), `region` (one of: Europe, Asia, Americas, Middle East & Africa), `order` (put it after the others in its region), `intro` (1–2 sentences on its character), `flavours` (the key ingredients and flavours, comma-separated), optional `hk` (one true sentence on where it shows up in Hong Kong; leave it out if unsure), and `dishes`: 6–12 signature dishes, each `{ "name", "local" (native name, optional), "say" (rough pronunciation, optional), "what", "ingredients": [4–6 main components], "wiki" }`.

`what` is one line on what the dish is and looks like, not how to cook it; mention the cooking method only when it is the dish's signature (tandoor, spit-roasting, Peking duck). `wiki` must be the exact title of the English Wikipedia article whose lead picture shows the dish; the app loads and caches that picture. Commit with a message like `Add cuisine: Ethiopian`.

