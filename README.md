# Item Catalog Project

This is the second project for us as a students of Udacity Full Stack Web Developer Nanodegree program.

## Introduction 

This project is a web application that implemented with Python based on Flask framework .
It uses SQLALchemy to perform CRUD operations.
It provides a third-party OAuth authentication.
It Implements RESTful APIs endpoints with JSON. 

## Project Description

The application is built with some data which provides a list of items within a variety of categories as well as provide a user authentication system. It allows users to sign in via their Google plus account. 
logged users will have the ability to post, edit and delete their own items.
Unlogged users can only view a list of items.

## Project Idea 

It is a platform that provides a list of wedding venues names, and by clicking on a specific wedding venue it'll display information related to that wedding venue as well as the name of the user who made the post associated with a picture of his/her Google Plus account at the top right.

## Dependencies

       - VirtualBox 
       - Vagrant 
       - Udacity Vagrantfile

## Installation

  1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 
  2. Install [Vagrant](https://www.vagrantup.com/downloads.html)
  3. Download [Udacity Vagrantfile](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)

## How to run the project:

  * Clone this repository inside the vagrant directory that you just downloaded by running: 
  git clone git://github.com/kalthommusa/Item_Catalog_Project2.git

## Start your machine   

  1. Navigate to cd vagrant
  3. Run vagrant up
  4. Run vagrant ssh
  5. Access the shared folder cd /vagrant
  6. Navigate to cd Item_Catalog_Project2
  
## Setup the database
 
  1. To create the database, run python database_setup.py
  2. To populate the database with some data(optional), run python populate_database.py  
  7. To start the application, run python project.py
  8. To access the application, open up the browser to http://localhost:5000

## JSON Endpoints

  -  /weddingvenues/JSON - lists all wedding venues in the app.

  - /weddingvenues/<int:weddingvenue_id>/items/JSON - lists specific wedding venue items.

  - /weddingvenues/<int:weddingvenue_id>/item/<int:item_id>/JSON - Lists specific wedding venue item.
