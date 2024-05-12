# YoutubeCLI

[Link to the YouTube video](https://youtu.be/CYNpdmgwNTM)

All of us have probably experienced the horrors beyond human comprehension that come with a classic Youtube session, so what do you say if, by taking this nigh infinite potential of the platform, while getting rid of all the fluff, we use it in the way it’s always been intended – running the entire thing from your terminal, no fancy useless UI, no fancy useless features and even no fancy useless graphics.

By combining the powers of the official Youtube API, the ever-dependable Python and the ingenuity (ahem) of yours truly, I try to get the entirety of the Youtube experience running in a terminal, in such a way that no matter the environment, you'll get to experience the platform in its most adequate form.

## Setting up
To setup the execution environment:
```shell
cd path/to/root
python -m venv env
pip install -r requirements.txt
```

To be able to use the Google Auth side of things, you need to create and download your client secret config file.
1. Create a new project in your **Google Cloud Console**.
2. Enable Youtube Data API v3 and setup OAuth, making sure to select the correct scopes: `https://www.googleapis.com/auth/youtube.force-ssl`.
3. Download the credentials file to the auth directory and make sure it's named `client_secret.json`.

Usage:
```
usage: main.py [-h] [--scaling-factor SCALING_FACTOR] [--char-ratio CHAR_RATIO] [--max-width MAX_WIDTH]
               [--video-url VIDEO_URL] [--subtitles] [--subtitles-lang SUBTITLES_LANG] [--colors]

optional arguments:
  -h, --help            show this help message and exit
  --scaling-factor SCALING_FACTOR, -f SCALING_FACTOR
                        Scaling factor relative to the CLI dimensions.
  --char-ratio CHAR_RATIO, -r CHAR_RATIO
                        CLI characters aspect ratio.
  --max-width MAX_WIDTH, -w MAX_WIDTH
                        Max video frame width in chars. Aspect ratio is fixed so it determines entire video size.
                        Negative means uncapped, default behavior.
  --video-url VIDEO_URL, -u VIDEO_URL
                        URL for a video to be played directly on start.
  --subtitles, -s       Flag that signals to enable video subtitles. If no matches are found, it attempts to load
                        auto-generated captions.
  --subtitles-lang SUBTITLES_LANG, -l SUBTITLES_LANG
                        The preferred language for the subtitles.
  --colors, -c          Use colors when rendering. *Warning: Performance-heavy.
```

Keyboard mappings:
* **H** : Navigate to the Home page.
* **C** : Navigate to the Creator page.
* **S** : Navigate to the Search page | Enable Search if on the Search page.
* **V** : Navigate to the Video page.
* **SPACE** : Pause / Unpause the video if on the Video page.
* **BACKSPACE** : Delete character if on the Search page and the Search bar is active.
* **ENTER** : Navigate to current video if on the Home / Creator / Search page.
* **ESC** : Set Search bar is inactive, if on the Search page.
* **N** : Navigate to the next video if on the Home / Creator / Search page.
* **P** : Navigate to the previous video if on the Home / Creator / Search page.
* **K** : Navigate to the current video creator's page, if on the Video page.
* **L** : Like the current video, if on the Video page. If already liked, cancels like.
* **D** : Dislike the current video, if on the Video page. If already disliked, cancels dislike.
* **U** : Update subscription status, if on the Creator page (look S was already taken, had to brainstorm).
* **Q** : Quit the application.

*Notes:
1. Regarding **Color rendering** of the frames, currently it has been set to accept the base ANSI-8 primary colors, but new entries can be added to the ANSIConstants.COLORS dictionary, following the established structure. The color matching algorithm (should) work with any number of input colors, although the more colors to choose from, the slower the execution.
2. I have opted **not** to include *audio* support due to the on-the-fly nature of the project, as it would over-complicate and slow-down the execution considerably due to potential syncing issues. 
