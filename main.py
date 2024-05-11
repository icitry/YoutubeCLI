import argparse

from CliManager import CliManager
from service import ServiceLocator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scaling-factor', '-s',
                        help="Scaling factor relative to the CLI dimensions.",
                        type=float,
                        default=1.)
    parser.add_argument('--char-ratio', '-c',
                        help="CLI characters aspect ratio.",
                        type=float,
                        default=.6)
    parser.add_argument('--max-width', '-w',
                        help="Max video frame width in chars. Aspect ratio is fixed so it determines entire video size."
                             " Negative means uncapped, default behavior.",
                        type=int,
                        default=-1
                        )
    parser.add_argument('--video-url', '-u',
                        help="URL for a video to be played directly on start.",
                        type=str,
                        default=None
                        )
    args = parser.parse_args()

    service_locator = ServiceLocator(args.char_ratio)
    cli_manager = CliManager(service_locator, args.scaling_factor, args.max_width)

    try:
        cli_manager.run(video_url=args.video_url)
    except KeyboardInterrupt:
        quit()


if __name__ == '__main__':
    main()
