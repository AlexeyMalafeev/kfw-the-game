"""KFW - Kung-Fu World: single entry point.

Usage examples:
    python kfw.py                        new interactive game
    python kfw.py --autoplay             AI-only game, 4 players
    python kfw.py --autoplay -n 100      AI-only stress test, 100 players
    python kfw.py --autoplay --autosave  AI-only game with auto save
    python kfw.py --load save.txt        load a saved game
    python kfw.py --load "auto save.txt"
    python kfw.py --no-color             play without terminal colors
"""
import argparse

from kf_lib import game
from kf_lib import ui
from kf_lib.actors.player import SmartAIP, SmartAIPVisible
from kf_lib.ui import yn


def main():
    parser = argparse.ArgumentParser(description='KFW - Kung-Fu World')
    parser.add_argument('--load', metavar='FILE', help='load a saved game from the save folder')
    parser.add_argument('--autoplay', action='store_true', help='AI players only (no humans)')
    parser.add_argument('-n', '--num-players', type=int, default=None)
    parser.add_argument('--autosave', action='store_true', help='turn auto save on')
    parser.add_argument('--silent-ending', action='store_true',
                        help='no interactive prompts at the end of the game')
    parser.add_argument('--no-color', action='store_true', help='disable terminal colors')
    args = parser.parse_args()

    ui.init_colors(no_color_flag=args.no_color)

    g = game.Game()
    try:
        if args.load:
            g.load_game(args.load)
        elif args.autoplay:
            g.new_game(
                num_players=args.num_players or 4,
                coop=False,
                ai_only=True,
                auto_save_on=args.autosave,
                generated_styles=True,
                silent_ending=args.silent_ending,
            )
        else:
            kwargs = {}
            if args.num_players:
                kwargs['num_players'] = args.num_players
            if args.autosave:
                kwargs['auto_save_on'] = True
            visible_ai = yn("Do you want to see what AI players do?")
            DefaultAI = SmartAIPVisible if visible_ai else SmartAIP
            g.new_game(forced_aip_class=DefaultAI, confirm_styles_with_player=True, **kwargs)
        g.play()
    except KeyboardInterrupt:
        print('\nFarewell, brave warrior!')
    except Exception:  # noqa
        from kf_lib.testing.debug_tools import crash_report
        crash_report(g)


def run():
    main()


if __name__ == '__main__':
    run()
