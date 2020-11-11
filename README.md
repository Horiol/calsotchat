# CalsotChat

CalsotChat is an open source tool that lets you securely and anonymously 
chat with friends using the Tor network.

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

# TODO List

- [ ] Chat in groups with multiple members
- [x] Static Tor address
- [ ] Edit contact names
- [x] Make ports dynamics