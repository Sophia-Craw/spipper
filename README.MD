# How To Setup

All you will need in terms of prerequisits are a Spotify API client ID and secret.
You can obtain these by creating an API app at: https://developer.spotify.com/

There, you must log in and head to the __developer portal__ where you can then create an API app which will generate both a client ID and secret for you.

Once you've obtained these create a `.env` file in the same directory (folder) that the `sipper` binary exists in.

Should look something like this:
```env
CLIENT_ID="<your_id>"
CLIENT_SECRET="<your_secret>"
```