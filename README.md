# Event Management System

A comprehensive Django REST Framework-based backend for managing events, users, and event participation.

## Overview

This Event Management System provides a robust API for creating and managing events with different user roles, authentication, and comprehensive logging. 
It follows the separation of concerns principle and implements best practices for Django and DRF.

## Features

### User Roles

- **Event Creator**:
  - Create and edit events
  - View the list of participants (only for their own events)
  - Manage event status and capacity
  - Delete events only if there are no participants

- **Regular User**:
  - View the list of open events
  - Join events (authentication required)
  - View their joined events
  - See event details (without access to the participant list)

- **Admin**:
  - Manage events and users
  - Modify event statuses
  - Monitor logs and metadata

### Authentication & Security

- JWT-based authentication
- Open events are publicly viewable (without authentication)
- Joining an event requires authentication
- Follows the Separation of Concerns principle in design

### Event Features

- Event name, description, capacity limit
- Date & location
- Event status (open, closed, canceled)
- Participant list (only visible to the creator)
- Metadata including timestamps, logs, and statuses

### Restrictions & Rules

- Users can only have a limited number of open events
- If the capacity limit is reached, new events cannot be created
- If an event has participants, it cannot be deleted
- Users can view the events they have joined

### Filters

- Filter by date
- Filter by event status
- Filter by remaining capacity

### Logging & Monitoring

- Track event modification history
- Log all system activities

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
