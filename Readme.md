# Xibo Media Updater
Xibo Media Updater automatically pulls media from Google Drive using rclone, then uses a python script to push changes to Xibo.

## Configuration
Xibo Media Updater expects 2 config files, `config.env` for environment variables, and `config.csv`, which correlates folders with playlists.
Start by going to Xibo, and adding a new application, and selecting the client credentials grant. Then put the Xibo URL and the generated client ID and client secret into the `config.env` file.

Then, you can create the folder structure in Google Drive. By default, rclone will look for a folder entitled `media` in your drive and sync it down to a folder called `media` locally. This can be reconfigured in `main.sh` and `config.csv`. Rclone then syncs the contents of the remote media folder into the local media folder. If you are working with multiple different playlists, you can create subfolders within your root media folder, updating `config.csv` accordingly. A line in that file might look something like this: `media/display1, 12`. That would push everything in the `media/display1` folder into the playlist with ID 12. If you only need one playlist, your `config.csv` may only have one line like this: `media, 5`.

Create that media folder locally once you are done setting up your drive: `mkdir media`
### Rclone Setup

Rclone can be setup with the guide here: https://rclone.org/drive/

I chose to call my Google Drive `gdrive` in rclone, if you choose something else, make sure to update `main.sh` accordingly.


## Python Dependencies
`pip install requests`

## Running
Start with: `chmod +x main.sh`

Then: `./main.sh`. Or you could schedule a cron job.