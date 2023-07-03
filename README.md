# Plex Poster Exporter
Export posters, backgrounds, banners, and theme songs from Plex.

## Installation
```
sudo python3 -m pip install -r requirements.txt
```

## Dry run
To dry run this script (you can even do it from a different machine with a different filestructure), try the `--output-path` option:
```sh
python3 plex-poster-exporter.py --output-path /home/me/test

# ... go through prompts.
# ... assets get saved to this location:
# /home/me/test/your-data/path/to/Library/Movie (1999)/poster.jpg

# ... instead of the real path of the data, as Plex sees it:
# # /your-data/path/to/Library/Movie (1999)/poster.jpg
```

## Usage
```
python3 plex-poster-exporter.py --verbose
```

## Advanced Usage
```
python3 plex-poster-exporter.py --username "<EMAIL>" --token "<TOKEN>" --server "<SERVER>" --library "<LIBRARY>" --output-path "<OUTPUTPATH>" --assets "<ASSETS>" --overwrite --verbose
```

## Arguments

All arguments are optional. If one is required and it is not provided, the script will ask you to enter it.

| Option          | Description                                                                                         | Default       |  
| --------------- | --------------------------------------------------------------------------------------------------- | ------------- |  
| --username      | The username for Plex.                                                                              |               |  
| --server        | The Plex server name.                                                                               |               |  
| --library       | The Plex library name.                                                                              |               |  
| --output-path   | The base output path; change to export assets in directory structure that mirrors your library.     | '/'           |  
| --assets        | Which assets should be exported? (all, posters, backgrounds, banners, themes)                       | all           |  
| --overwrite     | Overwrite existing assets?                                                                          | False         |  
| --verbose       | Show extra information?                                                                             | False         |  
| --help          | Show the help message and exit.                                                                     |               |  

## Notes

This script expects all of your media files to be in the correct folder structure for Plex. If your files are not organized in the way that Plex recommends, you **will not** be able to use this.

[Movies](https://support.plex.tv/articles/naming-and-organizing-your-movie-media-files/)  
[Series](https://support.plex.tv/articles/naming-and-organizing-your-tv-show-files/)  

Enjoy!
