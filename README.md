# CalsotChat

CalsotChat is an open source tool that lets you securely and anonymously 
chat with friends using the Tor network.

## Requirements
* Python3.7
* Nodejs v12.19.0
* Tor installed as a service

### Install tor as a service
* Ubuntu: https://help.ubuntu.com/community/Tor
    * Edit torrc file (default location in /etc/tor/)
        * Edit "CookieAuthentication" and set it to "0"
        * Uncomment "SocksPort 9050"
        * Uncomment "ControlPort 9051"
* Windows:
    * Download Windows Expert Bundle: https://www.torproject.org/download/tor/ 
    * Create a torrc file with the following content:
        ```
        SocksPort 9050
        ControlPort 9051
        CookieAuthentication 0
        ```
    * Install tor service using torrc file
        ```
        .\tor.exe -f .\torrc
        ```
    * More info at https://miloserdov.org/?p=1839 



## Project setup
```
yarn install
pip install -r requirements
```

### Compiles and hot-reloads for development
shell 1:
```
python main.py
```

shell 2:
```
yarn serve
```

### Compiles and minifies for production
```
pyinstaller main.spec && yarn build
```

### Lints and fixes files
```
yarn lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).


## Electron

### Start develop server
shell 1:
```
python main.py
```

shell 2:
```
yarn electron:serve
or
npm run electron:serve
```

### Build app
```
pyinstaller main.spec && yarn electron:build
or
pyinstaller main.spec && npm run electron:build
```

## Launch 2 instance in the same machine
To be able to launch 2 instance of the app in the same machine we have to add some cmd arguments to start the app:
* --port : local port that we will listen (default: 5000) 
* --onion_port : port that will be listen in tor network interface (default: 80) 
* --folder: local directory where save persistent data (default: ~/calsotchat)

for example, to launch the second instance we will do the following in a cmd terminal:
```
./CalsotChat-0.1.0.AppImage --port=5010 --onion_port=8080 --folder=~/calsotchat2
```

## TODO List

- [ ] Chat in groups with multiple members
- [x] Static Tor address
- [x] Edit contact names
- [x] Check contacts status (online/offline)
- [x] Resend failed messages when contact reconnects
- [ ] Write logs when running in Bundle
- [x] Make ports dynamics
- [ ] Mechanism to discover of servers