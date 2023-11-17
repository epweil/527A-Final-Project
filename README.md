# 527A-Final-Project

## TODOs

1. API

    - Make an endpoint to modify the MAX_STEPS. 

    - Maybe also return more information about what task number it is and step number (i.e., return total_resets and total_steps)

    - Test the API

        - edge cases, like calling /get_next_task more than 134 times
        
        - making sure you can't take more actions after completing the task or going over the max action limit

        -etc

2. Test debate

3. Test the other agent types (reflexion will be a lot of work, rest should be fairly straightforward)


## Docker setup

1. Install docker on your computer https://www.docker.com/get-started/ 

2. From your command line, navigate to the root of the repo (i.e., the same directory that Dockerfile is in)

3. Create the image: ```docker build -t 527_debate .```

    a. ```-t 527_debate``` tags the image with the name 527_debate
    
    b. ```.``` means docker should look for a file called "Dockerfile" in the current directory

4. Start the container: ```docker run -it -p 8000:8000 527_debate```

    a. ```-it``` tells docker to connect to expose an interactive terminal from the container so we can interact with it via the command line
    
    b. ```-p 8000:8000``` forwards port 8000 so that localhost:8000 on your computer connects to port 8000 within the docker container

    c. ```527_debate``` means the container is created off of the image named 527_debate which you created above

### Other notes

- There is a VSCode extension called "Dev Containers". It is really helpful. Once you install it, you can click on the bottom left of your screen (blue icon) to open a list of prompts. Then you can click on the prompt that says "Attach to Running Container". This will connect you to the container you select, and you can open files in VSCode and use the terminal and stuff. Helpful for development or debugging.

- I think the image is nearly 10GB in size

- It's easy to test the API in Postman. Make sure to set the url as `http://localhost:8000` (i.e., use http not https). Also make sure for the POST endpoints you are sending JSON in the body (i.e., select "raw" then "JSON" from the dropdown menu)


## Simulator API

The docker container runs the simulator API. The simulator API has some endpoints that allows anyone to interact with ALFWorld. 

### Endpoints:

**GET /get_next_task**

- This is a GET endpoint and doesn't take any parameters

- It returns a JSON object with keywords "prompt", "observation", and "prompt_and_observation"

    - "prompt" is a string containing 2 examples of how an agent can interact with ALFWorld

    - "observation" is a string containing the task description

    - "prompt_and_observation" is basically the concatenation of the above. This is the thing you should probably use.

**POST /take_action**

- This is a POST endpoint and takes a JSON object in the body with a single keyword "action" with value of a string the agent wants to take. For example, the body might look like 

    ```
    {
        "action": "go to drawer 1"
    }
    ```

- It returns a JSON object with keywords "observation", "reward", "done", "message"

    - "observation" is the observation as a result of the action

    - "reward" is True or False and indicates whether you completed the task

    - "done" is True or False and indicates whether the task is finished. Note, done is set to True if the agent completes the task or if the agent has exceeded the maximum allowed actions without completing the task

    - "message" this is usually None, except when you try to do something illegal. For example, if you try to take an action after exceeding the number of actions then the message will say that.


### Other notes

- There are 134 tasks. So if you call /get_next_task more than 134 times, it just wraps around to the first task again

## Agents