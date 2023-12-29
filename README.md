# critrolehue

Extract color :rainbow: from the Critical Role set lights.

![demo picture](demo.jpg)

> You can try out this demo [live in your browser](https://bauersimon.github.io/critrolehue/).

The goal of this project is to have an automatic way of extracting color from the Critical Role ambient lights. Please note that the color extraction is **not real-time**. Feel free to check out [this little technical slide deck I made](https://docs.google.com/presentation/d/e/2PACX-1vS42vjidmfR-c_pF3WUeojw-l25jv1xyqiYwAY1syjcCvkgWOrHTKnAytf2k_sLbU15zHwDgDEhuPNi/pub?start=false&loop=false&delayms=60000).

## Components

- functional
  - `extractor` written in `python` (extract colors and save them to `json`)
- planned
  - GitHub pages to host extracted colors (so it can be used by other tools)
  - GitHub action to automatically extract colors for new episodes as they are released
  - "some way" of synchronizing the colors with smart home (i.e. Philips Hue) when watching an episode
    - local program that interacts with the browser
    - (unlikely) browser extension
    - (unlikely) website that embedds episodes via `iframe`
  - maybe train a small BERT model with the color information from campaign 3 to generate color information for campaigns 1 and 2 as well

## Requirements

- `extractor`
    - see `extractor/requirements.txt`
    - `ffmpeg`
