# CalsotChat

CalsotChat is an open source tool that lets you securely and anonymously 
chat with friends using the Tor network.

## How to contribute
- Install python requirements:
```
pip install -r requirements
```

- Start python main script:
```
python main.py
```

## How to create a package
- Build python package using pyinstaller
```
pyinstaller main.spec
```

This command will create a new build in ./dist folder and then you can 
execute python script using the following command:
```
dist/clasotchat/calsotchat
```