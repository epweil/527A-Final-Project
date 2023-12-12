# 527A-Final-Project

This repo implements a ReAct agent, a debate tool, and self-consistency on the ALFWorld dataset.

This repo was used to generate results for our CSE 527A Final Project Paper.

Replicating the results in the paper is very simple, they are already defined for you in `main.py`.

Defining new experiments is also very simple. Please read the below sections to learn how to set up ALFWorld, connect to PaLM 2, and run the experiments!


## Running the experiments


1. Create an Anaconda environment and install everything in environment.yml
   - If you are in the root of this directory, simply run `conda env create -f environment.yml`, then `conda activate 527_debate_env`


2. To use PaLM 2 you will need to create a project on Google Cloud Platform (GCP). Copy the associated Project ID associated to it, as you'll need this to connect to PaLM 2.


3. Next, download the gcloud CLI https://cloud.google.com/sdk/docs/install. Keep the default options when running it for the first time. I believe this sets up Google cloud authentication automatically. But if you find out later it doesn't follow guides here https://cloud.google.com/vertex-ai/docs/workbench/reference/authentication to set up authentication. 


4. At this point you should be able to successfully connect to PaLM 2. However, if you use the PaLM tokenizer, you will need to request an increase in that limit. The category this falls under is "LlmUtilityAPIRequestPerMinutePerProjectPerRegion". If you don't want to do this you can just use the OpenAI tokenizer by uncommenting that part in the `tokens()` function in `utils.py`.


5. The final step is to set up and run the Docker container to run ALFWorld. Basically, the agent uses a tool to take actions in the environment. But because ALFWorld doesn't run on Windows, we have to run it in a Docker container and connect to it by wrapping it in an API.
   - Please follow the instructions in "Docker setup" to set up and run the container.

6. After the container is running, simply run `main.py` to generate the results! Read the "analyzing results" section below to know how to get the statistics from the saved results you just made.


## Creating new experiments

All of the parameters you can modify are already given in the experiments defined. Just copy and modify those to run what you want.


## Analyzing results

Results are stored in `./results/<timestamp>/results_<timestamp>.json` and log files are stored in `./results/<timestamp>/info_<timestamp>.log`.

To analyze these results, you just need to copy the timestamp (this is a field stored in the results themselves to make it easy to copy it).

The file `analysis.py` has functionality for getting statistics on a single results file or statistics on comparing two results. Please read the comments in that function. All you'll need to do is paste in the timestamp of the result and run the file.



## Docker setup

1. Install docker on your computer https://www.docker.com/get-started/ 

2. From your command line, navigate to the root of the repo (i.e., the same directory that Dockerfile is in)

3. Create the image: ```docker build -t 527_debate .``` ONLY DO THIS ONCE.

    a. ```-t 527_debate``` tags the image with the name 527_debate
    
    b. ```.``` means docker should look for a file called "Dockerfile" in the current directory

4. Create the container: ```docker run -it --name 527_debate_container -p 8000:8000 527_debate``` ONLY DO THIS ONCE.

    a. ```-it``` tells docker to connect to expose an interactive terminal from the container so we can interact with it via the command line

    b. ```--name 527_debate_container``` names the conatiner 527_debate_container.
    
    c. ```-p 8000:8000``` forwards port 8000 so that localhost:8000 on your computer connects to port 8000 within the docker container

    d. ```527_debate``` means the container is created off of the image named 527_debate which you created above

5. Stopping and starting the container. Once you have created the image, and used that to create the container (and run it), you might want to stop it, and then start it later on. Here is how to do that:

    a. In docker desktop, you can click the stop button for the container. Or I think you can hit CTRL-d

    a. To start the container (which is different from creating it), you can run ```docker start -ai 527_debate_container```

### Other notes

- There is a VSCode extension called "Dev Containers". It is really helpful. Once you install it, you can click on the bottom left of your screen (blue icon) to open a list of prompts. Then you can click on the prompt that says "Attach to Running Container". This will connect you to the container you select, and you can open files in VSCode and use the terminal and stuff. Helpful for development or debugging.

- I think the image is nearly 10GB in size

- It's easy to test the API in Postman. Make sure to set the url as `http://localhost:8000` (i.e., use http not https). Also make sure for the POST endpoints you are sending JSON in the body (i.e., select "raw" then "JSON" from the dropdown menu)


## Anaconda environment

In the project root, run `conda env create -f environment.yml`, then run `conda activate 527_debate_env`


## Simulator API

NOTE: the below documentation is slightly out of date, but I don't have time to update it right now. Basically some of the responses have extra fields, and there's also an endpoint you can use to reset the ALFWorld environment to start from the first task again.

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

