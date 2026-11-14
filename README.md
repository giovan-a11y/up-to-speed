# Up to Speed

Crash courses on 30+ small-talk topics (sports, luxury & style, money, food & drink, tech, culture, lifestyle), each with a course, flashcards, quiz, cheat sheet and a Hong Kong angle. It installs to your Home Screen and works offline.

**Open it:** https://giovan-a11y.github.io/up-to-speed/ (on iPhone: open in Safari → Share → Add to Home Screen; on Android or a computer: *Install app*).

## What keeps it current

A Claude cloud routine runs every morning at 06:30 Hong Kong time and follows [`ROUTINE.md`](ROUTINE.md), the same way the World Top 10 news briefing is made. No API key is needed.

- **Mondays:** it searches the web and refreshes "What people are talking about", key numbers (standings, prices, charts) and 3 current-events quiz questions for the fast-moving topics: football, F1, NBA, tennis, golf, racing, stocks, crypto, HK property, the economy, AI, gadgets, gaming, films & TV, K-pop/Canto-pop. Slower topics (wine, watches, hiking…) get the same refresh every four weeks.
- **Every day:** it writes any topics you requested. In the app, type a topic that isn't there → *Request this topic* → submit the GitHub issue that opens.

The installed app downloads new content the next time it's opened online and says "This week's update is ready".

## Files

| File | What it is |
|---|---|
| `data/topics/<slug>.json` | One topic each. `refresh` is `weekly` or `monthly`. |
| `data/weekly.json` | The latest refresh date and "Fresh this week" highlights. |
| `build.py` | Checks every topic and combines them into `data/bundle.json`, which the app loads; also stamps `sw.js` so installed apps update. Run `python3 build.py` after any change. |
| `index.html` | The app. |
| `sw.js`, `manifest.webmanifest`, `icons/` | Installing and working offline. |
| `ROUTINE.md` | Instructions the daily routine follows. |

Progress is saved on the device; use *Back up my progress* at the bottom of the home page to move it to another device.
