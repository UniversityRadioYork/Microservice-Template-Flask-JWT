# Microservice Template with Flask and JWT Auth
A handy template to get started with MyRadio authentcation with JSON Web Tokens and Flask. This can be rapidly deployed on URY's microservices infrastructure via portainer.

# Setup
You get get this running in docker as follows:

```bash
docker compose up --build
```

You'll need to re-run that command when you make certain changes.

If you want to develop it might be easier to be closer to the metal and run on your machine. Simply install the pyton env and run the the main file. Make sure to fill out the an appropriate env file - if dev mode is on, it will hot-refresh for any changes you make.

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

The server will be live on `127.0.0.1:6339` - check, the port may be different. 

# How do JWT work
JSON Web Tokens are a way to authenticate a user through one login method and save a value in the browser that can be validated by new apps. 

To do this we wrap all flask methods in the `verify_session` function. This function sends your token to MyRadio to authenticate you. If all comes back clear it lets you through, if there are any problems it directs you to the MyRadio login page to grab a fresh token. 

# The MyRadio API
You can see some examples of how the MyRadio API can be intergrated into flask by taking a look at projects like [UniversityRadioYork/BaradDur](https://github.com/UniversityRadioYork/BaradDur/) or [UniversityRadioYork/Noticeboard-2](https://github.com/UniversityRadioYork/Noticeboard-2).

If you want to see a full spec of what the API can do you can see it at [ury.org.uk/api](https://ury.org.uk/api/). It's broken into chunks based on the object that the speciifc function manipulates. Beware of GET vs PUT vs POST when needed, and ensure you're encoding your parameters the correct way.

# Getting it Deployed
Ask someone to set this up... that what I've always done.

Okay okay fine if you want to try it yourself - here's what [Michael Grace](https://github.com/michael-grace) said to do.

You'll need to be able to SSH into `evergiven`; this is a server, if you don't have access pester the Head of Computing, if you are the HoC oh no... 

- SSH into evergiven
- git clone the project to your home directory
- note the `IMAGE_NAME` in the docker file and make sure your using an unused port
- build the image (`docker build -t everigven.ury.york.ac.uk:[port]/IMAGE_NAME`)
- Push the image to the registry (`docker push everigven.ury.york.ac.uk:[port]/IMAGE_NAME`)
- Go to `docker.ury.org.uk`, go into evergiven -> services -> add
- Add all the details in, including a port mapping (host just pick a big random number, container is probably `80` or whatever your app runs on)
- If you need to mount any files, make sure they're in `/dockervolumes`, which is copied between evergiven and steve, just so wherever it puts it, it'll be fine
- Go to `jenkins.ury.org.uk` and make a new freestyle project - make sure to click `limit where it can run` and put in the docker tag
- Link it to the github project
- In build steps, add a shell script thing, and copy it (essentially copy the entire setup) from one which works (like MyRadio), this is the docker build, docker push, docker service update steps.

And voila, it might work now! 
