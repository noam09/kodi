# script.keepawake
When you stream media from a remote Kodi library, KeepAwake makes sure it doesn't fall asleep while you're streaming.

## Description
If Kodi streams files from a remote Kodi instance, KeepAwake makes sure that the remote instance doesn't enter sleep mode by sending it a quick left and right remote "shake" (just like pressing left and right on its remote/keyboard). This prevents suspend.

## Installation
Download the latest ZIP [here](https://github.com/noam09/kodi/tree/master/repo/script.keepawake).
Feel free to [install the repository](https://github.com/noam09/kodi/tree/master/repo/repository.coffee) in order to receive updates for the addon. 

## Usage
* Make sure the webserver is enabled on the remote Kodi instance, this can be found in `Settings → Services → Control → Allow control of Kodi via HTTP`.
* Make note of the port and optional username (default `kodi`) and password (default `kodi`) values.
* Determine the IP address of the remote Kodi device using the `System Information` screen, or by running the command relevant to your operating system in a terminal or command prompt (usually `ifconfig` on Linux, `ipconfig` on Windows).
* Interval in minutes determines the delay between every time the remote Kodi is kept awake with a "shake", "rattle", or whatever you'd like to call it.
* Input these values on the configuration screen for the KeepAwake addon.
* If you would like to issue a Wake-On-Lan following failed stream attempts, or after a file has been paused for a while, enable the Wake-On-Lan setting and input the MAC address of the remote Kodi device.

## Screenshot
![preview thumb](http://i.imgur.com/lh7s5o6.png)
