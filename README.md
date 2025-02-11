# GitHub gist API


This is an example interface for GitHub API. Using this tool you will be able to view publicly available gists for a user.

This repository contains the Python API code and Docker file required to get the tool up and running.


## Building and Running a container

  1. Clone the GitHub repo:

      ```sh
      git clone https://github.com/drshott/gist-api.git
      ```
  
  2. Navigate inside the directory
    
     ```sh
     cd gist-api/app
     ```

  3. Run the following command to build the image:

      ```sh
      docker build -t <username>/<imagename> .
      ```
  
  4. Run the following command to start the containers:

      ```sh
      docker run -n gist-api -p 8080:8080 -itd <username>/<imagename>
      ```

## Use helm chart

Set nginx ingress for your kubernetes cluster if not done already.

```sh
helm install nginx-ingress ingress-nginx/ingress-nginx --set controller.publishService.enabled=true
```

Install the chart
     
```sh
cd gist-api/
helm install gist-api ./charts/gist-api
```

## Access API

You can now try the API endpoints

Swagger documentation

For docker image

```sh
curl -v http://localhost:8080/docs     
```
     
For helm
Add gistapi.localhost entry in your hosts file

```sh
curl -v https://gistapi.localhost/docs
```