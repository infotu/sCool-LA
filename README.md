# sCool Learning Analytics application

All of the following commands are for the initial version of the website, however they also apply to the new version, be aware that this is the name of the OLD docker image:

```
aniltilanthe/scool-la-app 
```

The NEW docker image is called:

```
infotu/scool-la-mz
```


(*) Run me 

```
docker run -p 8090:8090 *insert_image_name*
```
(*) Run me in detached mode with -d  
```
docker run -d -p 8090:8090 *insert_image_name*
```


(*) also further options try these  

```
#map localhost:8090 to the container 8090        -    127.0.0.1 is the localhost
docker run -d -p 127.0.0.1:8090:8090 *insert_image_name*
```


(*) also   

```
docker run -d -p 0.0.0.0:8090:8090 *insert_image_name*
```


OR

(*) -P Automatically publish all ports exposed by container and binds them to random port on the host machine
```
#1 Automatically publish all ports exposed by container and binds them to random port on the host machine
docker container run -P -d *insert_image_name*

#2.a Find the host machine port using container_uuid
docker container port *insert container_uuid*

#2.b Or using netstat
netstat -ntlp
```

check localhost

```
curl -I 0.0.0.0:8090

#or
curl -v 0.0.0.0:8090
```

Build me: 

```
docker build -t *insert_image_name* .
```

Clone me from docker hub :  

```
docker pull *insert_image_name*
```


Docker hub repo old:  

* aniltilanthe/scool-la-app

Docker gub repo new:

* infotu/scool-la-mz



sCool Data analysis and visualization


* Installation

```
pip install -r requirements.txt
```



* Set Up

  - Change the Database name (**DatabaseName**) in **constants.py**




* Login Redirect form

```
<!DOCTYPE html>
<html>
<head>
<title>Login Page</title>
</head>
<body>
<form action="http://codislabgraz.org:8090/login?securityStamp=<'securityStampString'>" method="post">
  <input type="submit" value="Click to Login" style="height: 300px;
    width: 300px;
    margin: 0;
    position: absolute;
    top: 50%;
    -ms-transform: translateY(-50%);
    transform: translateY(-50%);
    left: 40%;
	font-size: 30px;">
</form>
</body>
</html>
```



* To push and CI CD to Docker hub - push with tag
```
# lightweight
git tag v1.0.2

#  OR annotated   -  Annotated tags are stored as full objects in the Git database.
git tag -a v1.0.2   -m "my version 1.0.2"


git push origin v1.0.2
```
