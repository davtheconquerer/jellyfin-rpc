# Jellyfin RPC

A little python script I wrote to display the current movie/tv series I'm watching on my [Jellyfin](https://jellyfin.org/) server, on my [Discord](https://discord.com/) status.

## How to install

### 1. Clone latest repository

```bash
git clone https://github.com/davtheconquerer/jellyfin-rpc.git
cd jellyfin-rpc
```

### 2. Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
```

#### Activate Virtual Environment

For Windows:

```bash
./venv/Scripts/activate
```

For Linux:

```bash
source /venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Discord Developer Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and name it something like "Jellyfin".
3. Copy the **Application ID** (You'll need this for the `config.json` step).

Next two steps are **Optional**:

4. On the **left** menu, go to **Rich Presence -> Art Assets**.
5. Click **Add Image**, upload a Jellyfin logo, name it exactly `jellyfin_logo`, and save your changes.

### 4. Create and Setup `config.json`

Copy `templateconfig.json` and rename the copy to `config.json`.

Fill in with your details:

```json
{
    "client_id": "YOUR_DISCORD_APPLICATION_ID_HERE",
    "server_url": "http://your-jellyfin-ip:8096",
    "api_key": "YOUR_JELLYFIN_API_KEY_HERE",
    "username": "YOUR_JELLYFIN_USERNAME_HERE"
}
```

### 5. Haven't made your API key on your jellyfin server yet?

1. Login to an **admin** account on your jellyfin server
2. Go to **Dashboard**
3. Scroll to bottom and find **API Keys**
4. Create a new one and call it `jellyfin-rpc` or whatever you want.
5. Copy that into your `config.json`

## How to use

Make sure your venv is activated *(see [Activate Your Virtual Environment](#activate-virtual-environment))*

Then run the following command:

```bash
python main.py
```
