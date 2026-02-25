# What is Spipper?
Spipper is a tool that lets you take ownership of your music on Spotify.

If you are tired of having to pay indefinitely for your music and can't quite leave the collection you've curated over the many years of using Spotfy, this tool is for you.

***THE MISUSAGE OF THIS TOOL TO OBTAIN MEDIA THAT YOU DO NOT OWN OR HAVE NOT ALREADY LISTENED TO REGULARLY AND/OR HAVE HAD ADDED BEFORE IS NOT CONDONED***

***IT IS ENCOURAGED THAT YOU REBUILD YOUR LIBRARY OVER TIME AND SUPPORT ARTISTS ON PLATFORMS SUCH AS [BANDCAMP](https://bandcamp.com) OR [ITUNES](https://www.apple.com/itunes/)***

# How To Setup

All you will need in terms of prerequisits are a Spotify API client ID and secret.
You can obtain these by creating an API app at: https://developer.spotify.com/

There, you must log in and head to the __developer portal__ where you can then create an API app which will generate both a client ID and secret for you.

Once you've obtained these create a `.env` file in the same directory (folder) that the `spipper` binary exists in.

Should look something like this:
```env
CLIENT_ID="<your_id>"
CLIENT_SECRET="<your_secret>"
```