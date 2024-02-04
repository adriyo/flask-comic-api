##Comic Management API

A sample Flask and PostgreSQL project designed for learning how to create a simple CRUD API using python. This project will be integrated into another repository for the frontend, serving the purpose of managing comics uploaded by users.

##Packages
- **Flask**
- **Flask Restx**
- **PostgreSQL**
- **Flask Mail**

## Environment Configuration

Before running the project, make sure to set up your environment variables in the `.env` file as follows:

```env
POSTGRES_USER=root
POSTGRES_PASSWORD=root
POSTGRES_DB=root
POSTGRES_HOST_DB=db
PGADMIN_DEFAULT_EMAIL=admin@gmail.com
PGADMIN_DEFAULT_PASSWORD=admin
MAIL_USERNAME={{your email}}
MAIL_PASSWORD={{your password from mail service}}
MAIL_SERVER={{your mail server}}
MAIL_PORT={{your mail port}}
MAIL_USE_SSL={{true or false}}

```

## Environment Configuration
Use the following command to build and start the project:


```bash
docker compose up --build
```
## Swagger
Explore the API documentation using Swagger at [localhost:5000/docs](http://localhost:5000/docs)

**Note:**
This project is still experimental, and there may be changes in the future during development.
