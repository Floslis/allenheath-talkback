# Installation

**English** · [Deutsch](INSTALL.de.md)

Takes about 10 minutes: 5 on the Mac, 5 at the desk.

## What you need

- A **Mac** on the **same network as the desk** (e.g. the tech laptop)
- An **Allen & Heath Avantis** with firmware V2.01
- A talkback mic on a **free input channel**

## 1. Prepare the desk

1. Patch the **talkback mic** to a free input channel. Note the channel number
2. Turn on **network MIDI**: Setup → Control → MIDI. Note the **base channel** (default 12)
3. Pick **one empty mute group per group** (e.g. 6, 7, 8 for Band, MD, Vicom). Empty means no channel is assigned to it
4. Put a **softkey** on each of these mute groups

> It works without softkeys too, then you only switch in the browser.

## 2. Install on the Mac

1. **[Download Talkback.zip](https://github.com/Floslis/allenheath-talkback/releases/latest/download/Talkback.zip)** (always the latest version)
2. Unzip it and drag the **`Talkback` folder directly into your home folder** (Finder → Go → Home, the house icon)

   > ⚠️ **Not** on the Desktop, in Documents, Downloads or iCloud. macOS does not let background services read files there, and the tool won't start. The installer checks this and warns you.

3. In the folder, **right-click `Installieren.command` → Open → Open**

   A double-click isn't enough for downloaded files, macOS blocks them otherwise.

4. If Python 3 is missing, macOS asks to install the **developer tools**: click yes, wait, then repeat step 3
5. Your browser opens **http://localhost:8787**. From now on the tool starts at every login and restarts after a crash

## 3. Set up

In the tool, click **Settings** at the top right:

1. Click **Find desk**. The tool listens for the desk and shows it with model and firmware. Tap it to take the IP
2. Enter the **talkback channel** and **MIDI base channel** from step 1
3. Choose the **mixes** that should appear in the tool
4. Create **groups**: name, softkey (mute group) and which mixes belong to it. One group can be **"all others"**, it then contains every mix that isn't in another group
5. Click **Save**

The main page now shows **"Desk connected"**.

## 4. Test

**Test outside of services and shows first**, with someone at the desk:

- Tap a group in the tool → the talkback channel's assigns change on the desk
- Press a softkey → the group changes in the tool, the LED lights green
- Change an assign by hand on the desk → the tool shows it within a second

## Updates

The tool checks GitHub every 6 hours and installs new versions **at 4 am**, so never during a service. If a blue banner appears at the top, you can also install right away. Settings and your own branding stay. Turn off: Settings → Updates.

## Troubleshooting

| Problem | Solution |
|---|---|
| Browser says "can't reach this page" | Is the folder in your home folder? Then run `Installieren.command` again. Errors are in `talkback.log` in the folder |
| "Desk … not reachable" | Settings → Find desk. Mac and desk must be on the same network |
| Find desk finds nothing | Are Mac and desk on different networks (VLANs)? Then enter the IP by hand (Setup → Network on the desk) |
| Softkey does nothing | Network MIDI on? Base channel correct? Mute group entered in the settings? |
| Folder moved | Run `Installieren.command` again in the new place |

## Uninstall

Run `Deinstallieren.command` (right-click → Open), then delete the folder.
