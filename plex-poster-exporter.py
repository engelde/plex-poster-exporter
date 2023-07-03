#!/usr/bin/env python3

import os
import sys

# sys
sys.dont_write_bytecode = True
if sys.version_info[0] < 3:
    print('\033[91mERROR:\033[0m', 'you must be running python 3.0 or higher.')
    sys.exit()

# click
try:
    import click
except:
    print('\033[91mERROR:\033[0m', 'click is not installed.')
    sys.exit()

# plexapi
try:
    import plexapi.utils
    from plexapi.server import PlexServer
    from plexapi.exceptions import BadRequest
except:
    print('\033[91mERROR:\033[0m', 'plexapi is not installed.')
    sys.exit()

# defaults
NAME = 'plex-poster-exporter'
VERSION = 0.1

# plex
class Plex():
    def __init__(self, baseurl=None, token=None, library=None, overwrite=False, verbose=False, output_path=None):
        self.baseurl = baseurl
        self.token = token
        self.server = None
        self.libraries = []
        self.library = library
        self.overwrite = overwrite
        self.verbose = verbose
        self.output_path = output_path
        self.downloaded = 0
        self.skipped = 0

        self.getServer()
        self.getLibrary()

    def getServer(self):
        try:
            self.server = PlexServer(self.baseurl, self.token)
        except BadRequest as e:
            print('\033[91mERROR:\033[0m', 'failed to connect to Plex. Check your server URL and token.')
            sys.exit()

        if self.verbose:
            print('\033[94mSERVER:\033[0m', self.server.friendlyName)

    def getLibrary(self):
        self.libraries = [ _ for _ in self.server.library.sections() if _.type in {'movie', 'show'} ]
        if not self.libraries:
            print('\033[91mERROR:\033[0m', 'no available libraries.')
            sys.exit()
        if self.library == None or self.library not in [ _.title for _ in self.libraries ]:
            self.library = plexapi.utils.choose('Select Library', self.libraries, 'title')
        else:
            self.library = self.server.library.section(self.library)
        if self.verbose:
            print('\033[94mLIBRARY:\033[0m', self.library.title)

    def getAll(self):
        return self.library.all()

    def getPath(self, item, season=False):
        if self.library.type == 'movie':
            for media in item.media:
                for part in media.parts:
                    return part.file.rsplit('/', 1)[0]
        elif self.library.type == 'show':
            for episode in item.episodes():
                for media in episode.media:
                    for part in media.parts:
                        if season:
                            return part.file.rsplit('/', 1)[0]
                        return part.file.rsplit('/', 2)[0]

    def download(self, url=None, filename=None, path=None):
        path = path.lstrip('/')
        abs_path = os.path.join(self.output_path, path)

        if not self.overwrite and os.path.isfile(os.path.join(abs_path, filename)):
            if self.verbose:
                print('\033[93mSKIPPED:\033[0m', os.path.join(abs_path, filename))
            self.skipped += 1
        else:
            if plexapi.utils.download(self.server._baseurl+url, self.token, filename=filename, savepath=abs_path):
                if self.verbose:
                    print('\033[92mDOWNLOADED:\033[0m', os.path.join(abs_path, filename))
                self.downloaded += 1
            else:
                print('\033[91mDOWNLOAD FAILED:\033[0m', os.path.join(abs_path, filename))
                sys.exit()






# main
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name=NAME, version=VERSION, message='%(prog)s v%(version)s')
@click.option('--baseurl', prompt='Plex Server URL', help='The base URL for the Plex server.', required=True)
@click.option('--token', prompt='Plex Token', help='The authentication token for Plex.', required=True)
@click.option('--library', help='The Plex library name.',)
@click.option('--assets', help='Which assets should be exported?', type=click.Choice(['all', 'posters', 'backgrounds', 'banners', 'themes']), default='all')
@click.option('--output-path', default='/', help='The output path for the downloaded assets. Change to a hardcoded location to run script as a sort of dry run.')
@click.option('--overwrite', help='Overwrite existing assets?', is_flag=True)
@click.option('--verbose', help='Show extra information?', is_flag=True)
@click.pass_context
def main(ctx, baseurl: str, token: str, library: str, assets: str, overwrite: bool, verbose: bool, output_path: str):
    plex = Plex(baseurl, token, library, overwrite, verbose, output_path)

    if verbose:
        print('\033[94mASSETS:\033[0m', assets)
        print('\033[94mOVERWRITE:\033[0m', str(overwrite))
        print('\nGetting library items...')

    items = plex.getAll()

    for item in items:
        if verbose:
            print('\n\033[94mITEM:\033[0m', item.title)

        path = plex.getPath(item)
        if path == None:
            print('\033[91mERROR:\033[0m', 'failed to extract the path.')
            sys.exit()

        if (assets == 'all' or assets == 'posters') and hasattr(item, 'thumb') and item.thumb != None:
            plex.download(item.thumb, 'poster.jpg', path)
        if (assets == 'all' or assets == 'backgrounds') and hasattr(item, 'art') and item.art != None:
            plex.download(item.art, 'background.jpg', path)
        if (assets == 'all' or assets == 'banners') and hasattr(item, 'banner') and item.banner != None:
            plex.download(item.banner, 'banner.jpg', path)
        if (assets == 'all' or assets == 'themes') and hasattr(item, 'theme') and item.theme != None:
            plex.download(item.theme, 'theme.mp3', path)

        if plex.library.type == 'show':
            for season in item.seasons():
                path = plex.getPath(season, True)
                if path == None:
                    print('\033[91mERROR:\033[0m', 'failed to extract the path.')
                    sys.exit()

                # TODO: Add backgrounds for seasons?
                # if (assets == 'all' or assets == 'backgrounds') and hasattr(season, 'art') and season.art != None and season.title != None:
                #     plex.download(season.art, (season.title+'-background' if season.title != 'Specials' else 'season-specials-background')+'.jpg', path)
                # TODO: Add banners for seasons?
                # if (assets == 'all' or assets == 'banners') and hasattr(season, 'banner') and season.banner != None and season.title != None:
                #     plex.download(season.banner, (season.title+'-banner' if season.title != 'Specials' else 'season-specials-banner')+'.jpg', path)

    if verbose:
        print('\n\033[94mTOTAL SKIPPED:\033[0m', str(plex.skipped))
        print('\033[94mTOTAL DOWNLOADED:\033[0m', str(plex.downloaded))

# run
if __name__ == '__main__':
    main(obj={})
