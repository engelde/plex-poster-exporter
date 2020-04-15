# Plex Poster Exporter
Export posters, backgrounds, banners, and theme songs from Plex.

## Installation
```
sudo python3 -m pip install -r requirements.txt
```

## Usage
```
python3 plex-poster-exporter.py --verbose
```

## Advanced Usage
```
python3 plex-poster-exporter.py --username "<EMAIL>" --password "<PASSWORD>" --server "<SERVER>" --library "<LIBRARY>" --assets "<ASSETS>" --overwrite --verbose
```

## Arguments

All arguments are optional. If one is required and it is not provided, the script will ask you to enter it.

| Option          | Description                                                                    | Default       |  
| --------------- | ------------------------------------------------------------------------------ | ------------- |  
| --username      | The username for Plex.                                                         |               |  
| --password      | The password for Plex.                                                         |               |  
| --server        | The Plex server name.                                                          |               |  
| --library       | The Plex library name.                                                         |               |  
| --assets        | Which assets should be exported? (all, posters, backgrounds, banners, themes)  | all           |  
| --overwrite     | Overwrite existing assets?                                                     | False         |  
| --verbose       | Show extra information?                                                        | False         |  
| --help          | Show the help message and exit.                                                |               |  

## Notes

This script expects all of your media files to be in the correct folder structure for Plex. If your files are not organized in the way that Plex [recommends](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/), you **will not** be able to use this.

Enjoy!