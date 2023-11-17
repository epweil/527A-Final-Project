# Use the existing "vzhong/alfworld" image as a base
FROM vzhong/alfworld

# Set the working directory to /opt
WORKDIR /opt

# Clone the ReAct repository into the /opt directory
RUN git clone https://github.com/ysymyth/ReAct.git

# Set environment variable
ENV ALFWORLD_ROOT /opt/alfworld/
ENV ALFWORLD_DATA /opt/alfworld/data/
ENV REACT_ROOT /opt/ReAct/

# Copy the local "simulator.py" file into the container's /opt/ directory
COPY simulator.py /opt/

# Run the simulator.py script when the container starts
CMD ["python", "/opt/simulator.py"]
