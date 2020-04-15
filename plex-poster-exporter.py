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
    from plexapi.server import PlexServer, CONFIG
    from plexapi.myplex import MyPlexAccount
    from plexapi.exceptions import BadRequest
except:
    print('\033[91mERROR:\033[0m', 'plexapi is not installed.')
    sys.exit()

# defaults
NAME = 'plex-poster-exporter'
VERSION = 0.1

# plex
class Plex():
    def __init__(self, username=None, password=None, server=None, library=None, overwrite=False, verbose=False):
        self.account = None
        self.username = username
        self.password = password
        self.servers = []
        self.server = server
        self.libraries = []
        self.library = library
        self.overwrite = overwrite
        self.verbose = verbose
        self.downloaded = 0
        self.skipped = 0

        self.getAccount()
        self.getServer()
        self.getLibrary()

    def getAccount(self):
        try:
            self.account = MyPlexAccount(self.username, self.password)
        except BadRequest as e:
            print('\033[91mERROR:\033[0m', 'failed to connect to Plex. Check your username and password.')
            sys.exit()


    def getServer(self):
        self.servers = [ _ for _ in self.account.resources() if _.product == 'Plex Media Server' ]
        if not self.servers:
            print('\033[91mERROR:\033[0m', 'no available servers.')
            sys.exit()
        if self.server == None or self.servers not in [ _.name for _ in self.servers ]:
            self.server = plexapi.utils.choose('Select Server', self.servers, 'name').connect()
        else:
            self.server = self.server(self.server)
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
        if not self.overwrite and os.path.isfile(path+'/'+filename):
            if self.verbose:
                print('\033[93mSKIPPED:\033[0m', path+'/'+filename)
            self.skipped += 1
        else:
            if plexapi.utils.download(self.server._baseurl+url, self.account._token, filename=filename, savepath=path):
                if self.verbose:
                    print('\033[92mDOWNLOADED:\033[0m', path+'/'+filename)
                self.downloaded += 1
            else:
                print('\033[91mDOWNLOAD FAILED:\033[0m', path+'/'+filename)
                sys.exit()

# main
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name=NAME, version=VERSION, message='%(prog)s v%(version)s')
@click.option('--username', prompt='Plex Username', help='The username for Plex.', required=True)
@click.option('--password', prompt='Plex Password', help='The password for Plex.', required=True)
@click.option('--server', help='The Plex server name.')
@click.option('--library', help='The Plex library name.',)
@click.option('--assets', help='Which assets should be exported?', type=click.Choice(['all', 'posters', 'backgrounds', 'banners', 'themes']), default='all')
@click.option('--overwrite', help='Overwrite existing assets?', is_flag=True)
@click.option('--verbose', help='Show extra information?', is_flag=True)
@click.pass_context
def main(ctx, username: str, password: str, server: str, library: str, assets: str, overwrite: bool, verbose: bool):
    plex = Plex(username, password, server, library, overwrite, verbose)

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

        if (assets is 'all' or assets == 'posters') and hasattr(item, 'thumb') and item.thumb != None:
            plex.download(item.thumb, 'poster.jpg', path)
        if (assets is 'all' or assets == 'backgrounds') and hasattr(item, 'art') and item.art != None:
            plex.download(item.art, 'background.jpg', path)
        if (assets is 'all' or assets == 'banners') and hasattr(item, 'banner') and item.banner != None:
            plex.download(item.banner, 'banner.jpg', path)
        if (assets is 'all' or assets == 'themes') and hasattr(item, 'theme') and item.theme != None:
            plex.download(item.theme, 'theme.mp3', path)

        if plex.library.type == 'show':
            for season in item.seasons():
                path = plex.getPath(season, True)
                if path == None:
                    print('\033[91mERROR:\033[0m', 'failed to extract the path.')
                    sys.exit()

                if (assets is 'all' or assets is 'posters') and hasattr(item, 'thumb') and item.thumb != None and season.title != None:
                    plex.download(item.thumb, (season.title+'-poster' if season.title != 'Specials' else 'season-specials-poster')+'.jpg', path)
                if (assets is 'all' or assets is 'backgrounds') and hasattr(item, 'art') and item.art != None and season.title != None:
                    plex.download(item.art, (season.title+'-background' if season.title != 'Specials' else 'season-specials-background')+'.jpg', path)
                # TODO: Add banners for seasons?
                # if (assets is 'all' or assets is 'banners') and hasattr(item, 'banner') and item.banner != None and season.title != None:
                #     plex.download(item.banner, (season.title+'-banner' if season.title != 'Specials' else 'season-specials-banner')+'.jpg', path)

    if verbose:
        print('\n\033[94mTOTAL SKIPPED:\033[0m', str(plex.skipped))
        print('\033[94mTOTAL DOWNLOADED:\033[0m', str(plex.downloaded))

# run
if __name__ == '__main__':
    main(obj={})