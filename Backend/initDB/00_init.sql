
-- Only save a Reference about the user, Use details from Key cloak.
-- We can add Properties should we need them & cant save that data in Keycloak later
-- TODO Maybe save a Public Key so we could add some encryption
create table Users (
    id serial primary key,
    sub text,
    username text
);

-- A Group has a associated Owner, Name and Description
-- TODO maybe add some form of a Tag System Later
create table Groups (
    id serial primary key,
    Owner int references Users(id),
    Name text,
    Description text
);

-- A group can have Multiple Members
-- TODO Maybe add a Reference for rights
create table GroupMembers (
    id serial primary key,
    "group" int references Groups(id),
    "user" int references Users(id)
);

-- A basic Message between two Users
-- Holds Send, receive and read Timestamps
-- For the Database it is irrelevant whether the msg is encrypted or not
-- TODO maybe add a Option to replay to a specific Msg
create table DirectMessages (
    id serial primary key,
    sender int references Users(id),
    receiver int references Users(id),
    msg text,
    sendTime timestamp,
    recTime timestamp,
    readTime timestamp
);

-- TODO Check how Group chats should work
-- one Group chat for a group, or could there be separate Chat groups
-- TODO I'm also uncertain how encryption would work for Group chats (the end to end kind (to the server everything is protected by SSL anyways))
-- TODO probably need a separate Table for Rec & read Times
create table GroupMessages (
    id serial primary key,
    sender int references Users(id),
    msg text,
    sendTime timestamp
);