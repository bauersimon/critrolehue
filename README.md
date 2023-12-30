# critrolehue

Extract color :rainbow: from the Critical Role set lights.

![demo picture](demo.jpg)

> You can try out this demo [live in your browser](https://bauersimon.github.io/critrolehue/).

The goal of this project is to have an automatic way of extracting color from the Critical Role ambient lights. Please note that the color extraction is **not real-time**. Feel free to check out [this little technical slide deck I made](https://docs.google.com/presentation/d/e/2PACX-1vS42vjidmfR-c_pF3WUeojw-l25jv1xyqiYwAY1syjcCvkgWOrHTKnAytf2k_sLbU15zHwDgDEhuPNi/pub?start=false&loop=false&delayms=60000).

## Components / Roadmap

- [x] `extractor` (`python`): extracts colors and saves them to `json`
- [x] GitHub pages to host extracted colors (so it can be used by other tools)
- [x] GitHub action to automatically extract colors for new episodes as they are released
- [ ] `connector` (`golang`): demo application that synchronizes the colors with smart home (i.e. Philips Hue) when watching an episode
- [ ] train a small BERT model with the color information from campaign 3 to generate color information for campaigns 1 and 2 as well

## Requirements

- `extractor`
    - see `extractor/requirements.txt`
    - `ffmpeg`
